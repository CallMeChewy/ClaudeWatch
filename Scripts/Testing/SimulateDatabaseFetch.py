# File: SimulateDatabaseFetch.py
# Path: /home/herb/Desktop/AndyLibrary/SimulateDatabaseFetch.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 09:50AM

"""
Simulate database fetch and setup for use
Simple test to download DB to temp location and launch app to use it
"""

import os
import shutil
import tempfile
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

class DatabaseFetchSimulator:
    """Simulate fetching database and setting up app to use it"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.source_db = self.project_root / "Data" / "Local" / "cached_library.db"
        self.temp_dir = None
        self.temp_db_path = None
        
    def simulate_database_fetch(self):
        """Simulate downloading database to temp location"""
        print("📥 Simulating database fetch...")
        
        # Create temp directory
        self.temp_dir = tempfile.mkdtemp(prefix="andylibrary_")
        self.temp_db_path = os.path.join(self.temp_dir, "fetched_library.db")
        
        print(f"📁 Temp location: {self.temp_dir}")
        
        # Check source database exists
        if not self.source_db.exists():
            print(f"❌ Source database not found: {self.source_db}")
            return False
        
        try:
            # Simulate the fetch (copy to temp location)
            print("🔄 Fetching database...")
            shutil.copy2(self.source_db, self.temp_db_path)
            
            # Verify the fetched database
            file_size = os.path.getsize(self.temp_db_path)
            print(f"✅ Database fetched successfully")
            print(f"   📍 Location: {self.temp_db_path}")
            print(f"   💾 Size: {file_size / 1024:.1f} KB")
            
            return True
            
        except Exception as e:
            print(f"❌ Fetch failed: {e}")
            return False
    
    def verify_database_content(self):
        """Quick verification that fetched database is usable"""
        print("\n📊 Verifying fetched database content...")
        
        try:
            conn = sqlite3.connect(self.temp_db_path)
            
            # Basic content check
            book_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
            category_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
            
            print(f"✅ Database content verified:")
            print(f"   📚 {book_count} books")
            print(f"   📂 {category_count} categories")
            
            # Test a simple query
            sample = conn.execute("SELECT title FROM books LIMIT 1").fetchone()
            if sample:
                print(f"   📖 Sample book: {sample[0]}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
            return False
    
    def create_temp_config(self):
        """Create temporary config pointing to fetched database"""
        print("\n⚙️ Creating temporary config...")
        
        try:
            # Create a minimal config that points to our temp database
            temp_config = {
                "database": {
                    "local_path": self.temp_db_path,
                    "use_temp_location": True
                },
                "server_port": 8090,  # Use different port for testing
                "mode": "local"
            }
            
            self.temp_config_path = os.path.join(self.temp_dir, "temp_config.json")
            
            import json
            with open(self.temp_config_path, 'w') as f:
                json.dump(temp_config, f, indent=2)
            
            print(f"✅ Config created: {self.temp_config_path}")
            print(f"   🎯 Database path: {self.temp_db_path}")
            print(f"   🌐 Port: 8090")
            
            return True
            
        except Exception as e:
            print(f"❌ Config creation failed: {e}")
            return False
    
    def launch_app_with_temp_database(self):
        """Launch the app configured to use the fetched database"""
        print("\n🚀 Launching app with fetched database...")
        
        try:
            # Create a simple launcher script that uses our temp database
            launcher_script = f"""
import os
import sys

# Add project to path
sys.path.insert(0, '{self.project_root}')

# Set environment to use our temp database
os.environ['ANDYGOOGLE_TEMP_DB'] = '{self.temp_db_path}'
os.environ['ANDYGOOGLE_MODE'] = 'local'

# Import and start server
from Source.API.MainAPI import app
import uvicorn

print("🔍 Using temp database: {self.temp_db_path}")
print("🌐 Starting server on port 8090...")

