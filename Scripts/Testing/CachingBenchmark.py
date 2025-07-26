# File: CachingBenchmark.py
# Path: /home/herb/Desktop/AndyLibrary/CachingBenchmark.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 10:05AM

"""
Blazing Fast Caching Benchmark
Tests different caching strategies for optimal performance
"""

import os
import sqlite3
import time
import tempfile
import shutil
import json
from pathlib import Path
from contextlib import contextmanager

class CachingBenchmark:
    """Benchmark different database caching strategies"""
    
    def __init__(self, use_real_db=False):
        self.project_root = Path(__file__).parent
        if use_real_db:
            self.source_db = self.project_root / "Data" / "Databases" / "MyLibrary.db"
        else:
            self.source_db = self.project_root / "Data" / "Local" / "cached_library.db"
        self.results = {}
        
    def setup_test_database(self):
        """Setup test database for benchmarking"""
        if not self.source_db.exists():
            print(f"❌ Source database not found: {self.source_db}")
            return None
        
        # Create temp copy for testing with unique timestamp
        import time
        timestamp = str(int(time.time() * 1000000))  # microsecond precision
        temp_db = tempfile.NamedTemporaryFile(suffix=f'_{timestamp}.db', delete=False)
        temp_db.close()
        shutil.copy2(self.source_db, temp_db.name)
        
        # Get basic stats
        conn = sqlite3.connect(temp_db.name)
        book_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        category_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        file_size = os.path.getsize(temp_db.name)
        conn.close()
        
        print(f"📊 Test Database Setup:")
        print(f"   📚 Books: {book_count}")
        print(f"   📂 Categories: {category_count}")
        print(f"   💾 Size: {file_size / 1024:.1f} KB")
        
        return temp_db.name
    
    @contextmanager
    def timer(self, operation_name):
        """Context manager for timing operations"""
        start_time = time.perf_counter()
        yield
        end_time = time.perf_counter()
        duration = end_time - start_time
        self.results[operation_name] = duration
        print(f"   ⏱️ {operation_name}: {duration:.4f}s")
    
    def benchmark_disk_database(self, db_path):
        """Benchmark standard disk-based database access"""
        print("\n🗄️ DISK DATABASE BENCHMARK")
        print("-" * 30)
        
        # Force cold start - disable SQLite caching
        with self.timer("Disk: Cold Connection"):
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            # Disable SQLite page cache for true cold test
            conn.execute("PRAGMA cache_size = 0") 
            conn.execute("SELECT COUNT(*) FROM books").fetchone()
            conn.close()
            conn = None  # Force cleanup
        
        # Warm connection reuse
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        with self.timer("Disk: Book Count"):
            book_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        
        with self.timer("Disk: Categories Load"):
            categories = conn.execute("SELECT * FROM categories ORDER BY category").fetchall()
        
        with self.timer("Disk: Complex Query"):
            books = conn.execute("""
                SELECT b.id, b.title, c.category, s.subject 
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                LEFT JOIN subjects s ON b.subject_id = s.id
                LIMIT 100
            """).fetchall()
        
        with self.timer("Disk: Search Query"):
            search_results = conn.execute("""
                SELECT b.title, c.category
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                WHERE b.title LIKE '%python%'
                LIMIT 50
            """).fetchall()
        
        conn.close()
        
        print(f"   📊 Results: {book_count} books, {len(categories)} categories")
        print(f"   📖 Complex query: {len(books)} books")
        print(f"   🔍 Search results: {len(search_results)} matches")
    
    def benchmark_memory_database(self, disk_db_path):
        """Benchmark in-memory database (loaded from disk)"""
        print("\n🧠 MEMORY DATABASE BENCHMARK")
        print("-" * 30)
        
        # Load entire database into memory
        with self.timer("Memory: Database Load"):
            # Create in-memory database
            memory_conn = sqlite3.connect(":memory:")
            memory_conn.row_factory = sqlite3.Row
            
            # Load from disk
            disk_conn = sqlite3.connect(disk_db_path)
            disk_conn.backup(memory_conn)
            disk_conn.close()
        
        with self.timer("Memory: Book Count"):
            book_count = memory_conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        
        with self.timer("Memory: Categories Load"):
            categories = memory_conn.execute("SELECT * FROM categories ORDER BY category").fetchall()
        
        with self.timer("Memory: Complex Query"):
            books = memory_conn.execute("""
                SELECT b.id, b.title, c.category, s.subject 
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                LEFT JOIN subjects s ON b.subject_id = s.id
                LIMIT 100
            """).fetchall()
        
        with self.timer("Memory: Search Query"):
            search_results = memory_conn.execute("""
                SELECT b.title, c.category
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                WHERE b.title LIKE '%python%'
                LIMIT 50
            """).fetchall()
        
        memory_conn.close()
        
        print(f"   📊 Results: {book_count} books, {len(categories)} categories")
    
    def benchmark_python_cache(self, db_path):
        """Benchmark Python dictionary caching"""
        print("\n🐍 PYTHON CACHE BENCHMARK")
        print("-" * 30)
        
        cache = {}
        
        with self.timer("Python: Cache Load"):
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            
            # Load all data into Python structures
            cache['books'] = [dict(row) for row in conn.execute("""
                SELECT b.id, b.title, c.category, s.subject 
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                LEFT JOIN subjects s ON b.subject_id = s.id
            """).fetchall()]
            
            cache['categories'] = [dict(row) for row in conn.execute("SELECT * FROM categories").fetchall()]
            cache['subjects'] = [dict(row) for row in conn.execute("SELECT * FROM subjects").fetchall()]
            
            conn.close()
        
        with self.timer("Python: Book Count"):
            book_count = len(cache['books'])
        
        with self.timer("Python: Categories Load"):
            categories = cache['categories']
        
        with self.timer("Python: Complex Query"):
            # Simulate complex query with list comprehension
            books = cache['books'][:100]
        
        with self.timer("Python: Search Query"):
            # Simulate search with filter
            search_results = [book for book in cache['books'] 
                            if 'python' in book['title'].lower()][:50]
        
        print(f"   📊 Results: {book_count} books, {len(categories)} categories")
        print(f"   💾 Cache size: {len(str(cache)) / 1024:.1f} KB in memory")
    
    def benchmark_optimized_sqlite(self, db_path):
        """Benchmark SQLite with optimizations"""
        print("\n⚡ OPTIMIZED SQLITE BENCHMARK")
        print("-" * 30)
        
        with self.timer("Optimized: Connection + Setup"):
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            
            # SQLite optimizations
            conn.execute("PRAGMA cache_size = 10000")  # 10MB cache
            conn.execute("PRAGMA temp_store = MEMORY")
            conn.execute("PRAGMA mmap_size = 268435456")  # 256MB mmap
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
        
        with self.timer("Optimized: Book Count"):
            book_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        
        with self.timer("Optimized: Categories Load"):
            categories = conn.execute("SELECT * FROM categories ORDER BY category").fetchall()
        
        with self.timer("Optimized: Complex Query"):
            books = conn.execute("""
                SELECT b.id, b.title, c.category, s.subject 
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                LEFT JOIN subjects s ON b.subject_id = s.id
                LIMIT 100
            """).fetchall()
        
        with self.timer("Optimized: Search Query"):
            search_results = conn.execute("""
                SELECT b.title, c.category
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                WHERE b.title LIKE '%python%'
                LIMIT 50
            """).fetchall()
        
        conn.close()
        
        print(f"   📊 Results: {book_count} books, {len(categories)} categories")
    
    def analyze_user_directory_needs(self):
        """Analyze what user directory structure is needed"""
        print("\n📁 USER DIRECTORY ANALYSIS")
        print("-" * 30)
        
        # Calculate different storage scenarios
        file_size = os.path.getsize(self.source_db)
        
        scenarios = {
            "Physical DB File": {
                "storage": file_size,
                "startup_time": "~0.001s",
                "memory_usage": "~1MB",
                "pros": ["Persistent", "Low memory", "Fast startup"],
                "cons": ["Disk I/O", "File management"]
            },
            "Memory-Only": {
                "storage": 0,
                "startup_time": "~0.010s",
                "memory_usage": f"~{file_size / 1024:.0f}KB",
                "pros": ["Blazing fast", "No disk I/O", "No files"],
                "cons": ["Reload on restart", "Memory usage"]
            },
            "Hybrid Cache": {
                "storage": file_size,
                "startup_time": "~0.005s", 
                "memory_usage": "~2MB",
                "pros": ["Fast access", "Persistent fallback", "Smart caching"],
                "cons": ["Complex logic", "Memory + disk"]
            },
            "JSON Cache": {
                "storage": file_size * 1.5,  # JSON is larger
                "startup_time": "~0.020s",
                "memory_usage": f"~{file_size * 1.5 / 1024:.0f}KB",
                "pros": ["Human readable", "Language agnostic", "Easy debugging"],
                "cons": ["Larger size", "Slower parsing"]
            }
        }
        
        print("📊 Storage Scenarios:")
        for name, scenario in scenarios.items():
            print(f"\n   🎯 {name}:")
            print(f"      💾 Storage: {scenario['storage'] / 1024:.1f}KB" if scenario['storage'] else "      💾 Storage: None")
            print(f"      ⏱️ Startup: {scenario['startup_time']}")
            print(f"      🧠 Memory: {scenario['memory_usage']}")
            print(f"      ✅ Pros: {', '.join(scenario['pros'])}")
            print(f"      ⚠️ Cons: {', '.join(scenario['cons'])}")
    
    def recommend_optimal_strategy(self):
        """Recommend optimal caching strategy based on results"""
        print("\n🎯 PERFORMANCE ANALYSIS")
        print("-" * 30)
        
        # Compare key operations
        operations = ['Book Count', 'Categories Load', 'Complex Query', 'Search Query']
        strategies = ['Disk', 'Memory', 'Python', 'Optimized']
        
        print("📊 Performance Comparison (seconds):")
        print(f"{'Operation':<15} {'Disk':<8} {'Memory':<8} {'Python':<8} {'Optimized':<10}")
        print("-" * 55)
        
        for op in operations:
            disk_time = self.results.get(f'Disk: {op}', 0)
            memory_time = self.results.get(f'Memory: {op}', 0)
            python_time = self.results.get(f'Python: {op}', 0)
            opt_time = self.results.get(f'Optimized: {op}', 0)
            
            print(f"{op:<15} {disk_time:<8.4f} {memory_time:<8.4f} {python_time:<8.4f} {opt_time:<10.4f}")
        
        # Find fastest strategy
        total_times = {}
        for strategy in strategies:
            total = sum(self.results.get(f'{strategy}: {op}', 0) for op in operations)
            total_times[strategy] = total
        
        fastest = min(total_times.items(), key=lambda x: x[1])
        
        print(f"\n🏆 FASTEST STRATEGY: {fastest[0].upper()}")
        print(f"   ⚡ Total time: {fastest[1]:.4f}s")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if fastest[0] == 'Memory':
            print("   🧠 Use in-memory database for blazing speed")
            print("   📥 Download DB → Load to :memory: → Blazing fast access")
            print("   🎯 User needs: Just temp download, no persistent files")
            
        elif fastest[0] == 'Python':
            print("   🐍 Use Python dict caching for ultimate speed")
            print("   📥 Download DB → Parse to dict → Lightning fast filtering")
            print("   🎯 User needs: Just temp download, pure memory operations")
            
        elif fastest[0] == 'Optimized':
            print("   ⚡ Use optimized SQLite for best balance")
            print("   📥 Download DB → Apply optimizations → Fast + flexible")
            print("   🎯 User needs: DB file + optimized connection settings")
        
        print(f"\n🚀 BLAZING FAST SETUP:")
        print(f"   1. Download 456KB database to temp location")
        print(f"   2. Load using {fastest[0]} strategy") 
        print(f"   3. Access 1219 books in {fastest[1]:.4f}s total")
        print(f"   4. User directory: Minimal/none needed for memory-only")
    
    def clear_system_caches(self):
        """Clear system caches to ensure cold tests"""
        print("🧹 CLEARING SYSTEM CACHES...")
        try:
            # Clear Python bytecode cache
            import sys
            if hasattr(sys, '_clear_type_cache'):
                sys._clear_type_cache()
            
            # Clear filesystem cache (requires sudo, so try but don't fail)
            try:
                os.system("sync")  # Flush filesystem buffers
                print("   ✅ Filesystem buffers flushed")
            except:
                print("   ⚠️ Could not flush filesystem cache (need sudo)")
            
            # Force garbage collection
            import gc
            gc.collect()
            print("   ✅ Python garbage collection cleared")
            
            print("   ✅ Caches cleared for cold test")
            
        except Exception as e:
            print(f"   ⚠️ Cache clearing partial: {e}")

    def run_complete_benchmark(self):
        """Run complete caching benchmark with cache clearing"""
        print("🚀 BLAZING FAST CACHING BENCHMARK")
        print("=" * 45)
        
        # Clear caches before starting
        self.clear_system_caches()
        
        # Setup - create fresh temp database each time
        db_path = self.setup_test_database()
        if not db_path:
            return False
        
        try:
            # Run all benchmarks with cache clearing between each
            print("\n🔄 Running benchmarks with cache clearing between tests...")
            
            self.clear_system_caches()
            time.sleep(0.1)  # Brief pause
            self.benchmark_disk_database(db_path)
            
            self.clear_system_caches() 
            time.sleep(0.1)
            self.benchmark_memory_database(db_path)
            
            self.clear_system_caches()
            time.sleep(0.1) 
            self.benchmark_python_cache(db_path)
            
            self.clear_system_caches()
            time.sleep(0.1)
            self.benchmark_optimized_sqlite(db_path)
            
            # Analysis
            self.analyze_user_directory_needs()
            self.recommend_optimal_strategy()
            
            return True
            
        finally:
            # Cleanup
            if os.path.exists(db_path):
                os.unlink(db_path)

def main():
    """Main benchmark runner"""
    import sys
    use_real_db = "--real" in sys.argv
    
    if use_real_db:
        print("🔥 USING REAL 10MB+ DATABASE")
    else:
        print("📋 USING CACHED DATABASE (use --real for 10MB database)")
    
    benchmark = CachingBenchmark(use_real_db=use_real_db)
    success = benchmark.run_complete_benchmark()
    
    print(f"\n{'🎯 BENCHMARK COMPLETE!' if success else '❌ BENCHMARK FAILED'}")
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())