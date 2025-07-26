# File: CreateUserTestEnvironment.py
# Path: /home/herb/Desktop/AndyLibrary/Scripts/CreateUserTestEnvironment.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 01:24PM

"""
Clean User Test Environment Creator
Creates a realistic user environment for examination and testing
Simulates post-download user experience
"""

import os
import sys
import tempfile
import shutil
import sqlite3
from pathlib import Path

def CreateUserTestEnvironment():
    """Create clean user test environment"""
    
    print("🚀 Creating Clean User Test Environment")
    print("Simulating: Student who just downloaded database")
    print("=" * 60)
    
    # Create user environment directory
    user_env = tempfile.mkdtemp(prefix="andylibrary_user_test_")
    
    print(f"📁 User environment: {user_env}")
    
    try:
        # Create directory structure
        user_data_dir = os.path.join(user_env, "Data", "Local")
        user_config_dir = os.path.join(user_env, "Config")
        os.makedirs(user_data_dir, exist_ok=True)
        os.makedirs(user_config_dir, exist_ok=True)
        
        # Copy the proper cache database (with embedded thumbnails)
        source_cache = "Data/Local/cached_library.db"
        user_cache = os.path.join(user_data_dir, "cached_library.db")
        
        if not os.path.exists(source_cache):
            print("❌ Source cache database not found")
            return None
            
        shutil.copy2(source_cache, user_cache)
        
        # Verify database
        db_size_mb = os.path.getsize(user_cache) / (1024 * 1024)
        print(f"✅ Database copied: {db_size_mb:.1f}MB")
        
        # Test database content
        conn = sqlite3.connect(user_cache)
        conn.row_factory = sqlite3.Row
        
        try:
            # Get counts
            categories_count = conn.execute('SELECT COUNT(*) FROM categories').fetchone()[0]
            subjects_count = conn.execute('SELECT COUNT(*) FROM subjects').fetchone()[0]
            books_count = conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
            thumbnails_count = conn.execute('SELECT COUNT(*) FROM books WHERE thumbnail_image IS NOT NULL').fetchone()[0]
            
            print(f"📚 Books: {books_count}")
            print(f"📂 Categories: {categories_count}")
            print(f"🏷️ Subjects: {subjects_count}")
            print(f"🖼️ Thumbnails: {thumbnails_count}")
            
            # Test a few sample queries (typical user interactions)
            print("\n🧪 Testing User Interactions:")
            
            # Query 1: Get categories for dropdown
            categories = conn.execute('SELECT id, category FROM categories ORDER BY category LIMIT 5').fetchall()
            print(f"✅ Categories query: {len(categories)} results")
            
            # Query 2: Get books by category
            if categories:
                cat_id = categories[0]['id']
                books = conn.execute('SELECT COUNT(*) FROM books WHERE category_id = ?', (cat_id,)).fetchone()[0]
                print(f"✅ Books in '{categories[0]['category']}': {books}")
            
            # Query 3: Search books
            search_results = conn.execute("SELECT COUNT(*) FROM books WHERE title LIKE '%Python%'").fetchone()[0]
            print(f"✅ Python books search: {search_results} results")
            
            # Query 4: Get thumbnail
            thumbnail_test = conn.execute('SELECT title, LENGTH(thumbnail_image) FROM books WHERE thumbnail_image IS NOT NULL LIMIT 1').fetchone()
            if thumbnail_test:
                print(f"✅ Thumbnail test: '{thumbnail_test[0]}' has {thumbnail_test[1]} byte image")
            
        finally:
            conn.close()
        
        # Create simple config file
        config_file = os.path.join(user_config_dir, "andygoogle_config.json")
        config_content = """{
    "database": {
        "local_path": "Data/Local/cached_library.db",
        "version": "1.0.0"
    },
    "mode": "local",
    "last_update_check": null,
    "student_preferences": {
        "update_frequency": "quarterly",
        "show_cost_warnings": true,
        "offline_mode": true
    }
}"""
        
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        print(f"✅ Config created: {config_file}")
        
        # Create version info file (simulating what would be downloaded)
        version_file = os.path.join(user_data_dir, "version.json")
        version_content = """{
    "database_version": "1.0.0",
    "download_date": "2025-07-24",
    "size_mb": %.1f,
    "book_count": %d,
    "thumbnail_count": %d,
    "educational_mission": "active"
}""" % (db_size_mb, books_count, thumbnails_count)
        
        with open(version_file, 'w') as f:
            f.write(version_content)
        
        print(f"✅ Version info: {version_file}")
        
        # Create README for examination
        readme_file = os.path.join(user_env, "README.md")
        readme_content = f"""# User Test Environment

## Overview
This is a clean user test environment simulating a student who just downloaded the AndyLibrary database.

## Structure
```
{os.path.basename(user_env)}/
├── Data/Local/
│   ├── cached_library.db    ({db_size_mb:.1f}MB - with embedded thumbnails)
│   └── version.json         (download metadata)
├── Config/
│   └── andygoogle_config.json (user preferences)
└── README.md               (this file)
```

## Database Contents
- **Books**: {books_count:,}
- **Categories**: {categories_count}
- **Subjects**: {subjects_count}
- **Thumbnails**: {thumbnails_count:,} embedded as BLOBs

## Student Cost Analysis
- **One-time download**: ${db_size_mb * 0.10:.2f} (at $0.10/MB)
- **Storage impact**: {(db_size_mb / (8*1024)) * 100:.3f}% of 8GB tablet
- **Update frequency**: User choice (quarterly recommended)

## Testing Notes
- All thumbnails are embedded as BLOBs in the database
- No separate thumbnail files needed
- App should work entirely offline with this database
- Version control protects students from unnecessary downloads

## Examination Commands
```bash
# Connect to database
sqlite3 Data/Local/cached_library.db

# Sample queries
SELECT COUNT(*) FROM books;
SELECT category FROM categories;
SELECT title, LENGTH(thumbnail_image) FROM books WHERE thumbnail_image IS NOT NULL LIMIT 5;
```
"""
        
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        print(f"✅ README created: {readme_file}")
        
        print("\n" + "=" * 60)
        print("🎯 CLEAN USER TEST ENVIRONMENT READY")
        print(f"📁 Location: {user_env}")
        print(f"💾 Database: {db_size_mb:.1f}MB with {thumbnails_count:,} embedded thumbnails")
        print(f"🎓 Educational mission: Student cost ${db_size_mb * 0.10:.2f}")
        print("=" * 60)
        
        return user_env
        
    except Exception as e:
        print(f"❌ Error creating user environment: {e}")
        return None

if __name__ == "__main__":
    env_path = CreateUserTestEnvironment()
    if env_path:
        print(f"\n🔗 Ready for examination: {env_path}")
    else:
        print("❌ Failed to create user test environment")
        sys.exit(1)