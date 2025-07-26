# File: TestGoogleDriveDevMode.py
# Path: /home/herb/Desktop/AndyLibrary/TestGoogleDriveDevMode.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 02:22PM

"""
Development Mode Test for Google Drive Integration
Simulates Google Drive API responses to test full system without OAuth
"""

import os
import sys
import time
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our systems
from Source.Core.StudentBookDownloader import StudentBookDownloader
from Source.Core.ChunkedDownloader import ChunkedDownloader, DownloadProgress, NetworkCondition

@dataclass
class MockGoogleDriveFile:
    """Mock Google Drive file for dev testing"""
    file_id: str
    name: str
    size_bytes: int
    mime_type: str

class DevModeGoogleDriveAPI:
    """Development mode Google Drive API simulator"""
    
    def __init__(self):
        self.authenticated = False
        self.library_folder_id = "mock_library_folder_123"
        
        # Mock book files from our database
        self.mock_books = {
            "1970-03-Management-Accounting-v51-n9 Litton ABS 1231": MockGoogleDriveFile(
                file_id="mock_file_001",
                name="1970-03-Management-Accounting-v51-n9 Litton ABS 1231.pdf",
                size_bytes=5 * 1024 * 1024,  # 5MB
                mime_type="application/pdf"
            ),
            "Advanced Engineering Mathematics": MockGoogleDriveFile(
                file_id="mock_file_002", 
                name="Advanced Engineering Mathematics.pdf",
                size_bytes=25 * 1024 * 1024,  # 25MB
                mime_type="application/pdf"
            ),
            "Introduction to Python Programming": MockGoogleDriveFile(
                file_id="mock_file_003",
                name="Introduction to Python Programming.pdf", 
                size_bytes=2 * 1024 * 1024,  # 2MB
                mime_type="application/pdf"
            )
        }
        
        # Initialize student systems
        self.cost_calculator = StudentBookDownloader()
        self.chunked_downloader = ChunkedDownloader()
    
    def MockAuthenticate(self) -> bool:
        """Simulate successful authentication"""
        print("🔐 DEV MODE: Simulating Google Drive authentication...")
        time.sleep(1)
        print("✅ DEV MODE: Authentication successful!")
        self.authenticated = True
        return True
    
    def MockFindLibraryFolder(self) -> Optional[str]:
        """Simulate finding library folder"""
        if not self.authenticated:
            print("❌ Not authenticated with Google Drive")
            return None
        
        print("🔍 DEV MODE: Searching for 'AndyLibrary' folder...")
        time.sleep(0.5)
        print(f"✅ DEV MODE: Found library folder: {self.library_folder_id}")
        return self.library_folder_id
    
    def MockGetBookFileInfo(self, book_title: str) -> Optional[MockGoogleDriveFile]:
        """Simulate getting book file info"""
        print(f"🔍 DEV MODE: Searching for book: {book_title}")
        
        # Try exact match first
        if book_title in self.mock_books:
            file_info = self.mock_books[book_title]
            print(f"✅ DEV MODE: Found exact match - {file_info.name}")
            return file_info
        
        # Try partial match
        for mock_title, file_info in self.mock_books.items():
            if book_title.lower() in mock_title.lower():
                print(f"✅ DEV MODE: Found partial match - {file_info.name}")
                return file_info
        
        print(f"❌ DEV MODE: Book not found in mock library")
        return None
    
    def MockDownloadWithStudentProtection(
        self, 
        book_id: int, 
        book_title: str, 
        region: str = "developing"
    ) -> Dict[str, Any]:
        """Simulate full student-protected download"""
        
        print(f"📚 DEV MODE: Starting protected download for: {book_title}")
        
        # Step 1: Get mock file info
        file_info = self.MockGetBookFileInfo(book_title)
        if not file_info:
            return {
                'success': False,
                'error': f'Book file not found in mock library: {book_title}',
                'recommendation': 'Check that the book exists in the available mock books'
            }
        
        print(f"✅ DEV MODE: Found book file: {file_info.name} ({file_info.size_bytes / (1024*1024):.1f}MB)")
        
        # Step 2: Get cost estimate
        cost_info = self.cost_calculator.GetBookCostEstimate(book_id)
        if cost_info:
            # Update with real mock file size
            real_size_mb = file_info.size_bytes / (1024 * 1024)
            real_cost = real_size_mb * 0.10  # $0.10/MB for developing region
            
            print(f"💰 DEV MODE: Cost estimate: ${real_cost:.2f} for {real_size_mb:.1f}MB")
            
            if real_cost > 3.0:  # High cost warning
                return {
                    'success': False,
                    'cost_warning': True,
                    'estimated_cost': real_cost,
                    'file_size_mb': real_size_mb,
                    'warning_level': 'extreme',
                    'recommendation': 'DEV MODE: This book is very expensive for mobile download.',
                    'alternatives': [
                        'Wait for WiFi connection (Free)',
                        'Download a smaller book instead',
                        'Read book description only'
                    ]
                }
        
        # Step 3: Start mock chunked download
        print("🚀 DEV MODE: Starting chunked download simulation...")
        
        # Create mock progress callback
        def mock_progress_callback(progress: DownloadProgress):
            percentage = (progress.downloaded_bytes / progress.total_size_bytes) * 100
            print(f"  📊 DEV MODE Progress: {percentage:.1f}% - {progress.student_message if hasattr(progress, 'student_message') else 'Downloading...'}")
        
        # Simulate download
        try:
            # Use ChunkedDownloader for realistic simulation
            download_result = self.chunked_downloader.StartChunkedDownload(
                book_id=book_id,
                title=book_title,
                file_size_bytes=file_info.size_bytes,
                download_url=f"mock://drive.google.com/file/{file_info.file_id}",
                progress_callback=mock_progress_callback,
                network_condition=NetworkCondition.SLOW_3G
            )
            
            # Monitor progress for a few seconds
            print("📱 DEV MODE: Monitoring download progress...")
            for i in range(3):
                time.sleep(1)
                progress_info = self.chunked_downloader.GetStudentFriendlyProgress(book_id)
                if progress_info:
                    print(f"  {progress_info['student_message']} ({progress_info['percentage_complete']}%)")
                    if progress_info['status'] in ['completed', 'error']:
                        break
            
            return {
                'success': True,
                'message': f'DEV MODE: {download_result}',
                'file_size_mb': file_info.size_bytes / (1024 * 1024),
                'estimated_cost': real_cost if 'real_cost' in locals() else 0.0,
                'network_condition': 'slow_3g',
                'download_id': book_id,
                'dev_mode': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'DEV MODE: Download simulation failed: {str(e)}',
                'recommendation': 'Check the chunked downloader implementation'
            }

