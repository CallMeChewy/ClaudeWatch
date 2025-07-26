# File: StartupAnalysisDisplay.py
# Path: /home/herb/Desktop/ClaudeWatch/src/claude_monitor/ui/StartupAnalysisDisplay.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 04:21AM

"""
User interface components for displaying startup analysis results
and handling user consent for automatic optimizations.
"""

import logging
from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm, Prompt
from rich.text import Text
from rich.markdown import Markdown
import time

from claude_monitor.core.SettingsAnalyzer import AnalysisResult, SettingsRecommendation, RecommendationType

logger = logging.getLogger(__name__)

class StartupAnalysisDisplay:
    """
    Handles the display of startup analysis results and user interactions
    for optimization recommendations.
    """
    
    def __init__(self, console: Console):
        self.console = console
        self.auto_apply_enabled = True
    
    def ShowAnalysisResults(self, Analysis: AnalysisResult, ProjectPath: str) -> List[SettingsRecommendation]:
        """
        Display analysis results and get user consent for recommendations.
        
        Args:
            Analysis: Complete analysis results
            ProjectPath: Current project path
            
        Returns:
            List of recommendations approved by user
        """
        if Analysis.data_quality == "insufficient":
            self._ShowInsufficientDataMessage(Analysis)
            return []
        
        # Show analysis summary
        self._ShowAnalysisSummary(Analysis, ProjectPath)
        
        if not Analysis.recommendations:
            self._ShowNoRecommendationsMessage(Analysis)
            return []
        
        # Show recommendations and get user consent
        ApprovedRecommendations = self._HandleRecommendations(Analysis.recommendations)
        
        return ApprovedRecommendations
    
    def _ShowAnalysisSummary(self, Analysis: AnalysisResult, ProjectPath: str) -> None:
        """Display analysis summary with key metrics."""
        
        # Create summary panel
        SummaryText = f"""
📊 **Usage Analysis Summary**

**Project**: `{ProjectPath}`
**Analysis Period**: {Analysis.analysis_period_days} days
**Sessions Analyzed**: {Analysis.total_sessions}
**Overall Efficiency**: {Analysis.overall_efficiency:.1%}
**Data Quality**: {Analysis.data_quality.title()}

**Potential Improvement**: {Analysis.potential_improvement}
        """.strip()
        
        AnalysisPanel = Panel(
            Markdown(SummaryText),
            title="🔍 Historical Usage Analysis",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(AnalysisPanel)
    
    def _ShowInsufficientDataMessage(self, analysis: AnalysisResult) -> None:
        """Show message when insufficient data is available."""
        
        message_text = f"""
**Insufficient Usage History**

I found only {analysis.total_sessions} session(s) in the last {analysis.analysis_period_days} days.
I need at least 5 sessions to provide meaningful optimization recommendations.

💡 **What you can do:**
- Continue using Claude Code regularly
- Run this analysis again after a few more sessions
- The system will automatically learn and optimize as you use it

**Current Status**: Learning mode active, collecting usage patterns...
        """.strip()
        
        panel = Panel(
            Markdown(message_text),
            title="📈 Building Usage Profile",
            border_style="yellow",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(panel)
    
    def _ShowNoRecommendationsMessage(self, analysis: AnalysisResult) -> None:
        """Show message when no optimizations are needed."""
        
        message_text = f"""
**Your settings are already optimized!** ✨

Based on {analysis.total_sessions} sessions over {analysis.analysis_period_days} days:
- **Efficiency Score**: {analysis.overall_efficiency:.1%}
- **Data Quality**: {analysis.data_quality.title()}

No changes needed at this time. The system is performing well with your current usage patterns.
        """.strip()
        
        panel = Panel(
            Markdown(message_text),
            title="✅ Optimal Configuration",
            border_style="green",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(panel)
    
    def _HandleRecommendations(self, recommendations: List[SettingsRecommendation]) -> List[SettingsRecommendation]:
        """Handle user interaction for recommendations."""
        
        # Group recommendations by type
        auto_recommendations = [r for r in recommendations if r.auto_applicable]
        manual_recommendations = [r for r in recommendations if not r.auto_applicable]
        
        approved = []
        
        # Handle auto-applicable recommendations
        if auto_recommendations:
            approved.extend(self._HandleAutoRecommendations(auto_recommendations))
        
        # Handle manual recommendations
        if manual_recommendations:
            approved.extend(self._HandleManualRecommendations(manual_recommendations))
        
        return approved
    
    def _HandleAutoRecommendations(self, recommendations: List[SettingsRecommendation]) -> List[SettingsRecommendation]:
        """Handle automatically applicable recommendations."""
        
        self.console.print()
        self.console.print("🤖 **Automatic Optimizations Available**", style="bold cyan")
        
        # Show recommendations table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Optimization", style="cyan", no_wrap=True)
        table.add_column("Impact", justify="center")
        table.add_column("Confidence", justify="center")
        table.add_column("Description")
        
        for rec in recommendations:
            impact_style = {
                "high": "red bold",
                "medium": "yellow",
                "low": "dim"
            }.get(rec.impact, "white")
            
            confidence_text = f"{rec.confidence:.0%}"
            confidence_style = "green" if rec.confidence > 0.8 else "yellow" if rec.confidence > 0.6 else "red"
            
            table.add_row(
                rec.title,
                Text(rec.impact.title(), style=impact_style),
                Text(confidence_text, style=confidence_style),
                rec.description
            )
        
        self.console.print(table)
        self.console.print()
        
        # Ask for bulk consent with error handling
        try:
            if Confirm.ask("🔄 Apply these optimizations automatically?", default=True):
                return recommendations
            else:
                # Ask individually
                approved = []
                for rec in recommendations:
                    try:
                        if Confirm.ask(f"Apply: {rec.title}?", default=True):
                            approved.append(rec)
                    except (EOFError, KeyboardInterrupt):
                        # User interrupted or EOF - assume no for this recommendation
                        continue
                return approved
        except (EOFError, KeyboardInterrupt):
            # User interrupted or EOF - apply all by default in non-interactive mode
            self.console.print("🔄 Non-interactive mode detected, applying all optimizations...", style="yellow")
            return recommendations
        
        return []
    
    def _HandleManualRecommendations(self, recommendations: List[SettingsRecommendation]) -> List[SettingsRecommendation]:
        """Handle recommendations that require manual action."""
        
        self.console.print()
        self.console.print("👤 **Manual Recommendations**", style="bold yellow")
        self.console.print("These suggestions require your consideration:")
        self.console.print()
        
        for i, rec in enumerate(recommendations, 1):
            # Create detailed recommendation panel
            rec_text = f"""
**{rec.title}**

{rec.description}

**Current**: {rec.current_value}
**Recommended**: {rec.recommended_value}

**Why**: {rec.reason}
**Confidence**: {rec.confidence:.0%} (based on {rec.data_points} data points)
**Impact**: {rec.impact.title()}
            """.strip()
            
            panel = Panel(
                Markdown(rec_text),
                title=f"💡 Recommendation {i}",
                border_style="yellow",
                padding=(1, 2)
            )
            
            self.console.print(panel)
            self.console.print()
        
        # These are informational only - user must take action manually
        return []
    
    def ShowApplyingRecommendations(self, recommendations: List[SettingsRecommendation]) -> None:
        """Show progress while applying recommendations."""
        
        if not recommendations:
            return
        
        self.console.print()
        self.console.print("🔄 **Applying Optimizations...**", style="bold green")
        
        for rec in recommendations:
            self.console.print(f"  • {rec.title}...", end="")
            time.sleep(0.5)  # Brief pause for user experience
            self.console.print(" ✅", style="green")
        
        self.console.print()
        self.console.print("✨ **Optimizations applied successfully!**", style="bold green")
    
    def ShowOptimizationResults(self, applied_count: int, failed_count: int) -> None:
        """Show final results of optimization process."""
        
        if applied_count == 0 and failed_count == 0:
            return
        
        self.console.print()
        
        if applied_count > 0:
            result_text = f"""
**Optimization Complete** ✅

- **Applied**: {applied_count} optimization(s)
- **Failed**: {failed_count} optimization(s)

Your Claude monitoring is now optimized based on your usage patterns!
The system will continue learning and adapting as you use it.
            """.strip()
            
            panel = Panel(
                Markdown(result_text),
                title="🎯 Optimization Results",
                border_style="green",
                padding=(1, 2)
            )
            
            self.console.print(panel)
        
        if failed_count > 0:
            self.console.print(f"⚠️  {failed_count} optimization(s) could not be applied automatically.", style="yellow")
    
    def ShowSkippedAnalysis(self, reason: str) -> None:
        """Show message when analysis is skipped."""
        
        skip_text = f"""
**Analysis Skipped**

{reason}

You can run analysis manually anytime with:
`python run_enhanced_monitor.py --analyze-settings`
        """.strip()
        
        panel = Panel(
            Markdown(skip_text),
            title="ℹ️  Startup Analysis",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(panel)
    
    def CreateQuickSummary(self, analysis: AnalysisResult) -> str:
        """Create a brief summary for logging or status display."""
        
        if analysis.data_quality == "insufficient":
            return f"Usage analysis: {analysis.total_sessions} sessions (need more data)"
        
        if not analysis.recommendations:
            return f"Usage analysis: {analysis.total_sessions} sessions, efficiency {analysis.overall_efficiency:.0%}, no optimizations needed"
        
        auto_count = len([r for r in analysis.recommendations if r.auto_applicable])
        manual_count = len([r for r in analysis.recommendations if not r.auto_applicable])
        
        return f"Usage analysis: {analysis.total_sessions} sessions, {auto_count} auto optimizations, {manual_count} suggestions"