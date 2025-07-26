# File: PrepareGoogleDriveTest.py
# Path: /home/herb/Desktop/AndyLibrary/PrepareGoogleDriveTest.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 02:27PM

"""
Prepare Google Drive Integration - Non-Interactive Setup
Validates setup and provides manual OAuth instructions
"""

import os
import sys
import json
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Source.Core.StudentGoogleDriveAPI import GOOGLE_AVAILABLE

def ValidateGoogleDriveSetup() -> Dict[str, Any]:
    """Validate Google Drive setup without OAuth"""
    print("🔧 VALIDATING GOOGLE DRIVE SETUP")
    print("=" * 50)
    
    validation = {'ready': False, 'steps_needed': []}
    
    # Check Google API libraries
    if not GOOGLE_AVAILABLE:
        print("❌ Google API libraries missing")
        validation['steps_needed'].append("Install Google libraries: pip install google-auth google-auth-oauthlib google-api-python-client")
        return validation
    
    print("✅ Google API libraries available")
    
    # Check credentials file
    creds_path = "Config/google_credentials.json"
    if not os.path.exists(creds_path):
        print("❌ Google credentials file not found")
        validation['steps_needed'].append(f"Create {creds_path} with Google Cloud Console credentials")
        return validation
    
    print(f"✅ Credentials file found: {creds_path}")
    
    # Validate credentials content
    try:
        with open(creds_path, 'r') as f:
            creds = json.load(f)
        
        if 'web' not in creds:
            print("❌ Invalid credentials format - missing 'web' section")
            validation['steps_needed'].append("Fix credentials file format")
            return validation
        
        web_creds = creds['web']
        required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
        missing_fields = [field for field in required_fields if field not in web_creds]
        
        if missing_fields:
            print(f"❌ Missing credential fields: {missing_fields}")
            validation['steps_needed'].append(f"Add missing fields to credentials: {missing_fields}")
            return validation
        
        if web_creds.get('client_secret') == 'YOUR_ACTUAL_SECRET_HERE':
            print("⚠️ Client secret needs to be updated with real value")
            validation['steps_needed'].append("Update client_secret in credentials file with real value from Google Cloud Console")
        else:
            print("✅ Client secret appears to be configured")
        
        print(f"✅ Client ID: {web_creds['client_id'][:20]}...")
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in credentials file")
        validation['steps_needed'].append("Fix JSON format in credentials file")
        return validation
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        validation['steps_needed'].append("Fix credentials file")
        return validation
    
    # Check for existing token
    token_path = "Config/google_token.json"
    if os.path.exists(token_path):
        print(f"✅ Existing token found: {token_path}")
        try:
            with open(token_path, 'r') as f:
                token_data = json.load(f)
            if 'access_token' in token_data:
                print("✅ Token contains access_token")
            if 'refresh_token' in token_data:
                print("✅ Token contains refresh_token (good for long-term access)")
        except Exception as e:
            print(f"⚠️ Token file exists but may be invalid: {e}")
    else:
        print(f"⚠️ No existing token: {token_path}")
        validation['steps_needed'].append("Complete OAuth authentication to generate token")
    
    # Check database connection
    db_path = "Data/Databases/MyLibrary.db"
    if os.path.exists(db_path):
        print(f"✅ Database found: {db_path}")
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            book_count = cursor.fetchone()[0]
            print(f"✅ Database contains {book_count} book records")
            conn.close()
        except Exception as e:
            print(f"⚠️ Database issue: {e}")
    else:
        print(f"❌ Database not found: {db_path}")
        validation['steps_needed'].append("Ensure database is in correct location")
    
    # Summary
    if not validation['steps_needed']:
        validation['ready'] = True
        print("\n🎉 Google Drive setup validation complete!")
        print("✅ Ready for OAuth authentication")
    else:
        print(f"\n⚠️ Setup needs {len(validation['steps_needed'])} more steps:")
        for i, step in enumerate(validation['steps_needed'], 1):
            print(f"   {i}. {step}")
    
    return validation