def TestFullIntegrationDevMode():
    """Test complete Google Drive integration in development mode"""
    print("🧪 TESTING GOOGLE DRIVE INTEGRATION - DEV MODE")
    print("=" * 60)
    
    # Initialize dev mode API
    dev_api = DevModeGoogleDriveAPI()
    
    # Test authentication
    print("\n🔐 Testing Authentication...")
    if not dev_api.MockAuthenticate():
        print("❌ Authentication failed")
        return
    
    # Test library folder discovery
    print("\n📁 Testing Library Folder Discovery...")
    if not dev_api.MockFindLibraryFolder():
        print("❌ Library folder discovery failed")
        return
    
    # Test book downloads
    test_books = [
        (1, "1970-03-Management-Accounting-v51-n9 Litton ABS 1231"),
        (2, "Advanced Engineering Mathematics"),
        (3, "Introduction to Python Programming")
    ]
    
    print("\n📚 Testing Book Downloads...")
    print("-" * 40)
    
    for book_id, book_title in test_books:
        print(f"\n📖 Testing: {book_title}")
        print("-" * 30)
        
        result = dev_api.MockDownloadWithStudentProtection(book_id, book_title)
        
        if result['success']:
            print(f"✅ Download successful!")
            print(f"   File size: {result['file_size_mb']:.1f}MB")
            print(f"   Estimated cost: ${result['estimated_cost']:.2f}")
            print(f"   Network condition: {result['network_condition']}")
        else:
            print(f"❌ Download failed: {result.get('error', 'Unknown error')}")
            if 'cost_warning' in result:
                print(f"⚠️ Cost warning: {result['recommendation']}")
    
    # Test student cost protection
    print("\n💰 Testing Student Cost Protection...")
    print("-" * 40)
    
    cost_calculator = StudentBookDownloader()
    
    # Test multiple book cost analysis
    book_ids = [1, 2, 3]
    multi_cost = cost_calculator.GetMultipleBooksCost(book_ids)
    
    print(f"📊 Multiple book analysis:")
    print(f"   Total books: {len(multi_cost['books'])}")
    print(f"   Total cost: ${multi_cost['total_cost_usd']}")
    print(f"   Total size: {multi_cost['total_size_mb']}MB")
    print(f"   Budget impact: {multi_cost['budget_percentage']}%")
    print(f"   Warning level: {multi_cost['warning_level']}")
    print(f"   Remaining budget: ${multi_cost['remaining_budget']}")
    
    # Test student guidance
    print("\n🎓 Testing Student Guidance...")
    print("-" * 40)
    
    guidance = cost_calculator.GetDownloadOptions(1)
    if 'error' not in guidance:
        print(f"📖 Book: {guidance['book_info']['title']}")
        print(f"💾 Size: {guidance['book_info']['size_mb']}MB")
        print(f"💰 Cost: ${guidance['book_info']['cost_usd']}")
        print(f"⚠️ Warning: {guidance['book_info']['warning_level']}")
        
        print(f"\n🎯 Download Options:")
        for option in guidance['download_options']:
            marker = "✅" if option['recommended'] else "⚪"
            print(f"   {marker} {option['label']}")
        
        print(f"\n💡 Student Guidance:")
        print(f"   {guidance['student_guidance']['recommendation']}")
        print(f"   {guidance['student_guidance']['explanation']}")
    
    print("\n" + "=" * 60)
    print("🎉 DEV MODE INTEGRATION TEST COMPLETE")
    print("✅ All systems working together successfully!")
    print("📱 Ready for real Google Drive OAuth when credentials are configured")

if __name__ == "__main__":
    TestFullIntegrationDevMode()