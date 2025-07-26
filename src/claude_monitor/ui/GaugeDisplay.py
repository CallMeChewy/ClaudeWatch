# File: GaugeDisplay.py
# Path: /home/herb/Desktop/ClaudeWatch/src/claude_monitor/ui/GaugeDisplay.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 07:57AM

"""
Enhanced gauge display system with color zones and >100% support
"""

from typing import Dict, List, Optional, Tuple, Union
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich.table import Table
import math


class GaugeRenderer:
    """Renders beautiful gauge displays with color zones"""
    
    def __init__(self, Console: Console):
        self.Console = Console
        self.ColorZones = {
            'green': {'min': 0, 'max': 70, 'color': 'green'},
            'yellow': {'min': 70, 'max': 90, 'color': 'yellow'},
            'red': {'min': 90, 'max': 100, 'color': 'red'},
            'critical': {'min': 100, 'max': float('inf'), 'color': 'bright_red'}
        }
    
    def CreateGauge(self, Value: float, MaxValue: float = 100.0, Title: str = "", 
                   Unit: str = "%", Width: int = 40, ShowValue: bool = True) -> str:
        """Create a single gauge with color zones"""
        
        # Calculate percentage (allow >100%)
        Percentage = min((Value / MaxValue) * 100, 150) if MaxValue > 0 else 0
        ActualPercentage = (Value / MaxValue) * 100 if MaxValue > 0 else 0
        
        # Determine color zone
        Color = self._GetColorForValue(ActualPercentage)
        
        # Create gauge bar
        FilledWidth = int((Percentage / 150) * Width)  # Scale to 150% max display
        EmptyWidth = Width - FilledWidth
        
        # Create gauge segments with zone colors
        GaugeBar = self._CreateColoredGaugeBar(FilledWidth, EmptyWidth, Width, ActualPercentage)
        
        # Create value display
        ValueText = f"{Value:.1f}{Unit}" if ShowValue else ""
        if ActualPercentage > 100:
            ValueText = f"[{Color}]{ValueText}[/]"
        else:
            ValueText = f"[{Color}]{ValueText}[/]"
        
        # Create title
        TitleText = f"[bold]{Title}[/]" if Title else ""
        
        return f"{TitleText}\n{GaugeBar} {ValueText}"
    
    def _CreateColoredGaugeBar(self, FilledWidth: int, EmptyWidth: int, 
                              TotalWidth: int, Percentage: float) -> str:
        """Create gauge bar with appropriate color zones"""
        
        # Define zone boundaries in terms of bar width
        GreenEnd = int(TotalWidth * 0.47)    # 0-70% = 47% of 150% scale
        YellowEnd = int(TotalWidth * 0.60)   # 70-90% = 13% more
        RedEnd = int(TotalWidth * 0.67)      # 90-100% = 7% more
        # 100%+ goes beyond RedEnd
        
        GaugeSegments = []
        
        for i in range(TotalWidth):
            if i < FilledWidth:
                if i < GreenEnd:
                    GaugeSegments.append("[green]█[/]")
                elif i < YellowEnd:
                    GaugeSegments.append("[yellow]█[/]")
                elif i < RedEnd:
                    GaugeSegments.append("[red]█[/]")
                else:  # >100%
                    GaugeSegments.append("[bright_red]█[/]")
            else:
                if i < GreenEnd:
                    GaugeSegments.append("[dim green]░[/]")
                elif i < YellowEnd:
                    GaugeSegments.append("[dim yellow]░[/]")
                elif i < RedEnd:
                    GaugeSegments.append("[dim red]░[/]")
                else:
                    GaugeSegments.append("[dim bright_red]░[/]")
        
        return "".join(GaugeSegments)
    
    def _GetColorForValue(self, Percentage: float) -> str:
        """Get color for value based on percentage"""
        if Percentage >= 100:
            return 'bright_red'
        elif Percentage >= 90:
            return 'red'
        elif Percentage >= 70:
            return 'yellow'
        else:
            return 'green'
    
    def CreateGaugePanel(self, GaugeData: Dict, Title: str = "System Metrics") -> Panel:
        """Create a panel with multiple gauges"""
        
        GaugeLines = []
        for GaugeName, Data in GaugeData.items():
            Value = Data.get('value', 0)
            MaxValue = Data.get('max', 100)
            Unit = Data.get('unit', '%')
            
            GaugeDisplay = self.CreateGauge(
                Value=Value,
                MaxValue=MaxValue,
                Title=GaugeName,
                Unit=Unit,
                Width=35
            )
            GaugeLines.append(GaugeDisplay)
            GaugeLines.append("")  # Spacing
        
        GaugeContent = "\n".join(GaugeLines[:-1])  # Remove last empty line
        
        return Panel(
            GaugeContent,
            title=f"[bold cyan]{Title}[/]",
            border_style="cyan",
            padding=(1, 2)
        )


