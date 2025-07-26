# File: RealTimeGaugeMonitor.py
# Path: /home/herb/Desktop/ClaudeWatch/src/claude_monitor/ui/RealTimeGaugeMonitor.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 07:58AM

"""
Real-time gauge monitoring with live updates and >100% capability
"""

import time
import threading
from typing import Dict, Optional, Callable
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from datetime import datetime, timedelta
import psutil
import os

from .GaugeDisplay import MonitoringGaugeDisplay, LiveGaugeUpdater


class RealTimeGaugeMonitor:
    """Real-time monitoring with beautiful gauge displays"""
    
    def __init__(self, DataProvider: Optional[Callable] = None):
        self.Console = Console()
        self.GaugeDisplay = MonitoringGaugeDisplay()
        self.LiveUpdater = LiveGaugeUpdater()
        self.DataProvider = DataProvider
        self.Running = False
        self.UpdateThread = None
        self.UpdateInterval = 2.0  # seconds
        self.LastUpdate = datetime.now()
        
    def StartMonitoring(self) -> None:
        """Start real-time gauge monitoring"""
        
        self.Running = True
        
        try:
            with Live(self._CreateInitialLayout(), refresh_per_second=1, console=self.Console) as live:
                while self.Running:
                    try:
                        # Get fresh metrics
                        Metrics = self._GetCurrentMetrics()
                        
                        # Create updated layout
                        UpdatedLayout = self._CreateLiveLayout(Metrics)
                        live.update(UpdatedLayout)
                        
                        time.sleep(self.UpdateInterval)
                        
                    except KeyboardInterrupt:
                        self.StopMonitoring()
                        break
                    except Exception as e:
                        # Show error in display but continue
                        ErrorLayout = self._CreateErrorLayout(str(e))
                        live.update(ErrorLayout)
                        time.sleep(self.UpdateInterval)
                        
        except KeyboardInterrupt:
            self.StopMonitoring()
            
    def StopMonitoring(self) -> None:
        """Stop monitoring"""
        self.Running = False
        self.Console.print("\n[yellow]Monitoring stopped by user[/]")
        
    def _CreateInitialLayout(self) -> Layout:
        """Create initial layout for monitoring"""
        
        InitialMetrics = {
            'tokens_used': 0,
            'token_limit': 100000,
            'messages_sent': 0,
            'message_limit': 1000,
            'rate_limit_hits': 0,
            'total_requests': 1,
            'efficiency_score': 1.0,
            'session_duration_minutes': 0,
            'avg_response_time': 0,
            'cpu_usage': 0,
            'memory_usage': 0,
            'connection_health': 100
        }
        
        return self._CreateLiveLayout(InitialMetrics)
        
    def _CreateLiveLayout(self, Metrics: Dict) -> Layout:
        """Create live updating layout with gauges"""
        
        # Main layout
        MainLayout = Layout()
        MainLayout.split_column(
            Layout(name="header", size=3),
            Layout(name="content", ratio=1),
            Layout(name="footer", size=3)
        )
        
        # Header with title and timestamp
        HeaderPanel = Panel(
            Align.center(f"[bold cyan]🚀 Enhanced Claude Monitor - Live Gauges[/]\n" +
                        f"[dim]Last Updated: {datetime.now().strftime('%H:%M:%S')}[/]"),
            style="cyan"
        )
        MainLayout["header"].update(HeaderPanel)
        
        # Content with gauges
        ContentLayout = Layout()
        ContentLayout.split_row(
            Layout(name="usage", ratio=1),
            Layout(name="performance", ratio=1),
            Layout(name="health", ratio=1)
        )
        
        # Create gauge panels
        UsageGauges = self._PrepareUsageGauges(Metrics)
        PerformanceGauges = self._PreparePerformanceGauges(Metrics)
        HealthGauges = self._PrepareHealthGauges(Metrics)
        
        ContentLayout["usage"].update(
            self.GaugeDisplay.GaugeRenderer.CreateGaugePanel(UsageGauges, "📊 Usage Metrics")
        )
        ContentLayout["performance"].update(
            self.GaugeDisplay.GaugeRenderer.CreateGaugePanel(PerformanceGauges, "⚡ Performance")
        )
        ContentLayout["health"].update(
            self.GaugeDisplay.GaugeRenderer.CreateGaugePanel(HealthGauges, "🔧 System Health")
        )
        
        MainLayout["content"].update(ContentLayout)
        
        # Footer with controls
        FooterPanel = Panel(
            Align.center("[dim]Press Ctrl+C to stop monitoring | Update interval: 2s[/]"),
            style="dim"
        )
        MainLayout["footer"].update(FooterPanel)
        
        return MainLayout
        
    def _CreateErrorLayout(self, ErrorMessage: str) -> Layout:
        """Create error display layout"""
        
        ErrorLayout = Layout()
        ErrorPanel = Panel(
            Align.center(f"[red]Error: {ErrorMessage}[/]\n[dim]Retrying...[/]"),
            title="[red]Error[/]",
            style="red"
        )
        ErrorLayout.update(ErrorPanel)
        return ErrorLayout
        
    def _GetCurrentMetrics(self) -> Dict:
        """Get current metrics from data provider or generate sample data"""
        
        if self.DataProvider:
            try:
                return self.DataProvider()
            except Exception:
                pass
                
        # Generate sample/demo metrics with some >100% values for testing
        CurrentTime = datetime.now()
        ElapsedMinutes = (CurrentTime - self.LastUpdate).total_seconds() / 60
        
        # Simulate some dynamic metrics
        import random
        
        Metrics = {
            'tokens_used': random.randint(80000, 120000),  # Can exceed limit
            'token_limit': 100000,
            'messages_sent': random.randint(800, 1200),   # Can exceed limit  
            'message_limit': 1000,
            'rate_limit_hits': random.randint(0, 25),
            'total_requests': random.randint(80, 120),
            'efficiency_score': random.uniform(0.7, 0.95),
            'session_duration_minutes': ElapsedMinutes + random.randint(0, 60),
            'avg_response_time': random.randint(800, 2500),
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'connection_health': random.randint(85, 100)
        }
        
        return Metrics
        
    def _PrepareUsageGauges(self, MetricsData: Dict) -> Dict:
        """Prepare usage-related gauges with >100% support"""
        
        TokenUsage = MetricsData.get('tokens_used', 0)
        TokenLimit = MetricsData.get('token_limit', 100000)
        TokenPercentage = (TokenUsage / TokenLimit * 100) if TokenLimit > 0 else 0
        
        MessageUsage = MetricsData.get('messages_sent', 0)
        MessageLimit = MetricsData.get('message_limit', 1000)
        MessagePercentage = (MessageUsage / MessageLimit * 100) if MessageLimit > 0 else 0
        
        RateLimitRate = (MetricsData.get('rate_limit_hits', 0) / 
                        max(MetricsData.get('total_requests', 1), 1)) * 100
        
        return {
            "Token Usage": {
                'value': TokenPercentage,
                'max': 100,
                'unit': f'% ({TokenUsage:,}/{TokenLimit:,})'
            },
            "Message Count": {
                'value': MessagePercentage,
                'max': 100,
                'unit': f'% ({MessageUsage}/{MessageLimit})'
            },
            "Rate Limit Rate": {
                'value': RateLimitRate,
                'max': 100,
                'unit': f'% ({MetricsData.get("rate_limit_hits", 0)} hits)'
            }
        }
        
    def _PreparePerformanceGauges(self, MetricsData: Dict) -> Dict:
        """Prepare performance gauges"""
        
        EfficiencyScore = MetricsData.get('efficiency_score', 0) * 100
        SessionDuration = MetricsData.get('session_duration_minutes', 0)
        ResponseTime = MetricsData.get('avg_response_time', 0)
        
        # Performance can exceed 100% (super-efficient)
        return {
            "Efficiency Score": {
                'value': EfficiencyScore,
                'max': 100,
                'unit': '%'
            },
            "Session Time": {
                'value': (SessionDuration / 480) * 100,  # % of 8 hours
                'max': 100,
                'unit': f'% ({SessionDuration:.0f}min)'
            },
            "Response Time": {
                'value': (ResponseTime / 5000) * 100,  # % of 5 second max
                'max': 100,
                'unit': f'% ({ResponseTime:.0f}ms)'
            }
        }
        
    def _PrepareHealthGauges(self, MetricsData: Dict) -> Dict:
        """Prepare system health gauges"""
        
        return {
            "CPU Usage": {
                'value': MetricsData.get('cpu_usage', 0),
                'max': 100,
                'unit': '%'
            },
            "Memory Usage": {
                'value': MetricsData.get('memory_usage', 0),
                'max': 100,
                'unit': '%'
            },
            "Connection Health": {
                'value': MetricsData.get('connection_health', 100),
                'max': 100,
                'unit': '%'
            }
        }


