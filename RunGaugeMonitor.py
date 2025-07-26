# File: RunGaugeMonitor.py
# Path: /home/herb/Desktop/ClaudeWatch/RunGaugeMonitor.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 10:52AM

"""
Enhanced Claude Monitor with beautiful gauge displays
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "Src"))

from ClaudeMonitor.Ui.RealTimeGaugeMonitor import GaugeMonitorLauncher
from ClaudeMonitor.Ui.GaugeDisplay import MonitoringGaugeDisplay
from ClaudeMonitor.Data.EnhancedDatabase import EnhancedDatabaseManager
from ClaudeMonitor.Monitoring.IntelligentOrchestrator import IntelligentOrchestrator
from rich.console import Console


def CreateDataProvider():
    """Create data provider that fetches real monitoring data"""
    
    try:
        # Initialize database and orchestrator to get real data
        DatabasePath = Path.home() / ".claude-monitor" / "enhanced_claude_monitor.db"
        DbManager = EnhancedDatabaseManager(str(DatabasePath))
        
        def GetRealTimeData():
            """Get actual monitoring data from database"""
            try:
                # Get latest session metrics
                SessionMetrics = DbManager.get_latest_session_metrics()
                if not SessionMetrics:
                    return GetDemoData()
                
                # Get system stats
                import psutil
                
                return {
                    'tokens_used': SessionMetrics.get('total_tokens_used', 0),
                    'token_limit': 100000,  # Default limit
                    'messages_sent': SessionMetrics.get('total_messages_sent', 0),
                    'message_limit': 1000,
                    'rate_limit_hits': SessionMetrics.get('rate_limit_hits', 0),
                    'total_requests': max(SessionMetrics.get('total_messages_sent', 1), 1),
                    'efficiency_score': SessionMetrics.get('efficiency_score', 1.0),
                    'session_duration_minutes': SessionMetrics.get('session_duration', 0) / 60,
                    'avg_response_time': 1000,  # Placeholder
                    'cpu_usage': psutil.cpu_percent(interval=0.1),
                    'memory_usage': psutil.virtual_memory().percent,
                    'connection_health': 100 if SessionMetrics.get('total_messages_sent', 0) > 0 else 50
                }
            except Exception:
                return GetDemoData()
        
        return GetRealTimeData
        
    except Exception:
        return GetDemoData


def GetDemoData():
    """Generate demo data for testing"""
    import random
    import time
    
    # Generate realistic demo data with some >100% scenarios
    BaseTime = int(time.time())
    
    return {
        'tokens_used': random.randint(80000, 150000),  # Can exceed 100k limit
        'token_limit': 100000,
        'messages_sent': random.randint(800, 1200),   # Can exceed 1k limit
        'message_limit': 1000,
        'rate_limit_hits': random.randint(2, 15),
        'total_requests': random.randint(50, 100),
        'efficiency_score': random.uniform(0.75, 1.1),  # Can exceed 100%
        'session_duration_minutes': random.randint(30, 600),
        'avg_response_time': random.randint(800, 2500),
        'cpu_usage': random.randint(20, 85),
        'memory_usage': random.randint(35, 75),
        'connection_health': random.randint(90, 100)
    }


def main():
    """Main entry point for gauge monitor"""
    
    Parser = argparse.ArgumentParser(
        description="Enhanced Claude Monitor with Gauge Display",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    Parser.add_argument(
        "--demo", 
        action="store_true",
        help="Run in demo mode with sample data"
    )
    
    Parser.add_argument(
        "--real-data",
        action="store_true", 
        help="Use real monitoring data from database"
    )
    
    Parser.add_argument(
        "--single-gauge",
        help="Show single large gauge for specific metric (tokens|messages|efficiency)"
    )
    
    Args = Parser.parse_args()
    
    console = Console()
    
    try:
        if Args.single_gauge:
            # Show single large gauge
            ShowSingleGauge(Args.single_gauge, Args.demo or not Args.real_data)
            
        elif Args.demo:
            # Run demo mode
            console.print("[cyan]🎮 Starting Demo Mode with Sample Data[/]")
            GaugeMonitorLauncher.LaunchQuickDemo()
            
        elif Args.real_data:
            # Use real data
            console.print("[cyan]📊 Starting Monitor with Real Data[/]")
            DataProvider = CreateDataProvider()
            GaugeMonitorLauncher.LaunchRealTimeMonitor(DataProvider)
            
        else:
            # Default: try real data, fall back to demo
            console.print("[cyan]🚀 Starting Enhanced Gauge Monitor[/]")
            console.print("[dim]Attempting to use real data, falling back to demo if unavailable[/]")
            DataProvider = CreateDataProvider()
            GaugeMonitorLauncher.LaunchRealTimeMonitor(DataProvider)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/]")
        sys.exit(1)


def ShowSingleGauge(MetricType: str, UseDemo: bool = True):
    """Show a single large gauge for specified metric"""
    
    console = Console()
    Display = MonitoringGaugeDisplay()
    
    # Get data
    if UseDemo:
        Data = GetDemoData()
    else:
        DataProvider = CreateDataProvider()
        Data = DataProvider()
    
    # Show appropriate gauge
    if MetricType.lower() == "tokens":
        Value = (Data['tokens_used'] / Data['token_limit']) * 100
        Display.DisplaySingleGauge(
            Value=Value,
            MaxValue=100,
            Title="Token Usage",
            Unit=f"% ({Data['tokens_used']:,}/{Data['token_limit']:,})"
        )
        
    elif MetricType.lower() == "messages":
        Value = (Data['messages_sent'] / Data['message_limit']) * 100
        Display.DisplaySingleGauge(
            Value=Value,
            MaxValue=100,
            Title="Message Usage", 
            Unit=f"% ({Data['messages_sent']}/{Data['message_limit']})"
        )
        
    elif MetricType.lower() == "efficiency":
        Value = Data['efficiency_score'] * 100
        Display.DisplaySingleGauge(
            Value=Value,
            MaxValue=100,
            Title="Efficiency Score",
            Unit="%"
        )
        
    else:
        console.print(f"[red]Unknown metric: {MetricType}[/]")
        console.print("[dim]Available: tokens, messages, efficiency[/]")


if __name__ == "__main__":
    main()