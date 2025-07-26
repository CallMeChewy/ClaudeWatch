# File: TestVersionAPI.py
# Path: /home/herb/Desktop/AndyLibrary/TestVersionAPI.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 10:26AM

"""
Test the lightweight version API directly
"""

import sqlite3
import os
from pathlib import Path

def test_version_logic():
    """Test the version check logic directly"""
    print("🔍 TESTING VERSION CHECK LOGIC")
    print("=" * 40)
    
    # Use the real database
    project_root = Path(__file__).parent
    db_path = project_root / "Data" / "Local" / "cached_library.db"
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    try:
        # Get file stats (what the API does)
        file_size = os.path.getsize(db_path)
        file_mtime = int(os.path.getmtime(db_path))
        
        # Quick book count
        conn = sqlite3.connect(db_path)
        book_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        conn.close()
        
        # Create version string
        version = f"{file_mtime}.{book_count}"
        
        # Simulate API response
        api_response = {
            "version": version,
            "size_mb": round(file_size / 1024 / 1024, 1),
            "book_count": book_count,
            "available": True,
            "download_url": "/api/database/download"
        }
        
        print("📊 VERSION API RESPONSE:")
        print(f"   Version: {api_response['version']}")
        print(f"   Size: {api_response['size_mb']}MB")
        print(f"   Books: {api_response['book_count']}")
        print(f"   Available: {api_response['available']}")
        
        # Calculate response size
        import json
        response_json = json.dumps(api_response)
        response_size = len(response_json.encode('utf-8'))
        
        print(f"\\n📡 DATA USAGE:")
        print(f"   Response size: {response_size} bytes")
        print(f"   Cost estimate: ${response_size * 0.000001:.6f}")
        print(f"   ✅ Under 1KB limit: {response_size < 1024}")
        
        # Show version change scenarios
        print(f"\\n🔄 VERSION CHANGE SCENARIOS:")
        print(f"   Current: {version}")
        print(f"   New book added: {file_mtime}.{book_count + 1}")
        print(f"   Database updated: {file_mtime + 3600}.{book_count}")
        
        print(f"\\n💡 BENEFITS:")
        print(f"   ✅ Version check: {response_size} bytes")
        print(f"   ❌ Full download: {file_size:,} bytes")
        print(f"   💰 Savings: {(file_size - response_size) / file_size * 100:.1f}%")
        
        return api_response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_version_logic()