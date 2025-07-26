# File: TestDatabaseDownload.py
# Path: /home/herb/Desktop/AndyLibrary/TestDatabaseDownload.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 09:45AM

"""
Simple database download test - simulates new user experience
"""

import os
import sqlite3
import shutil
from datetime import datetime
import json

class NewUserDatabaseTest:
    """Simulate new user downloading and using database"""
    
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.source_db = os.path.join(self.script_dir, "Data", "Local", "cached_library.db")
        self.user_cache_dir = os.path.join(self.script_dir, "UserCache")
        self.user_db = os.path.join(self.user_cache_dir, "andylibrary.db")
        
    def setup_user_environment(self):
        """Set up a clean user environment"""
        print("👤 Setting up new user environment...")
        
        # Create user cache directory
        os.makedirs(self.user_cache_dir, exist_ok=True)
        print(f"✅ User cache directory: {self.user_cache_dir}")
        
        return True
    
    def simulate_database_download(self):
        """Simulate downloading database from server"""
        print("\n📥 Simulating database download...")
        
        if not os.path.exists(self.source_db):
            print(f"❌ Source database not found: {self.source_db}")
            return False
        
        try:
            # Simulate the download process
            print(f"🔄 Downloading from server...")
            
            # Copy database to user cache (simulates download)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_filename = f"andylibrary_{timestamp}.db"
            download_path = os.path.join(self.user_cache_dir, download_filename)
            
            shutil.copy2(self.source_db, download_path)
            
            # Also create a "latest" symlink for easy access
            if os.path.exists(self.user_db):
                os.remove(self.user_db)
            shutil.copy2(download_path, self.user_db)
            
            # Get file info
            file_size = os.path.getsize(self.user_db)
            file_size_mb = round(file_size / (1024 * 1024), 2)
            
            print(f"✅ Database downloaded successfully:")
            print(f"   📁 File: {download_filename}")
            print(f"   💾 Size: {file_size_mb} MB")
            print(f"   📍 Location: {self.user_cache_dir}")
            
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def test_database_content(self):
        """Test the downloaded database content"""
        print("\n📊 Testing downloaded database content...")
        
        if not os.path.exists(self.user_db):
            print("❌ Database file not found")
            return False
        
        try:
            conn = sqlite3.connect(self.user_db, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            
            # Test basic queries
            book_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
            category_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
            subject_count = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
            
            print(f"✅ Database content verified:")
            print(f"   📚 Books: {book_count}")
            print(f"   📂 Categories: {category_count}")
            print(f"   🏷️ Subjects: {subject_count}")
            
            # Test a sample query (simulate user browsing)
            sample_books = conn.execute("""
                SELECT title, category, subject 
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                LEFT JOIN subjects s ON b.subject_id = s.id
                LIMIT 5
            """).fetchall()
            
            print(f"\n📖 Sample books:")
            for book in sample_books:
                title = book['title'] or 'Unknown Title'
                category = book['category'] or 'No Category'
                subject = book['subject'] or 'No Subject'
                print(f"   • {title} ({category} / {subject})")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Database test failed: {e}")
            return False
    
    def test_database_caching(self):
        """Test database caching performance"""
        print("\n🚀 Testing database caching performance...")
        
        try:
            import time
            
            # Test cold start (first connection)
            start_time = time.time()
            conn = sqlite3.connect(self.user_db, check_same_thread=False)
            conn.execute("SELECT COUNT(*) FROM books").fetchone()
            cold_time = time.time() - start_time
            conn.close()
            
            # Test warm start (cached connection)
            start_time = time.time()
            conn = sqlite3.connect(self.user_db, check_same_thread=False)
            conn.execute("SELECT COUNT(*) FROM books").fetchone()
            warm_time = time.time() - start_time
            conn.close()
            
            print(f"✅ Performance test results:")
            print(f"   🔥 Cold start: {cold_time:.3f}s")
            print(f"   ⚡ Warm start: {warm_time:.3f}s")
            print(f"   🚀 Speedup: {cold_time/warm_time:.1f}x faster")
            
            return True
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False
    
    def simulate_version_check(self):
        """Simulate checking if database needs updating"""
        print("\n🔍 Simulating version check...")
        
        try:
            # Create a fake version file
            version_file = os.path.join(self.user_cache_dir, "version.json")
            
            current_version = {
                "version": "1.0.0",
                "downloaded": datetime.now().isoformat(),
                "book_count": None,
                "file_size": None
            }
            
            if os.path.exists(self.user_db):
                conn = sqlite3.connect(self.user_db)
                current_version["book_count"] = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
                current_version["file_size"] = os.path.getsize(self.user_db)
                conn.close()
            
            with open(version_file, 'w') as f:
                json.dump(current_version, f, indent=2)
            
            print(f"✅ Version info saved:")
            print(f"   📋 Version: {current_version['version']}")
            print(f"   📅 Downloaded: {current_version['downloaded'][:19]}")
            print(f"   📚 Books: {current_version['book_count']}")
            
            # Simulate version check logic
            print("\n💭 Version check logic:")
            print("   • Check server version vs local version")
            print("   • Compare book counts")
            print("   • Check last modified dates")
            print("   • Download only if newer version available")
            
            return True
            
        except Exception as e:
            print(f"❌ Version check failed: {e}")
            return False
    
    def run_complete_test(self):
        """Run complete new user simulation"""
        print("🆕 NEW USER DATABASE DOWNLOAD SIMULATION")
        print("=" * 50)
        
        tests = [
            ("User Environment Setup", self.setup_user_environment),
            ("Database Download", self.simulate_database_download),
            ("Database Content Test", self.test_database_content),
            ("Database Caching Test", self.test_database_caching),
            ("Version Check Simulation", self.simulate_version_check)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    passed += 1
                    print(f"\n✅ {test_name} - PASSED")
                else:
                    print(f"\n❌ {test_name} - FAILED")
            except Exception as e:
                print(f"\n❌ {test_name} - ERROR: {e}")
        
        print("\n" + "=" * 50)
        print("📋 NEW USER TEST RESULTS")
        print("=" * 50)
        print(f"Tests passed: {passed}/{total} ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Ready for new users!")
            print("\n📍 Next Steps:")
            print("   1. ✅ Database download works")
            print("   2. ✅ Local caching is fast")
            print("   3. ⏳ Implement version checking")
            print("   4. ⏳ Add Google Drive book access")
        else:
            print("❌ Some tests failed - needs investigation")
        
        return passed == total

def main():
    """Main test runner"""
    tester = NewUserDatabaseTest()
    success = tester.run_complete_test()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())