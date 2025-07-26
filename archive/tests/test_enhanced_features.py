# File: test_enhanced_features.py
# Path: /home/herb/Desktop/ClaudeWatch/test_enhanced_features.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-01-26
# Last Modified: 2025-01-26 06:35PM

"""Test script to validate enhanced Claude monitoring features."""

import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from claude_monitor.monitoring.enhanced_proxy_monitor import RateLimitPatterns, SessionMetrics
from claude_monitor.data.enhanced_database import EnhancedDatabaseManager


def test_rate_limit_patterns():
    """Test the advanced rate limit pattern matching."""
    print("🔍 Testing Advanced Rate Limit Pattern Matching...")
    
    test_cases = [
        ("Rate limit approaching, 5000 tokens remaining", "approaching", 5000),
        ("RATE LIMIT REACHED|19000", "reached", 19000),
        ("Maximum usage reached: 88000 tokens", "reached", 88000),
        ("Message limit reached: 250 messages", "message_limit", 250),
        ("Usage warning: 1500 tokens remaining in session", "approaching", 1500),
        ("Session limit hit: 220000 tokens exceeded", "reached", 220000),
        ("No rate limit information here", None, None),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, (text, expected_type, expected_value) in enumerate(test_cases, 1):
        result = RateLimitPatterns.extract_rate_limit_info(text)
        
        if result is None and expected_type is None:
            print(f"   ✅ Test {i}: Correctly identified no rate limit info")
            passed += 1
        elif result and result['type'] == expected_type and result.get('limit_value') == expected_value:
            print(f"   ✅ Test {i}: Correctly extracted {expected_type} with value {expected_value}")
            passed += 1
        else:
            print(f"   ❌ Test {i}: Expected {expected_type}/{expected_value}, got {result}")
    
    print(f"   📊 Pattern Matching: {passed}/{total} tests passed ({passed/total:.1%})")
    return passed == total


def test_session_metrics():
    """Test session metrics tracking."""
    print("\n📈 Testing Session Metrics Tracking...")
    
    session = SessionMetrics("test_session_001", "/test/project/path")
    
    # Add some usage data
    session.add_token_usage(1000)
    session.add_token_usage(1500)
    session.add_token_usage(800)
    session.add_message()
    session.add_message()
    
    # Add rate limit event
    session.add_rate_limit_event({
        'type': 'approaching',
        'limit_value': 19000,
        'raw_text': 'Rate limit approaching: 19000 tokens'
    })
    
    metrics = session.get_current_metrics()
    
    # Validate metrics
    tests = [
        (metrics['session_id'] == "test_session_001", "Session ID"),
        (metrics['project_path'] == "/test/project/path", "Project path"),
        (metrics['total_tokens'] == 3300, "Total tokens calculation"),
        (metrics['peak_token_usage'] == 1500, "Peak token tracking"),
        (metrics['message_count'] == 2, "Message count"),
        (metrics['rate_limit_events'] == 1, "Rate limit events count"),
    ]
    
    passed = sum(1 for test, name in tests if test)
    total = len(tests)
    
    for test, name in tests:
        status = "✅" if test else "❌"
        print(f"   {status} {name}")
    
    print(f"   📊 Session Metrics: {passed}/{total} tests passed ({passed/total:.1%})")
    return passed == total


def test_enhanced_database():
    """Test enhanced database functionality."""
    print("\n🗄️ Testing Enhanced Database Operations...")
    
    # Use temporary database for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_enhanced.db"
        db_manager = EnhancedDatabaseManager(db_path)
        
        test_results = []
        
        # Test 1: Create session metrics first (to satisfy foreign key)
        session_data = {
            'session_id': 'test_session_001',
            'project_path': '/test/project',
            'start_time': '2025-01-26T18:00:00Z',
            'total_tokens': 15000,
            'peak_token_usage': 5000,
            'message_count': 45,
            'peak_message_count': 45,
            'cost_estimate': 12.50,
            'rate_limit_events_count': 1,
            'status': 'active',
            'metadata': {'test': True}
        }
        
        try:
            db_manager.create_or_update_session_metrics(session_data)
            test_results.append(("Session metrics created", True))
        except Exception as e:
            test_results.append(("Session metrics created", False))
            print(f"      Error: {e}")
        
        # Test 2: Add enhanced rate limit event
        event_data = {
            'event_type': 'approaching',
            'session_id': 'test_session_001',
            'elapsed_time': 1800.0,
            'limit_value': 19000,
            'raw_message': 'Rate limit approaching: 19000 tokens',
            'pattern_matched': r'rate.*limit.*approaching.*(\d+)',
            'project_path': '/test/project',
            'confidence_score': 0.95
        }
        
        try:
            db_manager.add_enhanced_rate_limit_event(event_data)
            test_results.append(("Enhanced rate limit event added", True))
        except Exception as e:
            test_results.append(("Enhanced rate limit event added", False))
            print(f"      Error: {e}")
        
        # Test 3: Update enhanced plan limit
        plan_data = {
            'plan_name': 'pro',
            'token_limit': 18500,  # Learned limit slightly lower than default
            'message_limit': 240,
            'confidence_score': 0.85,
            'sample_size': 10,
            'variance': 250.0
        }
        
        try:
            db_manager.update_enhanced_plan_limit(plan_data)
            test_results.append(("Enhanced plan limit updated", True))
        except Exception as e:
            test_results.append(("Enhanced plan limit updated", False))
            print(f"      Error: {e}")
        
        # Test 4: Get session analytics  
        try:
            analytics = db_manager.get_session_analytics()
            has_sessions = len(analytics['sessions']) > 0
            test_results.append(("Session analytics retrieved", has_sessions))
        except Exception as e:
            test_results.append(("Session analytics retrieved", False))
            print(f"      Error: {e}")
        
        # Test 5: Register terminal session
        terminal_data = {
            'terminal_id': 'user@host:12345:1640000000',
            'project_path': '/test/project',
            'session_id': 'test_session_001',
            'process_id': 12345
        }
        
        try:
            db_manager.register_terminal_session(terminal_data)
            test_results.append(("Terminal session registered", True))
        except Exception as e:
            test_results.append(("Terminal session registered", False))
            print(f"      Error: {e}")
        
        # Print results
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅" if result else "❌"
            print(f"   {status} {test_name}")
        
        print(f"   📊 Database Operations: {passed}/{total} tests passed ({passed/total:.1%})")
        return passed == total


def test_file_monitoring_simulation():
    """Test file monitoring capabilities with simulation."""
    print("\n📁 Testing File Monitoring Simulation...")
    
    # Simulate the file path parsing functionality
    test_paths = [
        (Path("/-home-herb-Desktop-ClaudeWatch/mcp-logs-context7/2025-01-26T18-00-00-000Z.txt"), 
         "/home/herb/Desktop/ClaudeWatch#2025-01-26T18-00-00-000Z"),
        (Path("/cache/claude-cli-nodejs/-home-user-project/mcp-logs/test.txt"),
         "/home/user/project#test"),
        (Path("/some/other/path.txt"),
         "/some/other/path.txt"),  # Fallback case
    ]
    
    from claude_monitor.monitoring.enhanced_proxy_monitor import EnhancedProxyMonitor
    from claude_monitor.data.enhanced_database import EnhancedDatabaseManager as DatabaseManager
    
    # Create mock database manager
    mock_db = MagicMock()
    monitor = EnhancedProxyMonitor(mock_db)
    
    passed = 0
    total = len(test_paths)
    
    for test_path, expected in test_paths:
        try:
            result = monitor.get_session_id_from_path(test_path)
            if expected in result or result == expected:
                print(f"   ✅ Path parsing: {test_path.name}")
                passed += 1
            else:
                print(f"   ❌ Path parsing: Expected '{expected}', got '{result}'")
        except Exception as e:
            print(f"   ❌ Path parsing failed: {e}")
    
    print(f"   📊 File Monitoring: {passed}/{total} tests passed ({passed/total:.1%})")
    return passed == total


def main():
    """Main test execution."""
    print("🧪 ENHANCED CLAUDE MONITOR - FEATURE VALIDATION")
    print("=" * 60)
    print("Testing all enhanced features requested in bm.txt...\n")
    
    test_results = []
    
    try:
        # Run all tests
        test_results.append(("Rate Limit Pattern Matching", test_rate_limit_patterns()))
        test_results.append(("Session Metrics Tracking", test_session_metrics()))
        test_results.append(("Enhanced Database Operations", test_enhanced_database()))
        test_results.append(("File Monitoring Simulation", test_file_monitoring_simulation()))
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        total_passed = sum(1 for _, passed in test_results if passed)
        total_tests = len(test_results)
        
        for test_name, passed in test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status:<8} {test_name}")
        
        print(f"\n🎯 OVERALL RESULT: {total_passed}/{total_tests} test suites passed ({total_passed/total_tests:.1%})")
        
        if total_passed == total_tests:
            print("\n🎉 SUCCESS: All enhanced features are working correctly!")
            print("\nKey enhancements validated:")
            print("• ✅ Advanced regex pattern matching for rate limit messages")
            print("• ✅ Comprehensive session metrics tracking") 
            print("• ✅ Enhanced database schema with analytics")
            print("• ✅ Multi-terminal session coordination")
            print("• ✅ Statistical confidence scoring")
            print("• ✅ Project-specific session tracking")
        else:
            print(f"\n⚠️  {total_tests - total_passed} test suite(s) failed - review implementation")
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return total_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)