def ProvideOAuthInstructions():
    """Provide manual OAuth instructions"""
    print("\n🔐 MANUAL OAUTH AUTHENTICATION INSTRUCTIONS")
    print("=" * 50)
    
    print("Since interactive OAuth isn't working in this environment,")
    print("here's how to authenticate manually:")
    print()
    
    # Generate the OAuth URL
    try:
        from Source.Core.StudentGoogleDriveAPI import StudentGoogleDriveAPI
        api = StudentGoogleDriveAPI()
        
        print("1. 📱 AUTHORIZATION URL:")
        print("   Run this command in a terminal where you can input text:")
        print("   python Source/Core/StudentGoogleDriveAPI.py")
        print()
        print("2. 🌐 BROWSER STEPS:")
        print("   - Copy the authorization URL from the output")
        print("   - Open it in your browser")
        print("   - Sign in to your Google account")
        print("   - Grant permission to access Google Drive") 
        print("   - Copy the authorization code")
        print()
        print("3. 🔑 COMPLETE AUTHENTICATION:")
        print("   - Paste the authorization code when prompted")
        print("   - The system will save your token to Config/google_token.json")
        print()
        print("4. ✅ VERIFY SUCCESS:")
        print("   - Run: python TestRealGoogleDrive.py")
        print("   - Should now work without OAuth prompts")
        
    except Exception as e:
        print(f"❌ Error generating instructions: {e}")
    
    print("\n💡 ALTERNATIVE: Create AndyLibrary folder in Google Drive")
    print("   1. Go to drive.google.com")
    print("   2. Create a folder named 'AndyLibrary'")
    print("   3. Upload some PDF books for testing")
    print("   4. Complete OAuth authentication as above")

def CreateTestBooks():
    """Create some test books info for Google Drive testing"""
    print("\n📚 RECOMMENDED TEST BOOKS FOR GOOGLE DRIVE")
    print("=" * 50)
    
    test_books = [
        {
            'title': 'Small Test Book',
            'suggested_name': 'SmallTestBook.pdf',
            'size_range': '1-2MB',
            'cost_estimate': '$0.10-$0.20',
            'purpose': 'Test low-cost downloads'
        },
        {
            'title': 'Medium Test Book', 
            'suggested_name': 'MediumTestBook.pdf',
            'size_range': '5-10MB',
            'cost_estimate': '$0.50-$1.00',
            'purpose': 'Test medium-cost warnings'
        },
        {
            'title': 'Large Test Book',
            'suggested_name': 'LargeTestBook.pdf', 
            'size_range': '20-30MB',
            'cost_estimate': '$2.00-$3.00',
            'purpose': 'Test high-cost warnings and WiFi recommendations'
        }
    ]
    
    print("Upload these types of books to your 'AndyLibrary' folder:")
    print()
    
    for book in test_books:
        print(f"📖 {book['title']}")
        print(f"   File name: {book['suggested_name']}")
        print(f"   Size: {book['size_range']}")
        print(f"   Cost: {book['cost_estimate']} (developing region)")
        print(f"   Purpose: {book['purpose']}")
        print()

if __name__ == "__main__":
    validation = ValidateGoogleDriveSetup()
    
    if validation['ready']:
        ProvideOAuthInstructions()
    
    CreateTestBooks()
    
    print("\n🎯 NEXT STEPS:")
    if validation['steps_needed']:
        print("1. Complete the setup steps listed above")
        print("2. Then follow OAuth instructions")
    else:
        print("1. Complete OAuth authentication manually")
        print("2. Upload test books to Google Drive")
        print("3. Run: python TestRealGoogleDrive.py")
    
    print("\n🎉 Once complete, you'll have full Google Drive integration!")
    print("Students will be able to download books with cost protection.")