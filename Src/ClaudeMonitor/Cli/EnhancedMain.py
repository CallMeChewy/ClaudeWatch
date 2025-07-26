# File: EnhancedMain.py
# Path: /home/herb/Desktop/ClaudeWatch/Src/ClaudeMonitor/Cli/EnhancedMain.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-01-26
# Last Modified: 2025-07-26 10:53AM

"""Enhanced CLI entry point using the intelligent orchestrator system."""

import argparse
import logging
import signal
import sys
import time
from pathlib import Path
from typing import List, Optional

from rich.console import Console

from ClaudeMonitor import __version__
from ClaudeMonitor.Cli.Bootstrap import SetupEnvironment, SetupLogging, EnsureDirectories
from ClaudeMonitor.Core.SettingsAnalyzer import SettingsAnalyzer
from ClaudeMonitor.Ui.StartupAnalysisDisplay import StartupAnalysisDisplay
from ClaudeMonitor.Monitoring.IntelligentOrchestrator import IntelligentOrchestrator


def CreateEnhancedParser() -> argparse.ArgumentParser:
    """Create argument parser for enhanced CLI."""
    parser = argparse.ArgumentParser(
        description="Enhanced Claude Code Usage Monitor with intelligent learning",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--version", "-v", 
        action="version", 
        version=f"claude-monitor {__version__} (enhanced)"
    )
    
    parser.add_argument(
        "--plan", 
        choices=["pro", "max5", "max20", "custom"],
        default="custom",
        help="Claude subscription plan (default: custom with auto-detection)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Log file path"
    )
    
    parser.add_argument(
        "--export-report",
        type=Path,
        help="Export comprehensive analytics report to specified path"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current system status and exit"
    )
    
    parser.add_argument(
        "--skip-analysis",
        action="store_true",
        help="Skip startup usage analysis and optimization suggestions"
    )
    
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Enhanced main entry point."""
    if argv is None:
        argv = sys.argv[1:]
    
    parser = CreateEnhancedParser()
    args = parser.parse_args(argv)
    
    # Initialize console first for error handling
    console = Console()
    
    try:
        # Setup environment
        SetupEnvironment()
        EnsureDirectories()
        
        # Setup logging
        LogLevel = "DEBUG" if args.debug else "INFO"
        if args.log_file:
            SetupLogging(LogLevel, args.log_file, DisableConsole=False)
        else:
            SetupLogging(LogLevel, DisableConsole=False)
        
        logger = logging.getLogger(__name__)
        logger.info("Starting Enhanced Claude Monitor")
        
        # Console already initialized at function start
        
        # Handle different modes
        if args.status:
            return show_status(console)
        
        if args.export_report:
            return export_report(console, args.export_report)
        
        # Default: Start monitoring
        return start_enhanced_monitoring(console, args)
        
    except KeyboardInterrupt:
        console.print("\n🛑 Enhanced monitoring stopped by user", style="yellow")
        return 0
    except Exception as e:
        console.print(f"❌ Enhanced monitor failed: {e}", style="red")
        logger = logging.getLogger(__name__)
        logger.error(f"Enhanced monitor failed: {e}", exc_info=True)
        return 1


def show_status(console: Console) -> int:
    """Show current system status."""
    try:
        console.print("📊 Enhanced Claude Monitor - System Status", style="bold blue")
        console.print("=" * 50)
        
        # Create temporary orchestrator to get status
        config = {"status_only": True}
        with IntelligentOrchestrator(config) as orchestrator:
            status = orchestrator.get_real_time_status()
            
            # Display system status
            system_status = status.get('system_status', {})
            console.print(f"🖥️  Terminal ID: {system_status.get('terminal_id', 'N/A')}")
            console.print(f"📁  Project Path: {system_status.get('current_project', 'N/A')}")
            console.print(f"⏱️  Running: {system_status.get('is_running', False)}")
            
            # Display monitoring stats
            monitoring_stats = status.get('monitoring_stats', {})
            console.print(f"🔄  Active Sessions: {monitoring_stats.get('active_sessions', 0)}")
            console.print(f"⚠️  Rate Limit Events: {monitoring_stats.get('total_rate_limit_events', 0)}")
            
            # Display learning performance
            learning_perf = status.get('learning_performance', {})
            summary = learning_perf.get('summary', {})
            if summary.get('total_predictions', 0) > 0:
                accuracy = summary.get('average_accuracy', 0)
                console.print(f"🧠  Learning Accuracy: {accuracy:.1%}")
            else:
                console.print("🧠  Learning: Initializing...")
            
            console.print("\n✅ Enhanced monitoring system is operational!")
            
        return 0
        
    except Exception as e:
        console.print(f"❌ Failed to get status: {e}", style="red")
        return 1


def export_report(console: Console, output_path: Path) -> int:
    """Export comprehensive analytics report."""
    try:
        console.print("📊 Exporting Enhanced Analytics Report...", style="blue")
        
        config = {"export_only": True}
        with IntelligentOrchestrator(config) as orchestrator:
            report_path = orchestrator.export_comprehensive_report(output_path)
            
            console.print(f"✅ Report exported successfully!", style="green")
            console.print(f"📄 Location: {report_path}")
            
        return 0
        
    except Exception as e:
        console.print(f"❌ Failed to export report: {e}", style="red")
        return 1


def perform_startup_analysis(console: Console, orchestrator, project_path: str) -> Optional[str]:
    """
    Perform startup analysis and handle user interaction for optimizations.
    
    Args:
        console: Rich console for output
        orchestrator: The intelligent orchestrator instance
        project_path: Current project path
        
    Returns:
        Brief summary of analysis results
    """
    try:
        # Create analyzer and display handler
        analyzer = SettingsAnalyzer(orchestrator.db_manager)
        display = StartupAnalysisDisplay(console)
        
        # Perform analysis
        analysis = analyzer.AnalyzeHistoricalUsage(project_path)
        
        # Show results and get user consent
        approved_recommendations = display.ShowAnalysisResults(analysis, project_path)
        
        # Apply approved recommendations
        if approved_recommendations:
            display.ShowApplyingRecommendations(approved_recommendations)
            
            applied_count = 0
            failed_count = 0
            
            for recommendation in approved_recommendations:
                if analyzer.ApplyRecommendation(recommendation):
                    applied_count += 1
                else:
                    failed_count += 1
            
            display.ShowOptimizationResults(applied_count, failed_count)
        
        # Return summary for logging
        return display.CreateQuickSummary(analysis)
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Startup analysis failed: {e}", exc_info=True)
        console.print(f"⚠️  Startup analysis encountered an error: {e}", style="yellow")
        return "Analysis failed"


def start_enhanced_monitoring(console: Console, args: argparse.Namespace) -> int:
    """Start the enhanced monitoring system."""
    console.print("🚀 Enhanced Claude Monitor - Starting...", style="bold green")
    console.print("=" * 50)
    
    # Create configuration
    config = {
        "plan": args.plan,
        "debug": args.debug
    }
    
    try:
        with IntelligentOrchestrator(config) as orchestrator:
            console.print("✅ Enhanced monitoring system started successfully!", style="green")
            
            # Perform startup analysis and optimization (unless skipped)
            if not args.skip_analysis:
                current_project = orchestrator.current_project_path
                startup_analysis_result = perform_startup_analysis(console, orchestrator, current_project)
            else:
                console.print("ℹ️  Startup analysis skipped (--skip-analysis)", style="dim")
            
            console.print("\n🔍 Features Active:")
            console.print("  • Real-time MCP log monitoring")
            console.print("  • Advanced rate limit detection")
            console.print("  • Intelligent learning algorithms")
            console.print("  • Multi-terminal session tracking")
            console.print("  • Comprehensive analytics")
            
            # Show initial status
            status = orchestrator.get_real_time_status()
            system_status = status.get('system_status', {})
            
            console.print(f"\n📋 Current Status:")
            console.print(f"  • Terminal: {system_status.get('terminal_id', 'N/A')}")
            console.print(f"  • Project: {system_status.get('current_project', 'N/A')}")
            console.print(f"  • Plan: {args.plan}")
            
            console.print(f"\n💡 Press Ctrl+C to stop monitoring")
            console.print("🔄 Monitoring in progress...\n")
            
            # Main monitoring loop
            try:
                signal.pause()
            except AttributeError:
                # Fallback for Windows
                while True:
                    time.sleep(1)
                    
    except KeyboardInterrupt:
        console.print("\n🛑 Monitoring stopped by user", style="yellow")
        return 0
    except Exception as e:
        console.print(f"\n❌ Monitoring failed: {e}", style="red")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())