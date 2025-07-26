# File: InitUserTestSpace.py
# Path: /home/herb/Desktop/AndyLibrary/InitUserTestSpace.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 10:35AM

"""
Initialize Clean User Test Environment
Sets up fresh test space with clean database and tracking files
"""

import os
import shutil
import tempfile
import sqlite3
import json
from pathlib import Path
from datetime import datetime

class UserTestEnvironment:
    """Create and manage clean test environment for user testing"""
    
    def __init__(self, test_name="user_test"):
        self.test_name = test_name
        self.project_root = Path(__file__).parent
        self.test_dir = Path(tempfile.mkdtemp(prefix=f"andylibrary_{test_name}_"))
        self.source_db = self.project_root / "Data" / "Databases" / "MyLibrary.db"
        
        print(f"🎯 INITIALIZING USER TEST ENVIRONMENT")
        print(f"📁 Test directory: {self.test_dir}")
        
    def clean_existing_data(self):
        """Clean out existing cache, logs, and temporary files"""
        print("\\n🧹 CLEANING EXISTING DATA...")
        
        # Areas to clean
        cleanup_paths = [
            self.project_root / "Data" / "Local" / "cached_library.db",
            self.project_root / "Data" / "Logs",
            self.project_root / "Config" / "google_token.json",
            "/tmp/andylibrary_*"
        ]
        
        for path in cleanup_paths:
            if "*" in str(path):
                # Handle glob patterns - but skip our current test directory
                import glob
                for match in glob.glob(str(path)):
                    if match == str(self.test_dir):
                        continue  # Don't clean our own test directory
                    try:
                        if os.path.isdir(match):
                            shutil.rmtree(match)
                        else:
                            os.unlink(match)
                        print(f"   ✅ Cleaned: {match}")
                    except Exception as e:
                        print(f"   ⚠️ Could not clean {match}: {e}")
            else:
                try:
                    if path.exists():
                        if path.is_dir():
                            shutil.rmtree(path)
                        else:
                            path.unlink()
                        print(f"   ✅ Cleaned: {path}")
                except Exception as e:
                    print(f"   ⚠️ Could not clean {path}: {e}")
        
        # Create fresh log directory
        log_dir = self.project_root / "Data" / "Logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created fresh log directory: {log_dir}")
    
    def setup_test_database(self):
        """Set up fresh test database"""
        print("\\n📊 SETTING UP TEST DATABASE...")
        
        if not self.source_db.exists():
            print(f"❌ Source database not found: {self.source_db}")
            return None
        
        # Copy database to test environment
        test_db_path = self.test_dir / "test_library.db"
        shutil.copy2(self.source_db, test_db_path)
        
        # Verify database
        conn = sqlite3.connect(test_db_path)
        book_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        category_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        
        # Get sample data
        sample_book = conn.execute("SELECT title, category_id FROM books LIMIT 1").fetchone()
        categories = conn.execute("SELECT id, category FROM categories LIMIT 5").fetchall()
        
        conn.close()
        
        file_size = test_db_path.stat().st_size
        
        print(f"   ✅ Database copied: {test_db_path}")
        print(f"   📚 Books: {book_count}")
        print(f"   📂 Categories: {category_count}")
        print(f"   💾 Size: {file_size / 1024 / 1024:.1f} MB")
        print(f"   📖 Sample: {sample_book[0] if sample_book else 'None'}")
        
        return test_db_path
    
    def setup_tracking_files(self):
        """Set up version tracking and analytics files"""
        print("\\n📋 SETTING UP TRACKING FILES...")
        
        # Version tracking file
        version_file = self.test_dir / "version.json"
        version_data = {
            "version": "0.0",
            "book_count": 0,
            "size_mb": 0,
            "last_check": datetime.now().isoformat(),
            "update_history": []
        }
        
        with open(version_file, 'w') as f:
            json.dump(version_data, f, indent=2)
        
        print(f"   ✅ Version tracking: {version_file}")
        
        # Analytics log file
        analytics_file = self.test_dir / "analytics.json"
        analytics_data = {
            "created": datetime.now().isoformat(),
            "test_environment": True,
            "entries": [],
            "stats": {
                "version_checks": 0,
                "downloads": 0,
                "data_saved_mb": 0
            }
        }
        
        with open(analytics_file, 'w') as f:
            json.dump(analytics_data, f, indent=2)
        
        print(f"   ✅ Analytics log: {analytics_file}")
        
        # User preferences file
        prefs_file = self.test_dir / "user_preferences.json"
        prefs_data = {
            "data_conscious_mode": True,
            "wifi_only_downloads": False,
            "auto_update_check": True,
            "cost_threshold_usd": 1.0,
            "preferred_categories": [],
            "usage_stats": {
                "sessions": 0,
                "books_accessed": 0,
                "search_queries": 0
            }
        }
        
        with open(prefs_file, 'w') as f:
            json.dump(prefs_data, f, indent=2)
        
        print(f"   ✅ User preferences: {prefs_file}")
        
        return {
            "version_file": version_file,
            "analytics_file": analytics_file,
            "preferences_file": prefs_file
        }
    
    def create_test_launcher(self, db_path, tracking_files):
        """Create launcher script for testing"""
        print("\\n🚀 CREATING TEST LAUNCHER...")
        
        launcher_script = f"""#!/usr/bin/env python3
# Generated Test Launcher - {datetime.now().isoformat()}

import os
import sys

# Test Environment Configuration
TEST_DB_PATH = "{db_path}"
VERSION_FILE = "{tracking_files['version_file']}"
ANALYTICS_FILE = "{tracking_files['analytics_file']}"
PREFERENCES_FILE = "{tracking_files['preferences_file']}"

print("🎯 ANDYLIBRARY USER TEST ENVIRONMENT")
print("=" * 50)
print(f"📁 Test database: {{TEST_DB_PATH}}")
print(f"📋 Version file: {{VERSION_FILE}}")
print(f"📊 Analytics file: {{ANALYTICS_FILE}}")
print(f"⚙️ Preferences: {{PREFERENCES_FILE}}")

# Set environment variables for the app
os.environ['ANDYGOOGLE_TEMP_DB'] = TEST_DB_PATH
os.environ['ANDYGOOGLE_MODE'] = 'local'
os.environ['ANDYGOOGLE_TEST_MODE'] = 'true'

print("\\n🌐 Starting test server...")
print("Access at: http://127.0.0.1:8090")

# Add project to path
sys.path.insert(0, '{self.project_root}')

# Import and start server
try:
    from Source.API.MainAPI import app
    import uvicorn
    
    uvicorn.run(app, host="127.0.0.1", port=8090, log_level="info")
except Exception as e:
    print(f"❌ Server failed to start: {{e}}")
    print("\\n🔧 MANUAL TESTING MODE")
    print("You can still test the database manually:")
    print(f"   Database: {{TEST_DB_PATH}}")
    print(f"   Use: sqlite3 {{TEST_DB_PATH}}")
"""
        
        launcher_path = self.test_dir / "launch_test.py"
        with open(launcher_path, 'w') as f:
            f.write(launcher_script)
        
        # Make executable
        os.chmod(launcher_path, 0o755)
        
        print(f"   ✅ Test launcher: {launcher_path}")
        
        return launcher_path
    
    def create_test_utilities(self):
        """Create utility scripts for testing"""
        print("\\n🛠️ CREATING TEST UTILITIES...")
        
        # Database inspector
        inspector_script = f"""#!/usr/bin/env python3
import sqlite3
import json

DB_PATH = "{self.test_dir}/test_library.db"

def inspect_database():
    print("🔍 DATABASE INSPECTION")
    print("=" * 30)
    
    conn = sqlite3.connect(DB_PATH)
    
    # Basic stats
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"📊 Tables: {{[t[0] for t in tables]}}")
    
    for table in ['books', 'categories', 'subjects']:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {{table}}").fetchone()[0]
            print(f"   {{table}}: {{count}} records")
        except:
            print(f"   {{table}}: not found")
    
    # Sample data
    print("\\n📚 Sample Books:")
    books = conn.execute("SELECT title, id FROM books LIMIT 5").fetchall()
    for book in books:
        print(f"   {{book[1]}}: {{book[0]}}")
    
    print("\\n📂 Categories:")
    cats = conn.execute("SELECT category, COUNT(*) as count FROM categories c JOIN books b ON c.id = b.category_id GROUP BY c.category LIMIT 5").fetchall()
    for cat in cats:
        print(f"   {{cat[0]}}: {{cat[1]}} books")
    
    conn.close()

if __name__ == "__main__":
    inspect_database()
"""
        
        inspector_path = self.test_dir / "inspect_db.py"
        with open(inspector_path, 'w') as f:
            f.write(inspector_script)
        os.chmod(inspector_path, 0o755)
        
        # Version tester
        version_tester = f"""#!/usr/bin/env python3
import requests
import json

def test_version_api():
    print("🔍 VERSION API TEST")
    print("=" * 25)
    
    try:
        # Test version check
        response = requests.get("http://127.0.0.1:8090/api/database/version", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Version API working")
            print(f"   Version: {{data['version']}}")
            print(f"   Size: {{data['size_mb']}}MB")
            print(f"   Books: {{data['book_count']}}")
        else:
            print(f"❌ Version API failed: {{response.status_code}}")
    
    except Exception as e:
        print(f"❌ Connection failed: {{e}}")
        print("Make sure the test server is running first")

if __name__ == "__main__":
    test_version_api()
"""
        
        version_test_path = self.test_dir / "test_version.py"
        with open(version_test_path, 'w') as f:
            f.write(version_tester)
        os.chmod(version_test_path, 0o755)
        
        print(f"   ✅ Database inspector: {inspector_path}")
        print(f"   ✅ Version API tester: {version_test_path}")
        
        return {
            "inspector": inspector_path,
            "version_tester": version_test_path
        }
    
    def display_test_instructions(self, launcher_path, utilities):
        """Display step-by-step testing instructions"""
        print("\\n" + "=" * 60)
        print("🎯 USER TEST ENVIRONMENT READY!")
        print("=" * 60)
        
        print(f"\\n📁 Test Directory: {self.test_dir}")
        print(f"🚀 Launcher: {launcher_path}")
        
        print(f"\\n📋 STEP-BY-STEP TESTING:")
        print(f"\\n1️⃣ INSPECT DATABASE (verify it's good)")
        print(f"   cd {self.test_dir}")
        print(f"   python inspect_db.py")
        
        print(f"\\n2️⃣ START TEST SERVER")
        print(f"   python launch_test.py")
        print(f"   # Opens on http://127.0.0.1:8090")
        
        print(f"\\n3️⃣ TEST VERSION API (in another terminal)")
        print(f"   cd {self.test_dir}")
        print(f"   python test_version.py")
        
        print(f"\\n4️⃣ TEST WEB INTERFACE")
        print(f"   Open: http://127.0.0.1:8090")
        print(f"   Try: Browse books, search, categories")
        
        print(f"\\n5️⃣ TEST DOWNLOAD WORKFLOW")
        print(f"   Visit: http://127.0.0.1:8090/api/database/version")
        print(f"   Try: http://127.0.0.1:8090/api/database/download")
        
        print(f"\\n6️⃣ VERIFY ANALYTICS")
        print(f"   Check: {self.test_dir}/analytics.json")
        print(f"   API: http://127.0.0.1:8090/api/analytics/data-usage")
        
        print(f"\\n🎯 SUCCESS CRITERIA:")
        print(f"   ✅ Database loads and shows correct book count")
        print(f"   ✅ Version API returns valid data (<1KB)")
        print(f"   ✅ Web interface displays books properly")
        print(f"   ✅ Download works and logs to analytics")
        print(f"   ✅ Search and filtering function correctly")
        
        print(f"\\n🧹 CLEANUP WHEN DONE:")
        print(f"   rm -rf {self.test_dir}")
        
        return True
    
    def run_complete_setup(self):
        """Run complete test environment setup"""
        try:
            # Step 1: Clean existing data
            self.clean_existing_data()
            
            # Step 2: Setup test database
            db_path = self.setup_test_database()
            if not db_path:
                return False
            
            # Step 3: Setup tracking files
            tracking_files = self.setup_tracking_files()
            
            # Step 4: Create launcher
            launcher_path = self.create_test_launcher(db_path, tracking_files)
            
            # Step 5: Create utilities
            utilities = self.create_test_utilities()
            
            # Step 6: Display instructions
            self.display_test_instructions(launcher_path, utilities)
            
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False

def main():
    """Initialize user test environment"""
    test_env = UserTestEnvironment("complete_workflow")
    success = test_env.run_complete_setup()
    
    if success:
        print(f"\\n🎉 Test environment ready!")
        print(f"🎯 Start testing with: cd {test_env.test_dir} && python launch_test.py")
    else:
        print(f"\\n❌ Setup failed!")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())