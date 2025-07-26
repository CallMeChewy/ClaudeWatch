# File: RunComprehensiveTests.py
# Path: /home/herb/Desktop/AndyLibrary/RunComprehensiveTests.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 08:20PM

"""
Comprehensive Test Suite for PROJECT HIMALAYA
Tests all core functionality, performance, and integration
"""

import os
import sys
import sqlite3
import time
import requests
import json
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ProjectHimalayaTestSuite:
    """Complete test suite for AndyLibrary platform"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8081"
        self.api_base = f"{self.base_url}/api"
        self.test_results = []
        self.database_path = "Data/Databases/MyLibrary.db"
        
    def RunAllTests(self):
        """Execute comprehensive test suite"""
        print("🧪 PROJECT HIMALAYA COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print(f"Database: {self.database_path}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Test categories
        test_categories = [
            ("Database Connectivity", self.TestDatabaseConnectivity),
            ("Core API Endpoints", self.TestCoreAPI),
            ("Book Management", self.TestBookManagement),
            ("Student Protection", self.TestStudentProtection),
            ("PDF Access System", self.TestPDFAccess),
            ("Search & Filtering", self.TestSearchFiltering), 
            ("Google Drive Integration", self.TestGoogleDriveIntegration),
            ("Performance Benchmarks", self.TestPerformance),
            ("Error Handling", self.TestErrorHandling),
            ("Security Validation", self.TestSecurity)
        ]
        
        # Execute all test categories
        for category_name, test_function in test_categories:
            print(f"\n🔍 Testing: {category_name}")
            print("-" * 40)
            
            try:
                results = test_function()
                self.test_results.extend(results)
                
                passed = sum(1 for r in results if r['status'] == 'PASS')
                total = len(results)
                print(f"✅ {category_name}: {passed}/{total} tests passed")
                
            except Exception as e:
                print(f"❌ {category_name}: Test category failed - {e}")
                self.test_results.append({
                    'category': category_name,
                    'test': 'Category Execution',
                    'status': 'FAIL',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # Generate test report
        self.GenerateTestReport()
        
    def TestDatabaseConnectivity(self) -> List[Dict]:
        """Test database connection and basic queries"""
        results = []
        
        # Test 1: Database file exists
        results.append(self.RunTest(
            "Database File Exists",
            lambda: os.path.exists(self.database_path),
            "Database file found at expected location"
        ))
        
        # Test 2: Database connection
        try:
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            
            results.append(self.RunTest(
                "Database Connection",
                lambda: True,
                "Successfully connected to SQLite database"
            ))
            
            # Test 3: Books table exists and populated
            cursor = conn.execute("SELECT COUNT(*) FROM books")
            book_count = cursor.fetchone()[0]
            
            results.append(self.RunTest(
                "Books Table Populated",
                lambda: book_count > 1000,
                f"Found {book_count} books in database"
            ))
            
            # Test 4: Essential columns exist
            cursor = conn.execute("PRAGMA table_info(books)")
            columns = [row[1] for row in cursor.fetchall()]
            essential_columns = ['id', 'title', 'category_id', 'subject_id']
            
            results.append(self.RunTest(
                "Essential Columns Present",
                lambda: all(col in columns for col in essential_columns),
                f"All essential columns found: {essential_columns}"
            ))
            
            conn.close()
            
        except Exception as e:
            results.append(self.RunTest(
                "Database Connection",
                lambda: False,
                f"Database connection failed: {e}"
            ))
        
        return results
    
    def TestCoreAPI(self) -> List[Dict]:
        """Test core API endpoints"""
        results = []
        
        # Test 1: API Health Check
        results.append(self.RunTest(
            "API Health Check",
            lambda: self.MakeAPICall("/health").status_code == 200,
            "API server responding to health checks"
        ))
        
        # Test 2: Books List Endpoint
        response = self.MakeAPICall("/books")
        results.append(self.RunTest(
            "Books List Endpoint",
            lambda: response.status_code == 200 and 'books' in response.json(),
            "Books list endpoint returning data"
        ))
        
        # Test 3: Categories Endpoint
        results.append(self.RunTest(
            "Categories Endpoint",
            lambda: self.MakeAPICall("/categories").status_code == 200,
            "Categories endpoint accessible"
        ))
        
        # Test 4: Subjects Endpoint
        results.append(self.RunTest(
            "Subjects Endpoint", 
            lambda: self.MakeAPICall("/subjects").status_code == 200,
            "Subjects endpoint accessible"
        ))
        
        # Test 5: Stats Endpoint
        response = self.MakeAPICall("/stats")
        results.append(self.RunTest(
            "Stats Endpoint",
            lambda: response.status_code == 200 and response.json().get('total_books', 0) > 0,
            "Stats endpoint returning library statistics"
        ))
        
        return results
    
    def TestBookManagement(self) -> List[Dict]:
        """Test book-specific functionality"""
        results = []
        
        # Get a sample book for testing
        books_response = self.MakeAPICall("/books?limit=1")
        if books_response.status_code == 200:
            books_data = books_response.json()
            if books_data.get('books'):
                sample_book_id = books_data['books'][0]['id']
                
                # Test 1: Individual Book Details
                results.append(self.RunTest(
                    "Book Detail Endpoint",
                    lambda: self.MakeAPICall(f"/books/{sample_book_id}").status_code == 200,
                    f"Book details accessible for book ID {sample_book_id}"
                ))
                
                # Test 2: Book Thumbnail
                results.append(self.RunTest(
                    "Book Thumbnail Endpoint",
                    lambda: self.MakeAPICall(f"/books/{sample_book_id}/thumbnail").status_code in [200, 204],
                    "Book thumbnail endpoint responding (may be empty)"
                ))
                
                # Test 3: Book Cost Estimation
                results.append(self.RunTest(
                    "Book Cost Endpoint",
                    lambda: self.MakeAPICall(f"/books/{sample_book_id}/cost").status_code == 200,
                    "Book cost estimation working"
                ))
                
                # Test 4: Download Options
                results.append(self.RunTest(
                    "Download Options Endpoint",
                    lambda: self.MakeAPICall(f"/books/{sample_book_id}/download-options").status_code == 200,
                    "Download options endpoint accessible"
                ))
                
            else:
                results.append(self.RunTest(
                    "Sample Book Available",
                    lambda: False,
                    "No books available for testing"
                ))
        
        return results
    
    def TestStudentProtection(self) -> List[Dict]:
        """Test student cost protection features"""
        results = []
        
        try:
            from Source.Core.StudentBookDownloader import StudentBookDownloader, StudentRegion
            
            downloader = StudentBookDownloader()
            
            # Test 1: Cost Calculator Initialization
            results.append(self.RunTest(
                "Cost Calculator Initialization",
                lambda: downloader is not None,
                "StudentBookDownloader initialized successfully"
            ))
            
            # Test 2: Cost Estimation for Sample Book
            cost_info = downloader.GetBookCostEstimate(1)
            results.append(self.RunTest(
                "Cost Estimation Function",
                lambda: cost_info is not None and cost_info.budget_percentage >= 0,
                f"Cost estimation working: ${cost_info.estimated_cost_usd:.2f}"
            ))
            
            # Test 3: Regional Pricing
            for region in [StudentRegion.DEVELOPING, StudentRegion.EMERGING, StudentRegion.DEVELOPED]:
                region_cost = downloader.GetBookCostEstimate(1, region)
                results.append(self.RunTest(
                    f"Regional Pricing - {region.value}",
                    lambda: region_cost is not None,
                    f"{region.value} region pricing: ${region_cost.estimated_cost_usd:.2f}" if region_cost else "Failed"
                ))
            
            # Test 4: Download Options Generation
            options = downloader.GetDownloadOptions(1)
            results.append(self.RunTest(
                "Download Options Generation",
                lambda: 'download_options' in options and len(options['download_options']) > 0,
                f"Generated {len(options.get('download_options', []))} download options"
            ))
            
            # Test 5: Budget Summary
            summary = downloader.GetMonthlySpendingSummary()
            results.append(self.RunTest(
                "Budget Summary Generation",
                lambda: 'remaining_budget' in summary and summary['remaining_budget'] >= 0,
                f"Budget tracking: ${summary['remaining_budget']:.2f} remaining"
            ))
            
        except ImportError as e:
            results.append(self.RunTest(
                "Student Protection Import",
                lambda: False,
                f"Failed to import student protection modules: {e}"
            ))
        
        return results
    
    def TestPDFAccess(self) -> List[Dict]:
        """Test PDF serving functionality"""
        results = []
        
        # Get a sample book for PDF testing
        books_response = self.MakeAPICall("/books?limit=1")
        if books_response.status_code == 200:
            books_data = books_response.json()
            if books_data.get('books'):
                sample_book_id = books_data['books'][0]['id']
                
                # Test 1: PDF Endpoint Exists
                pdf_response = self.MakeAPICall(f"/books/{sample_book_id}/pdf")
                results.append(self.RunTest(
                    "PDF Endpoint Accessible",
                    lambda: pdf_response.status_code in [200, 404, 302],  # 200=served, 404=not found, 302=redirect
                    f"PDF endpoint responding with status {pdf_response.status_code}"
                ))
                
                # Test 2: Content-Type Header
                if pdf_response.status_code == 200:
                    content_type = pdf_response.headers.get('Content-Type', '')
                    results.append(self.RunTest(
                        "PDF Content Type",
                        lambda: 'application/pdf' in content_type,
                        f"Correct content type returned: {content_type}"
                    ))
                
                # Test 3: Content-Disposition Header (should be inline)
                if pdf_response.status_code == 200:
                    disposition = pdf_response.headers.get('Content-Disposition', '')
                    results.append(self.RunTest(
                        "PDF Inline Viewing",
                        lambda: 'inline' in disposition,
                        "PDF set for inline viewing (not download)"
                    ))
        
        return results
    
    def TestSearchFiltering(self) -> List[Dict]:
        """Test search and filtering functionality"""
        results = []
        
        # Test 1: Title Search
        search_response = self.MakeAPICall("/books?search=python")
        results.append(self.RunTest(
            "Title Search Functionality",
            lambda: search_response.status_code == 200 and len(search_response.json().get('books', [])) > 0,
            "Title search returning relevant results"
        ))
        
        # Test 2: Category Filtering
        categories_response = self.MakeAPICall("/categories")
        if categories_response.status_code == 200:
            categories = categories_response.json().get('categories', [])
            if categories:
                sample_category = categories[0]['category']
                filter_response = self.MakeAPICall(f"/books?category={sample_category}")
                results.append(self.RunTest(
                    "Category Filtering",
                    lambda: filter_response.status_code == 200,
                    f"Category filtering working for: {sample_category}"
                ))
        
        # Test 3: Subject Filtering
        subjects_response = self.MakeAPICall("/subjects")
        if subjects_response.status_code == 200:
            subjects = subjects_response.json().get('subjects', [])
            if subjects:
                sample_subject = subjects[0]['subject']
                filter_response = self.MakeAPICall(f"/books?subject={sample_subject}")
                results.append(self.RunTest(
                    "Subject Filtering",
                    lambda: filter_response.status_code == 200,
                    f"Subject filtering working for: {sample_subject}"
                ))
        
        # Test 4: Pagination
        paginated_response = self.MakeAPICall("/books?limit=10&offset=5")
        results.append(self.RunTest(
            "Pagination Functionality",
            lambda: paginated_response.status_code == 200,
            "Pagination parameters accepted"
        ))
        
        # Test 5: Combined Filters
        combined_response = self.MakeAPICall("/books?search=math&limit=5")
        results.append(self.RunTest(
            "Combined Search and Pagination",
            lambda: combined_response.status_code == 200,
            "Combined search and pagination working"
        ))
        
        return results
    
    def TestGoogleDriveIntegration(self) -> List[Dict]:
        """Test Google Drive integration components"""
        results = []
        
        # Test 1: Google API Libraries Available
        try:
            import google.auth
            import googleapiclient.discovery
            results.append(self.RunTest(
                "Google API Libraries",
                lambda: True,
                "Google API libraries properly installed"
            ))
        except ImportError:
            results.append(self.RunTest(
                "Google API Libraries",
                lambda: False,
                "Google API libraries not available"
            ))
        
        # Test 2: Credentials File Exists
        creds_path = "Config/google_credentials.json"
        results.append(self.RunTest(
            "Google Credentials File",
            lambda: os.path.exists(creds_path),
            f"Credentials file found at {creds_path}"
        ))
        
        # Test 3: Token File Exists (may be placeholder)
        token_path = "Config/google_token.json"
        results.append(self.RunTest(
            "Google Token File",
            lambda: os.path.exists(token_path),
            f"Token file found at {token_path}"
        ))
        
        # Test 4: Student Google Drive API Import
        try:
            from Source.Core.StudentGoogleDriveAPI import StudentGoogleDriveAPI, GOOGLE_AVAILABLE
            results.append(self.RunTest(
                "StudentGoogleDriveAPI Import",
                lambda: GOOGLE_AVAILABLE,
                "StudentGoogleDriveAPI module available"
            ))
            
            # Test 5: API Initialization
            if GOOGLE_AVAILABLE:
                try:
                    api = StudentGoogleDriveAPI()
                    results.append(self.RunTest(
                        "Google Drive API Initialization",
                        lambda: api is not None,
                        "StudentGoogleDriveAPI initialized successfully"
                    ))
                except Exception as e:
                    results.append(self.RunTest(
                        "Google Drive API Initialization",
                        lambda: False,
                        f"Failed to initialize: {e}"
                    ))
        
        except ImportError as e:
            results.append(self.RunTest(
                "StudentGoogleDriveAPI Import",
                lambda: False,
                f"Import failed: {e}"
            ))
        
        return results
    
    def TestPerformance(self) -> List[Dict]:
        """Test performance benchmarks"""
        results = []
        
        # Test 1: Book List Response Time
        start_time = time.time()
        response = self.MakeAPICall("/books?limit=50")
        response_time = time.time() - start_time
        
        results.append(self.RunTest(
            "Book List Response Time",
            lambda: response_time < 2.0 and response.status_code == 200,
            f"Books list loaded in {response_time:.3f}s (target: <2s)"
        ))
        
        # Test 2: Search Response Time
        start_time = time.time()
        search_response = self.MakeAPICall("/books?search=programming")
        search_time = time.time() - start_time
        
        results.append(self.RunTest(
            "Search Response Time",
            lambda: search_time < 1.0 and search_response.status_code == 200,
            f"Search completed in {search_time:.3f}s (target: <1s)"
        ))
        
        # Test 3: Database Query Performance
        try:
            conn = sqlite3.connect(self.database_path)
            start_time = time.time()
            cursor = conn.execute("SELECT COUNT(*) FROM books WHERE title LIKE '%python%'")
            cursor.fetchone()
            query_time = time.time() - start_time
            conn.close()
            
            results.append(self.RunTest(
                "Database Query Performance",
                lambda: query_time < 0.5,
                f"Database search query in {query_time:.3f}s (target: <0.5s)"
            ))
        except Exception as e:
            results.append(self.RunTest(
                "Database Query Performance",
                lambda: False,
                f"Database query failed: {e}"
            ))
        
        return results
    
    def TestErrorHandling(self) -> List[Dict]:
        """Test error handling and edge cases"""
        results = []
        
        # Test 1: Invalid Book ID
        invalid_response = self.MakeAPICall("/books/999999")
        results.append(self.RunTest(
            "Invalid Book ID Handling",
            lambda: invalid_response.status_code == 404,
            "Properly returns 404 for non-existent books"
        ))
        
        # Test 2: Invalid Search Parameters
        invalid_search = self.MakeAPICall("/books?limit=-1")
        results.append(self.RunTest(
            "Invalid Search Parameters",
            lambda: invalid_search.status_code in [200, 400],  # Should handle gracefully
            "Handles invalid search parameters gracefully"
        ))
        
        # Test 3: Malformed Requests
        malformed_response = self.MakeAPICall("/books/not_a_number")
        results.append(self.RunTest(
            "Malformed Request Handling",
            lambda: malformed_response.status_code in [400, 422],
            "Properly handles malformed requests"
        ))
        
        return results
    
    def TestSecurity(self) -> List[Dict]:
        """Test basic security measures"""
        results = []
        
        # Test 1: SQL Injection Protection
        injection_attempt = self.MakeAPICall("/books?search='; DROP TABLE books; --")
        results.append(self.RunTest(
            "SQL Injection Protection",
            lambda: injection_attempt.status_code == 200,  # Should handle safely
            "Handles potential SQL injection attempts"
        ))
        
        # Test 2: Response Headers
        response = self.MakeAPICall("/books")
        headers = response.headers
        
        results.append(self.RunTest(
            "Security Headers Present",
            lambda: any('cors' in key.lower() or 'cache' in key.lower() for key in headers.keys()),
            "Security-related headers present in responses"
        ))
        
        return results
    
    def MakeAPICall(self, endpoint: str, timeout: int = 10) -> requests.Response:
        """Make API call with error handling"""
        try:
            url = f"{self.api_base}{endpoint}"
            response = requests.get(url, timeout=timeout)
            return response
        except requests.exceptions.RequestException as e:
            # Create a mock response for failed requests
            class MockResponse:
                def __init__(self, status_code=500, error_message=""):
                    self.status_code = status_code
                    self.error_message = error_message
                    self.headers = {}
                
                def json(self):
                    return {"error": self.error_message}
            
            return MockResponse(500, str(e))
    
    def RunTest(self, test_name: str, test_function, expected_message: str) -> Dict:
        """Execute individual test and record results"""
        try:
            success = test_function()
            status = "PASS" if success else "FAIL"
            message = expected_message if success else f"Failed: {expected_message}"
            
            result = {
                'test': test_name,
                'status': status,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"  {'✅' if success else '❌'} {test_name}: {message}")
            return result
            
        except Exception as e:
            result = {
                'test': test_name,
                'status': 'ERROR',
                'message': f"Test error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"  ⚠️ {test_name}: Test error - {e}")
            return result
    
    def GenerateTestReport(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("🧪 PROJECT HIMALAYA TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed_tests = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        error_tests = sum(1 for r in self.test_results if r['status'] == 'ERROR')
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️ Errors: {error_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Show failures and errors
        if failed_tests > 0 or error_tests > 0:
            print(f"\n⚠️ ISSUES FOUND:")
            for result in self.test_results:
                if result['status'] in ['FAIL', 'ERROR']:
                    print(f"   {result['status']}: {result['test']} - {result['message']}")
        
        # Overall assessment
        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! PROJECT HIMALAYA IS READY!")
        elif passed_tests / total_tests >= 0.90:
            print(f"\n✅ EXCELLENT! {(passed_tests/total_tests)*100:.1f}% success rate - ready for deployment")
        elif passed_tests / total_tests >= 0.75:
            print(f"\n⚠️ GOOD: {(passed_tests/total_tests)*100:.1f}% success rate - minor issues to address")
        else:
            print(f"\n❌ NEEDS WORK: {(passed_tests/total_tests)*100:.1f}% success rate - address failures before deployment")
        
        # Save detailed report
        report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'errors': error_tests,
                    'success_rate': (passed_tests/total_tests)*100,
                    'timestamp': datetime.now().isoformat()
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_filename}")
        print("=" * 60)

if __name__ == "__main__":
    print("🚀 Starting PROJECT HIMALAYA Comprehensive Test Suite...")
    print("⚠️ Make sure AndyLibrary server is running before starting tests!")
    
    # Give user a chance to start the server
    try:
        input("Press Enter when AndyLibrary server is running (Ctrl+C to cancel)...")
    except KeyboardInterrupt:
        print("\n❌ Tests cancelled by user")
        sys.exit(1)
    
    # Run comprehensive tests
    test_suite = ProjectHimalayaTestSuite()
    test_suite.RunAllTests()
    
    print("\n🎯 Testing complete! Check the detailed report for full results.")
    print("Ready for the next phase of PROJECT HIMALAYA! 🏔️✨")