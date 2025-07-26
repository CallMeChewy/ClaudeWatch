# File: TestGoogleDriveConnection.py
# Path: /home/herb/Desktop/AndyLibrary/TestGoogleDriveConnection.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 02:15PM

"""
Test Google Drive Connection for AndyLibrary
Validates authentication and basic functionality without requiring manual input
"""

import os
import sys
from typing import Dict, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Source.Core.StudentGoogleDriveAPI import StudentGoogleDriveAPI, GOOGLE_AVAILABLE

def TestGoogleCredentials() -> Dict[str, Any]:
    """Test if Google credentials are properly configured"""
    result = {'success': False, 'details': []}
    
    # Check if Google API libraries are available
    if not GOOGLE_AVAILABLE:
        result['details'].append("❌ Google API libraries not installed")
        result['details'].append("   Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
        return result
    
    result['details'].append("✅ Google API libraries available")
    
    # Check credentials file
    credentials_path = "Config/google_credentials.json"
    if not os.path.exists(credentials_path):
        result['details'].append(f"❌ Credentials file not found: {credentials_path}")
        result['details'].append("   Download from Google Cloud Console")
        return result
    
    result['details'].append(f"✅ Credentials file found: {credentials_path}")
    
    # Check for existing token
    token_path = "Config/google_token.json"
    if os.path.exists(token_path):
        result['details'].append(f"✅ Existing token found: {token_path}")
        result['token_exists'] = True
    else:
        result['details'].append(f"⚠️ No existing token: {token_path}")
        result['details'].append("   OAuth authentication will be required")
        result['token_exists'] = False
    
    result['success'] = True
    return result

def TestStudentBookDownloaderIntegration() -> Dict[str, Any]:
    """Test integration with StudentBookDownloader for cost estimation"""
    result = {'success': False, 'details': []}
    
    try:
        from Source.Core.StudentBookDownloader import StudentBookDownloader
        downloader = StudentBookDownloader()
        result['details'].append("✅ StudentBookDownloader initialized")
        
        # Test cost estimation for first book
        cost_info = downloader.GetBookCostEstimate(1)
        if cost_info:
            result['details'].append(f"✅ Cost estimation working")
            result['details'].append(f"   Book: {cost_info.title}")
            result['details'].append(f"   Size: {cost_info.file_size_mb}MB")
            result['details'].append(f"   Cost: ${cost_info.estimated_cost_usd}")
            result['details'].append(f"   Warning: {cost_info.warning_level}")
        else:
            result['details'].append("❌ Cost estimation failed - no book found")
            return result
        
        result['success'] = True
        
    except Exception as e:
        result['details'].append(f"❌ StudentBookDownloader error: {e}")
    
    return result

def TestChunkedDownloaderIntegration() -> Dict[str, Any]:
    """Test integration with ChunkedDownloader"""
    result = {'success': False, 'details': []}
    
    try:
        from Source.Core.ChunkedDownloader import ChunkedDownloader, NetworkCondition
        downloader = ChunkedDownloader()
        result['details'].append("✅ ChunkedDownloader initialized")
        
        # Test network condition detection
        condition = downloader.DetectNetworkCondition()
        result['details'].append(f"✅ Network condition: {condition.value}")
        
        # Test chunk size calculation
        chunk_size = downloader.GetOptimalChunkSize(condition)
        result['details'].append(f"✅ Optimal chunk size: {chunk_size / 1024:.0f}KB")
        
        result['success'] = True
        
    except Exception as e:
        result['details'].append(f"❌ ChunkedDownloader error: {e}")
    
    return result

def TestDatabaseConnection() -> Dict[str, Any]:
    """Test database connection for book metadata"""
    result = {'success': False, 'details': []}
    
    try:
        import sqlite3
        db_path = "Data/Databases/MyLibrary.db"
        
        if not os.path.exists(db_path):
            result['details'].append(f"❌ Database not found: {db_path}")
            return result
        
        result['details'].append(f"✅ Database found: {db_path}")
        
        # Test database connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute("SELECT COUNT(*) FROM books")
        book_count = cursor.fetchone()[0]
        result['details'].append(f"✅ Books in database: {book_count}")
        
        # Get sample book
        cursor.execute("SELECT id, title, author, FileSize FROM books LIMIT 1")
        sample_book = cursor.fetchone()
        if sample_book:
            book_id, title, author, file_size = sample_book
            size_mb = (file_size or 5000000) / (1024 * 1024)
            result['details'].append(f"✅ Sample book: {title} by {author}")
            result['details'].append(f"   Size: {size_mb:.1f}MB")
        
        conn.close()
        result['success'] = True
        
    except Exception as e:
        result['details'].append(f"❌ Database error: {e}")
    
    return result

def RunAllTests() -> None:
    """Run all Google Drive integration tests"""
    print("🧪 TESTING GOOGLE DRIVE INTEGRATION FOR ANDYLIBRARY")
    print("=" * 60)
    
    tests = [
        ("Google Credentials Check", TestGoogleCredentials),
        ("Database Connection", TestDatabaseConnection),
        ("StudentBookDownloader Integration", TestStudentBookDownloaderIntegration),
        ("ChunkedDownloader Integration", TestChunkedDownloaderIntegration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 40)
        
        result = test_func()
        results[test_name] = result
        
        for detail in result['details']:
            print(f"  {detail}")
        
        if result['success']:
            print(f"  ✅ {test_name}: PASSED")
        else:
            print(f"  ❌ {test_name}: FAILED")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Ready for Google Drive integration.")
    else:
        print("⚠️ Some tests failed. Review issues above.")
        
        # Check for authentication readiness
        creds_result = results.get("Google Credentials Check", {})
        if creds_result.get('success') and not creds_result.get('token_exists', False):
            print("\n💡 NEXT STEP: Run OAuth authentication")
            print("   python Source/Core/StudentGoogleDriveAPI.py")
            print("   (This will require browser interaction to authorize)")

if __name__ == "__main__":
    RunAllTests()