class GaugeMonitorLauncher:
    """Launcher for gauge-based monitoring"""
    
    @staticmethod
    def LaunchRealTimeMonitor(DataProvider: Optional[Callable] = None) -> None:
        """Launch real-time gauge monitoring"""
        
        Console = Console()
        
        try:
            Console.print("[cyan]🚀 Starting Enhanced Gauge Monitor...[/]")
            
            Monitor = RealTimeGaugeMonitor(DataProvider)
            Monitor.StartMonitoring()
            
        except KeyboardInterrupt:
            Console.print("\n[yellow]Monitoring stopped by user[/]")
        except Exception as e:
            Console.print(f"[red]Error starting monitor: {e}[/]")
    
    @staticmethod
    def LaunchQuickDemo() -> None:
        """Launch demo with sample data"""
        
        def SampleDataProvider():
            """Generate sample data for demo"""
            import random
            return {
                'tokens_used': random.randint(75000, 125000),  # >100% possible
                'token_limit': 100000,
                'messages_sent': random.randint(900, 1100),   # >100% possible
                'message_limit': 1000,
                'rate_limit_hits': random.randint(5, 20),
                'total_requests': random.randint(80, 150),
                'efficiency_score': random.uniform(0.75, 1.05),  # >100% possible
                'session_duration_minutes': random.randint(30, 300),
                'avg_response_time': random.randint(500, 3000),
                'cpu_usage': random.randint(20, 80),
                'memory_usage': random.randint(40, 90),
                'connection_health': random.randint(90, 100)
            }
        
        GaugeMonitorLauncher.LaunchRealTimeMonitor(SampleDataProvider)


# Test the gauge system
if __name__ == "__main__":
    # Launch demo
    GaugeMonitorLauncher.LaunchQuickDemo()