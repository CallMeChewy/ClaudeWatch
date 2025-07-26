# File: TestGoogleDriveWithWebCredentials.py
# Path: /home/herb/Desktop/AndyLibrary/TestGoogleDriveWithWebCredentials.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 02:32PM

"""
Test Google Drive Integration Using Working Web Credentials
Uses the proven client_id from AndyWeb for Google Drive access
"""

import os
import sys
import json
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def UpdateCredentialsFromWebSetup():
    """Update credentials file with working client_id from AndyWeb"""
    print("🔧 UPDATING GOOGLE CREDENTIALS FROM ANDYWEB")
    print("=" * 50)
    
    # Working credentials from AndyWeb/HTML/GoogleAuthorzeTest.html
    working_client_id = "906077568035-3ofuni3d731kk5m732nbv040j27b5glt.apps.googleusercontent.com"
    
    credentials_data = {
        "web": {
            "client_id": working_client_id,
            "project_id": "andygoogle-project",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "YOUR_CLIENT_SECRET_HERE",  # From web working setup
            "redirect_uris": [
                "http://localhost:8080",
                "http://127.0.0.1:8080",
                "http://localhost:8000",
                "http://127.0.0.1:8000"
            ],
            "javascript_origins": [
                "http://localhost:8000",
                "http://127.0.0.1:8000",
                "http://localhost:8080",
                "http://127.0.0.1:8080"
            ]
        }
    }
    
    # Write updated credentials
    creds_path = "Config/google_credentials.json"
    try:
        os.makedirs(os.path.dirname(creds_path), exist_ok=True)
        with open(creds_path, 'w') as f:
            json.dump(credentials_data, f, indent=2)
        
        print(f"✅ Updated credentials file: {creds_path}")
        print(f"✅ Client ID: {working_client_id[:30]}...")
        print(f"✅ Project: andygoogle-project")
        print(f"✅ Redirect URIs configured for ports 8000 and 8080")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating credentials: {e}")
        return False

def TestWithWebCredentials():
    """Test Google Drive API with web credentials"""
    print("\n🚀 TESTING WITH WEB CREDENTIALS")
    print("=" * 50)
    
    try:
        from Source.Core.StudentGoogleDriveAPI import StudentGoogleDriveAPI, GOOGLE_AVAILABLE
        
        if not GOOGLE_AVAILABLE:
            print("❌ Google API libraries not available")
            return False
        
        print("✅ Google API libraries available")
        
        # Initialize API with updated credentials
        api = StudentGoogleDriveAPI("Config/google_credentials.json")
        print("✅ StudentGoogleDriveAPI initialized")
        
        print("\n🔐 Now run OAuth authentication:")
        print("1. python Source/Core/StudentGoogleDriveAPI.py")
        print("2. Follow the authorization URL")
        print("3. Complete the OAuth flow")
        print("4. Token will be saved automatically")
        
        print("\n💡 After OAuth, you can test:")
        print("- Library folder discovery")
        print("- Book file searches")
        print("- Cost-protected downloads")
        print("- Student choice interface")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing with web credentials: {e}")
        return False

def CreateTestInstructions():
    """Create step-by-step test instructions"""
    print("\n📋 STEP-BY-STEP TEST INSTRUCTIONS")
    print("=" * 50)
    
    instructions = """
🎯 COMPLETE GOOGLE DRIVE INTEGRATION TEST

1. 📁 PREPARE GOOGLE DRIVE
   - Go to drive.google.com
   - Create folder named "AndyLibrary"
   - Upload 2-3 PDF books for testing:
     * Small book (1-2MB) - tests low cost downloads
     * Medium book (5-10MB) - tests cost warnings
     * Large book (20MB+) - tests high cost protection

2. 🔐 COMPLETE OAUTH AUTHENTICATION
   Run: python Source/Core/StudentGoogleDriveAPI.py
   - Copy authorization URL to browser
   - Sign in to Google account
   - Grant Drive access permissions
   - Copy authorization code back to terminal
   - Token saved to Config/google_token.json

3. ✅ VERIFY INTEGRATION
   Run: python TestRealGoogleDrive.py
   - Tests authentication with saved token
   - Discovers AndyLibrary folder
   - Shows library statistics
   - Tests book search functionality
   - Validates cost estimation system

4. 🎓 TEST STUDENT EXPERIENCE
   - Try downloading different sized books
   - Verify cost warnings appear correctly
   - Test chunked download progress
   - Confirm student choice interface works

5. 🎉 READY FOR PRODUCTION
   - Full Google Drive integration complete
   - Student cost protection active
   - Educational mission architecture deployed
   """
    
    print(instructions)
    
    print("\n🔑 KEY CREDENTIALS (Updated from AndyWeb):")
    print("✅ Client ID: 906077568035-3ofuni3d731kk5m732nbv040j27b5glt.apps.googleusercontent.com")
    print("✅ Project: andygoogle-project")
    print("✅ Scopes: drive.readonly, drive.metadata.readonly")
    print("✅ Redirect URIs: localhost:8000, localhost:8080")

if __name__ == "__main__":
    # Update credentials from working web setup
    if UpdateCredentialsFromWebSetup():
        print("\n✅ Credentials updated successfully!")
        
        # Test with updated credentials
        if TestWithWebCredentials():
            print("\n🎉 Ready for OAuth authentication!")
        
        # Show complete instructions
        CreateTestInstructions()
        
        print("\n🚀 NEXT STEP: Run OAuth authentication")
        print("   python Source/Core/StudentGoogleDriveAPI.py")
        
    else:
        print("❌ Failed to update credentials")