class MonitoringGaugeDisplay:
    """Enhanced monitoring display with gauge-based metrics"""
    
    def __init__(self):
        self.Console = Console()
        self.GaugeRenderer = GaugeRenderer(self.Console)
        
    def DisplayMonitoringGauges(self, MetricsData: Dict) -> None:
        """Display comprehensive monitoring gauges"""
        
        # Extract metrics for gauge display
        UsageGauges = self._PrepareUsageGauges(MetricsData)
        PerformanceGauges = self._PreparePerformanceGauges(MetricsData)
        HealthGauges = self._PrepareHealthGauges(MetricsData)
        
        # Create layout with gauge panels
        Layout = self._CreateGaugeLayout(UsageGauges, PerformanceGauges, HealthGauges)
        
        # Display
        self.Console.clear()
        self.Console.print(Layout)
    
    def _PrepareUsageGauges(self, MetricsData: Dict) -> Dict:
        """Prepare usage-related gauges"""
        return {
            "Token Usage": {
                'value': MetricsData.get('tokens_used', 0),
                'max': MetricsData.get('token_limit', 100000),
                'unit': ' tokens'
            },
            "Message Count": {
                'value': MetricsData.get('messages_sent', 0),
                'max': MetricsData.get('message_limit', 1000),
                'unit': ' msgs'
            },
            "Rate Limit Usage": {
                'value': (MetricsData.get('rate_limit_hits', 0) / max(MetricsData.get('total_requests', 1), 1)) * 100,
                'max': 100,
                'unit': '%'
            }
        }
    
    def _PreparePerformanceGauges(self, MetricsData: Dict) -> Dict:
        """Prepare performance-related gauges"""
        return {
            "Efficiency Score": {
                'value': MetricsData.get('efficiency_score', 0) * 100,
                'max': 100,
                'unit': '%'
            },
            "Session Duration": {
                'value': MetricsData.get('session_duration_minutes', 0),
                'max': 480,  # 8 hours
                'unit': ' min'
            },
            "API Response Time": {
                'value': MetricsData.get('avg_response_time', 0),
                'max': 5000,  # 5 seconds
                'unit': ' ms'
            }
        }
    
    def _PrepareHealthGauges(self, MetricsData: Dict) -> Dict:
        """Prepare system health gauges"""
        return {
            "System Load": {
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
    
    def _CreateGaugeLayout(self, UsageGauges: Dict, PerformanceGauges: Dict, 
                          HealthGauges: Dict) -> Layout:
        """Create rich layout with gauge panels"""
        
        # Create gauge panels
        UsagePanel = self.GaugeRenderer.CreateGaugePanel(UsageGauges, "Usage Metrics")
        PerformancePanel = self.GaugeRenderer.CreateGaugePanel(PerformanceGauges, "Performance")
        HealthPanel = self.GaugeRenderer.CreateGaugePanel(HealthGauges, "System Health")
        
        # Create layout
        MainLayout = Layout()
        MainLayout.split_column(
            Layout(UsagePanel, name="usage"),
            Layout(PerformancePanel, name="performance"),
            Layout(HealthPanel, name="health")
        )
        
        return MainLayout
    
    def DisplaySingleGauge(self, Value: float, MaxValue: float, Title: str, 
                          Unit: str = "%") -> None:
        """Display a single large gauge"""
        
        GaugeDisplay = self.GaugeRenderer.CreateGauge(
            Value=Value,
            MaxValue=MaxValue,
            Title=Title,
            Unit=Unit,
            Width=60,
            ShowValue=True
        )
        
        GaugePanel = Panel(
            Align.center(GaugeDisplay),
            title=f"[bold cyan]{Title}[/]",
            border_style="cyan",
            padding=(2, 4)
        )
        
        self.Console.print(GaugePanel)


class LiveGaugeUpdater:
    """Handles live updating of gauge displays"""
    
    def __init__(self):
        self.Display = MonitoringGaugeDisplay()
        self.LastMetrics = {}
    
    def UpdateGauges(self, NewMetrics: Dict) -> None:
        """Update gauges with new metrics data"""
        
        # Check if significant change to avoid flicker
        if self._ShouldUpdate(NewMetrics):
            self.Display.DisplayMonitoringGauges(NewMetrics)
            self.LastMetrics = NewMetrics.copy()
    
    def _ShouldUpdate(self, NewMetrics: Dict) -> bool:
        """Determine if display should be updated"""
        
        if not self.LastMetrics:
            return True
        
        # Check for significant changes (>5% difference)
        SignificantChange = False
        for Key, Value in NewMetrics.items():
            if isinstance(Value, (int, float)):
                OldValue = self.LastMetrics.get(Key, 0)
                if abs(Value - OldValue) > (OldValue * 0.05):  # 5% threshold
                    SignificantChange = True
                    break
        
        return SignificantChange


# Example usage and testing
if __name__ == "__main__":
    # Test gauge display
    Display = MonitoringGaugeDisplay()
    
    # Sample metrics data with some >100% values
    TestMetrics = {
        'tokens_used': 85000,
        'token_limit': 50000,  # >100% usage
        'messages_sent': 450,
        'message_limit': 1000,
        'rate_limit_hits': 15,
        'total_requests': 100,
        'efficiency_score': 0.85,
        'session_duration_minutes': 120,
        'avg_response_time': 1200,
        'cpu_usage': 45,
        'memory_usage': 78,
        'connection_health': 95
    }
    
    Display.DisplayMonitoringGauges(TestMetrics)