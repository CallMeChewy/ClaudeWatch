# File: SmartUpdateClient.py
# Path: /home/herb/Desktop/AndyLibrary/SmartUpdateClient.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 10:25AM

"""
Smart Update Client - Version-controlled database updates
Protects users from unnecessary data charges while ensuring fresh content
"""

import os
import json
import requests
import tempfile
import shutil
from pathlib import Path

class SmartUpdateClient:
    """Client-side version control for database updates"""
    
    def __init__(self, server_url="http://127.0.0.1:8081", local_db_dir=None):
        self.server_url = server_url.rstrip('/')
        self.local_db_dir = local_db_dir or tempfile.mkdtemp(prefix="andylibrary_")
        self.version_file = os.path.join(self.local_db_dir, "version.json")
        self.db_file = os.path.join(self.local_db_dir, "library.db")
        
        # Ensure directory exists
        os.makedirs(self.local_db_dir, exist_ok=True)
        
    def get_local_version(self):
        """Get locally stored version info"""
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"version": "0.0", "book_count": 0, "size_mb": 0}
    
    def save_local_version(self, version_info):
        """Save version info locally"""
        with open(self.version_file, 'w') as f:
            json.dump(version_info, f, indent=2)
    
    def check_for_updates(self):
        """Lightweight check for database updates (< 1KB data usage)"""
        print("🔍 Checking for database updates...")
        
        try:
            # Lightweight version check
            response = requests.get(f"{self.server_url}/api/database/version", timeout=10)
            if response.status_code != 200:
                print(f"❌ Version check failed: {response.status_code}")
                return None
            
            server_version = response.json()
            local_version = self.get_local_version()
            
            print(f"📊 Version comparison:")
            print(f"   Local:  {local_version['version']} ({local_version['book_count']} books)")
            print(f"   Server: {server_version['version']} ({server_version['book_count']} books)")
            
            # Check if update needed
            if server_version['version'] != local_version['version']:
                size_mb = server_version['size_mb']
                book_diff = server_version['book_count'] - local_version['book_count']
                
                print(f"🆕 Update available!")
                print(f"   📥 Download size: {size_mb}MB")
                print(f"   📚 New books: +{book_diff}")
                
                return {
                    'update_available': True,
                    'server_version': server_version,
                    'local_version': local_version,
                    'size_mb': size_mb,
                    'new_books': book_diff
                }
            else:
                print("✅ Database is up to date")
                return {
                    'update_available': False,
                    'server_version': server_version,
                    'local_version': local_version
                }
                
        except Exception as e:
            print(f"❌ Update check failed: {e}")
            return None
    
    def download_update(self, force=False):
        """Download database update if needed"""
        update_info = self.check_for_updates()
        
        if not update_info:
            print("❌ Cannot check for updates")
            return False
        
        if not update_info['update_available'] and not force:
            print("✅ No update needed")
            return True
        
        server_version = update_info['server_version']
        size_mb = server_version['size_mb']
        
        # User confirmation for data usage
        print(f"⚠️ DOWNLOAD CONFIRMATION")
        print(f"   📥 Size: {size_mb}MB")
        print(f"   📚 Books: {server_version['book_count']}")
        print(f"   💰 Data cost: ~${size_mb * 0.10:.2f} (estimated)")
        
        if not force:
            confirm = input("   Continue download? (y/N): ").lower().strip()
            if confirm not in ['y', 'yes']:
                print("❌ Download cancelled by user")
                return False
        
        print(f"📥 Downloading database ({size_mb}MB)...")
        
        try:
            # Download with progress
            response = requests.get(f"{self.server_url}/api/database/download", 
                                  stream=True, timeout=300)
            
            if response.status_code != 200:
                print(f"❌ Download failed: {response.status_code}")
                return False
            
            # Save to temporary file first
            temp_db = self.db_file + ".tmp"
            downloaded = 0
            total_size = int(response.headers.get('content-length', 0))
            
            with open(temp_db, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Simple progress indicator
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Every MB
                                print(f"   📥 Progress: {progress:.0f}%")
            
            # Verify download
            if os.path.getsize(temp_db) < 100000:  # Less than 100KB is suspicious
                print("❌ Download appears incomplete")
                os.unlink(temp_db)
                return False
            
            # Move to final location
            if os.path.exists(self.db_file):
                os.unlink(self.db_file)
            shutil.move(temp_db, self.db_file)
            
            # Save version info
            self.save_local_version(server_version)
            
            actual_size = os.path.getsize(self.db_file) / 1024 / 1024
            print(f"✅ Download complete: {actual_size:.1f}MB")
            print(f"📁 Database saved: {self.db_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def get_local_database_path(self):
        """Get path to local database file"""
        if os.path.exists(self.db_file):
            return self.db_file
        return None
    
    def get_data_usage_stats(self):
        """Get data usage statistics"""
        local_version = self.get_local_version()
        
        return {
            "current_database_mb": local_version.get('size_mb', 0),
            "estimated_monthly_usage_mb": local_version.get('size_mb', 0) * 4,  # 4 updates/month estimate
            "estimated_cost_usd": local_version.get('size_mb', 0) * 4 * 0.10  # $0.10/MB estimate
        }

def demo_smart_updates():
    """Demonstrate smart update system"""
    print("🎯 SMART UPDATE SYSTEM DEMO")
    print("=" * 50)
    
    # Initialize client
    client = SmartUpdateClient(server_url="http://127.0.0.1:8081")
    
    print(f"📁 Local database directory: {client.local_db_dir}")
    
    # Check for updates
    update_info = client.check_for_updates()
    
    if update_info and update_info['update_available']:
        print("\\n🎯 UPDATE RECOMMENDED")
        print("   This system protects users from unnecessary data charges")
        print("   Only downloads when new content is available")
        
        # Show data usage projection
        stats = client.get_data_usage_stats()
        print(f"\\n💰 DATA USAGE PROJECTION:")
        print(f"   Current DB: {stats['current_database_mb']}MB")
        print(f"   Monthly estimate: {stats['estimated_monthly_usage_mb']}MB")
        print(f"   Estimated cost: ${stats['estimated_cost_usd']:.2f}/month")
        
        # Download (with user confirmation)
        success = client.download_update()
        
        if success:
            db_path = client.get_local_database_path()
            print(f"\\n✅ Ready to use: {db_path}")
    
    else:
        print("\\n✅ Database is current - no data usage required")

if __name__ == "__main__":
    demo_smart_updates()