uvicorn.run(app, host="127.0.0.1", port=8090, log_level="warning")
"""
            
            launcher_path = os.path.join(self.temp_dir, "launch_temp_app.py")
            with open(launcher_path, 'w') as f:
                f.write(launcher_script)
            
            print(f"✅ Launcher created: {launcher_path}")
            print("🌐 App should start on: http://127.0.0.1:8090")
            print("\n▶️ Ready to launch! Run:")
            print(f"   python {launcher_path}")
            
            return launcher_path
            
        except Exception as e:
            print(f"❌ Launcher creation failed: {e}")
            return None
    
    def test_app_connectivity(self, launcher_path):
        """Test that the app can be launched and responds"""
        print("\n🧪 Testing app connectivity...")
        
        try:
            # Launch app in background
            print("⏳ Starting app (5 second test)...")
            
            # Set environment variables for the subprocess
            env = os.environ.copy()
            env['ANDYGOOGLE_TEMP_DB'] = self.temp_db_path
            env['ANDYGOOGLE_MODE'] = 'local'
            
            process = subprocess.Popen([
                sys.executable, launcher_path
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Give it time to start
            time.sleep(3)
            
            # Quick test if it's responding
            try:
                import requests
                response = requests.get("http://127.0.0.1:8090/api/health", timeout=2)
                if response.status_code == 200:
                    print("✅ App launched successfully!")
                    print("✅ Health check passed")
                    
                    # Quick database test
                    stats_response = requests.get("http://127.0.0.1:8090/api/stats", timeout=2)
                    if stats_response.status_code == 200:
                        stats = stats_response.json()
                        print(f"✅ Database working: {stats.get('total_books')} books")
                    
                    success = True
                else:
                    print(f"⚠️ App responded with status: {response.status_code}")
                    success = False
                    
            except Exception as e:
                print(f"⚠️ Connectivity test failed: {e}")
                success = False
            
            # Clean up process
            process.terminate()
            process.wait(timeout=2)
            
            return success
            
        except Exception as e:
            print(f"❌ App test failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print(f"🧹 Cleaned up temp directory: {self.temp_dir}")
            except Exception as e:
                print(f"⚠️ Cleanup warning: {e}")
    
    def run_simulation(self):
        """Run complete database fetch simulation"""
        print("🎯 DATABASE FETCH & SETUP SIMULATION")
        print("=" * 45)
        
        try:
            # Step 1: Simulate database fetch
            if not self.simulate_database_fetch():
                return False
            
            # Step 2: Verify database
            if not self.verify_database_content():
                return False
            
            # Step 3: Create launcher
            launcher_path = self.launch_app_with_temp_database()
            if not launcher_path:
                return False
            
            # Step 4: Test connectivity (optional)
            print("\n❓ Test app connectivity? (y/N):", end=" ")
            test_choice = input().strip().lower()
            
            if test_choice == 'y':
                connectivity_ok = self.test_app_connectivity(launcher_path)
            else:
                connectivity_ok = True
                print("⏭️ Skipping connectivity test")
            
            print("\n" + "=" * 45)
            print("📋 SIMULATION RESULTS")
            print("=" * 45)
            print("✅ Database fetch: SUCCESS")
            print("✅ Database verification: SUCCESS")
            print("✅ App launcher: SUCCESS")
            
            if test_choice == 'y':
                print(f"{'✅' if connectivity_ok else '⚠️'} Connectivity test: {'SUCCESS' if connectivity_ok else 'PARTIAL'}")
            
            print(f"\n🎯 READY TO USE:")
            print(f"   📁 Database: {self.temp_db_path}")
            print(f"   🚀 Launcher: {launcher_path}")
            print(f"   🌐 URL: http://127.0.0.1:8090")
            
            print(f"\n▶️ To launch app:")
            print(f"   python {launcher_path}")
            
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️ Simulation interrupted")
            return False
        except Exception as e:
            print(f"\n❌ Simulation failed: {e}")
            return False
        finally:
            # Ask about cleanup
            print(f"\n🧹 Clean up temp files? (Y/n):", end=" ")
            cleanup_choice = input().strip().lower()
            if cleanup_choice != 'n':
                self.cleanup()
            else:
                print(f"📁 Temp files kept at: {self.temp_dir}")

def main():
    """Main simulation runner"""
    simulator = DatabaseFetchSimulator()
    
    try:
        success = simulator.run_simulation()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n👋 Simulation cancelled")
        simulator.cleanup()
        return 1

if __name__ == "__main__":
    exit(main())