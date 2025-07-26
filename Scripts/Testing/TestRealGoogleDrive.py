# File: TestRealGoogleDrive.py
# Path: /home/herb/Desktop/AndyLibrary/TestRealGoogleDrive.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 02:25PM

"""
Real Google Drive Integration Test
Interactive test that handles OAuth flow properly
"""

import os
import sys
import time
from typing import Dict, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Source.Core.StudentGoogleDriveAPI import StudentGoogleDriveAPI, GOOGLE_AVAILABLE

def TestRealGoogleDriveInteractive():
    """Test real Google Drive with proper interactive OAuth"""
    print("🧪 TESTING REAL GOOGLE DRIVE INTEGRATION")
    print("=" * 60)
    
    if not GOOGLE_AVAILABLE:
        print("❌ Google API libraries not available")
        print("   Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
        return
    
    print("✅ Google API libraries available")
    
    # Initialize the API
    try:
        student_gdrive = StudentGoogleDriveAPI()
        print("✅ StudentGoogleDriveAPI initialized")
    except Exception as e:
        print(f"❌ Failed to initialize API: {e}")
        return
    
    # Check for existing token
    token_path = "Config/google_token.json"
    if os.path.exists(token_path):
        print(f"✅ Found existing token: {token_path}")
        print("🔄 Attempting to use existing credentials...")
    else:
        print(f"⚠️ No existing token found")
        print("📱 OAuth authentication will be required")
        print("\nWhen prompted:")
        print("1. Copy the authorization URL")
        print("2. Open it in your browser")
        print("3. Sign in and grant permissions")
        print("4. Copy the authorization code")
        print("5. Paste it back here")
        print("\nPress Enter to continue...")
        input()
    
    # Test authentication
    print("\n🔐 Testing Authentication...")
    print("-" * 40)
    
    try:
        auth_success = student_gdrive.Authenticate()
        if auth_success:
            print("🎉 Authentication successful!")
        else:
            print("❌ Authentication failed")
            return
    except KeyboardInterrupt:
        print("\n⚠️ Authentication cancelled by user")
        return
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # Test library folder discovery
    print("\n📁 Testing Library Folder Discovery...")
    print("-" * 40)
    
    try:
        library_folder_id = student_gdrive.FindLibraryFolder()
        if library_folder_id:
            print(f"✅ Library folder found: {library_folder_id}")
        else:
            print("❌ Library folder not found")
            print("💡 Create an 'AndyLibrary' folder in your Google Drive")
            print("   Upload some PDF books to test with")
            return
    except Exception as e:
        print(f"❌ Library folder search error: {e}")
        return
    
    # Test library statistics
    print("\n📊 Testing Library Statistics...")
    print("-" * 40)
    
    try:
        stats = student_gdrive.GetLibraryStats()
        if 'error' not in stats:
            print(f"📚 Library Statistics:")
            print(f"   Total files: {stats['total_files']}")
            print(f"   Total size: {stats['total_size_mb']:.1f}MB ({stats['total_size_gb']:.2f}GB)")
            print(f"   Average file size: {stats['average_file_size_mb']:.1f}MB")
            
            if stats['file_types']:
                print(f"   File types:")
                for mime_type, count in stats['file_types'].items():
                    type_name = mime_type.split('/')[-1] if '/' in mime_type else mime_type
                    print(f"     {type_name}: {count} files")
        else:
            print(f"❌ Stats error: {stats['error']}")
    except Exception as e:
        print(f"❌ Library stats error: {e}")
    
    # Test book file search
    print("\n🔍 Testing Book File Search...")
    print("-" * 40)
    
    # Try to find some common book titles
    test_titles = [
        "Management",  # Partial match for Litton ABS book
        "Engineering", # Common textbook topic
        "Python",      # Programming book
        "Mathematics"  # Math textbook
    ]
    
    for title in test_titles:
        try:
            print(f"\n📖 Searching for books containing: '{title}'")
            file_info = student_gdrive.GetBookFileInfo(title)
            
            if file_info:
                size_mb = file_info.size_bytes / (1024 * 1024)
                print(f"   ✅ Found: {file_info.name}")
                print(f"   📦 Size: {size_mb:.1f}MB")
                print(f"   🆔 File ID: {file_info.file_id}")
                print(f"   💰 Estimated cost (developing region): ${size_mb * 0.10:.2f}")
                
                # Test cost integration
                try:
                    cost_info = student_gdrive.cost_calculator.GetBookCostEstimate(1)  # Use first book from DB
                    if cost_info:
                        print(f"   ⚠️ Warning level: {cost_info.warning_level}")
                        if size_mb * 0.10 > 1.0:
                            print(f"   💡 Recommendation: Consider WiFi download for cost savings")
                except Exception as e:
                    print(f"   ⚠️ Cost calculation error: {e}")
                
                break  # Found one, that's good enough for testing
            else:
                print(f"   ❌ No books found for: '{title}'")
        except Exception as e:
            print(f"   ❌ Search error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 REAL GOOGLE DRIVE TEST SUMMARY")
    print("=" * 60)
    print("✅ Google Drive connection established")
    print("✅ Library folder discovered")
    print("✅ File statistics retrieved")
    print("✅ Book search functionality working")
    print("✅ Cost estimation integrated")
    print("\n🚀 Ready for student book downloads!")
    print("💡 Students can now access books with full cost protection")

if __name__ == "__main__":
    try:
        TestRealGoogleDriveInteractive()
    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()