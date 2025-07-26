# File: TestGoogleDriveWorkflow.py
# Path: /home/herb/Desktop/AndyLibrary/TestGoogleDriveWorkflow.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 07:15AM

"""
Complete Google Drive workflow testing script
Tests all major Google Drive integration features
"""

import requests
import json
import time
import os
from datetime import datetime

class GoogleDriveWorkflowTester:
    """Test the complete Google Drive workflow"""
    
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_server_health(self):
        """Test if server is running and healthy"""
        print("🏥 Testing server health...")
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server healthy - Version: {data.get('version')}")
                return True
            else:
                print(f"❌ Health check failed - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Server not reachable: {e}")
            return False
    
    def test_mode_detection(self):
        """Test current operating mode"""
        print("\n🔍 Testing mode detection...")
        try:
            response = self.session.get(f"{self.base_url}/api/mode", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Mode: {data.get('display_name')} {data.get('icon')}")
                print(f"   Connection: {data.get('connection_status', 'Unknown')}")
                print(f"   Sync enabled: {data.get('sync_enabled', False)}")
                
                if data.get('sync_enabled'):
                    print(f"   Last sync: {data.get('last_sync', 'Never')}")
                    print(f"   Sync status: {data.get('sync_status', 'Unknown')}")
                
                return data.get('mode') == 'gdrive'
            else:
                print(f"❌ Mode check failed - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Mode detection error: {e}")
            return False
    
    def test_database_access(self):
        """Test database connectivity and content"""
        print("\n📊 Testing database access...")
        try:
            response = self.session.get(f"{self.base_url}/api/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Database accessible:")
                print(f"   📚 Books: {data.get('total_books', 0)}")
                print(f"   📂 Categories: {data.get('total_categories', 0)}")
                print(f"   🏷️ Subjects: {data.get('total_subjects', 0)}")
                return True
            else:
                print(f"❌ Stats check failed - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Database access error: {e}")
            return False
    
    def test_core_api_endpoints(self):
        """Test core API functionality"""
        print("\n🔧 Testing core API endpoints...")
        
        endpoints = [
            ("/api/categories", "Categories"),
            ("/api/subjects", "Subjects"),
            ("/api/books?limit=5", "Books")
        ]
        
        success_count = 0
        for endpoint, name in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else data.get('total', len(data.get('books', [])))
                    print(f"✅ {name}: {count} items")
                    success_count += 1
                else:
                    print(f"❌ {name} failed - Status: {response.status_code}")
            except Exception as e:
                print(f"❌ {name} error: {e}")
        
        return success_count == len(endpoints)
    
    def test_search_functionality(self):
        """Test search capabilities"""
        print("\n🔍 Testing search functionality...")
        try:
            search_payload = {
                "query": "python",
                "page": 1,
                "limit": 5,
                "filters": {"category": "", "subject": "", "rating": 0}
            }
            
            response = self.session.post(
                f"{self.base_url}/api/books/search",
                json=search_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                book_count = len(data.get('books', []))
                print(f"✅ Search working - Found {book_count} books for 'python'")
                return True
            else:
                print(f"❌ Search failed - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Search error: {e}")
            return False
    
    def test_database_download(self):
        """Test database download functionality"""
        print("\n📥 Testing database download...")
        try:
            # First get database info
            info_response = self.session.get(f"{self.base_url}/api/database/info", timeout=10)
            if info_response.status_code == 200:
                info_data = info_response.json()
                if info_data.get('available'):
                    print(f"✅ Database info retrieved:")
                    print(f"   📊 {info_data.get('total_books')} books")
                    print(f"   💾 {info_data.get('file_size_mb')} MB")
                    print(f"   🔄 Source: {info_data.get('source')}")
                    
                    # Test download endpoint (just check it responds, don't actually download)
                    download_response = self.session.head(f"{self.base_url}/api/database/download", timeout=10)
                    if download_response.status_code == 200:
                        print("✅ Download endpoint accessible")
                        return True
                    else:
                        print(f"❌ Download endpoint failed - Status: {download_response.status_code}")
                        return False
                else:
                    print("❌ Database not available for download")
                    return False
            else:
                print(f"❌ Database info failed - Status: {info_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Database download test error: {e}")
            return False
    
    def test_google_drive_sync(self):
        """Test Google Drive sync functionality"""
        print("\n🌐 Testing Google Drive sync...")
        try:
            response = self.session.post(f"{self.base_url}/api/database/sync", timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sync triggered successfully")
                print(f"   Status: {data.get('status')}")
                print(f"   Message: {data.get('message')}")
                return True
            elif response.status_code == 400:
                print("⚠️ Google Drive mode not available (expected in LOCAL mode)")
                return True  # This is expected in local mode
            else:
                print(f"❌ Sync failed - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Sync test error: {e}")
            return False
    
    def run_complete_test(self):
        """Run the complete workflow test"""
        print("🚀 AndyLibrary Google Drive Workflow Test")
        print("=" * 50)
        
        test_results = []
        
        # Core connectivity tests
        test_results.append(("Server Health", self.test_server_health()))
        test_results.append(("Mode Detection", self.test_mode_detection()))
        test_results.append(("Database Access", self.test_database_access()))
        
        # API functionality tests
        test_results.append(("Core APIs", self.test_core_api_endpoints()))
        test_results.append(("Search Function", self.test_search_functionality()))
        
        # Google Drive specific tests
        test_results.append(("Database Download", self.test_database_download()))
        test_results.append(("Google Drive Sync", self.test_google_drive_sync()))
        
        # Results summary
        print("\n" + "=" * 50)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:20} {status}")
            if result:
                passed += 1
        
        print("-" * 50)
        print(f"Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Google Drive workflow is working!")
        elif passed >= total * 0.8:
            print("⚠️ Most tests passed - Minor issues detected")
        else:
            print("❌ Multiple failures detected - Check configuration")
        
        return passed == total

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Google Drive workflow")
    parser.add_argument('--url', default='http://127.0.0.1:8080', 
                       help='Server URL (default: http://127.0.0.1:8080)')
    parser.add_argument('--quick', action='store_true',
                       help='Run only essential tests')
    
    args = parser.parse_args()
    
    tester = GoogleDriveWorkflowTester(args.url)
    
    if args.quick:
        print("🏃 Running quick tests...")
        success = tester.test_server_health() and tester.test_database_access()
        print(f"\n{'✅ Quick tests passed!' if success else '❌ Quick tests failed!'}")
    else:
        success = tester.run_complete_test()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())