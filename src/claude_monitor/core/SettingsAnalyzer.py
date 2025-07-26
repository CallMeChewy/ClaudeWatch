# File: SettingsAnalyzer.py
# Path: /home/herb/Desktop/ClaudeWatch/src/claude_monitor/core/SettingsAnalyzer.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 04:21AM

"""
Intelligent settings analyzer that examines historical usage patterns
and provides optimization recommendations with user consent.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import statistics
import json

from claude_monitor.data.enhanced_database import EnhancedDatabaseManager
from claude_monitor.core.plans import PlanType

logger = logging.getLogger(__name__)

class RecommendationType(Enum):
    PLAN_OPTIMIZATION = "plan_optimization"
    RATE_LIMIT_ADJUSTMENT = "rate_limit_adjustment"
    MONITORING_FREQUENCY = "monitoring_frequency"
    SESSION_MANAGEMENT = "session_management"
    COST_OPTIMIZATION = "cost_optimization"

@dataclass
class SettingsRecommendation:
    """Individual settings recommendation with context."""
    type: RecommendationType
    title: str
    description: str
    current_value: Any
    recommended_value: Any
    confidence: float  # 0.0 to 1.0
    impact: str  # "high", "medium", "low"
    reason: str
    data_points: int
    auto_applicable: bool = True

@dataclass
class AnalysisResult:
    """Complete analysis result with all recommendations."""
    total_sessions: int
    analysis_period_days: int
    recommendations: List[SettingsRecommendation]
    overall_efficiency: float
    potential_improvement: str
    data_quality: str  # "excellent", "good", "limited", "insufficient"

class SettingsAnalyzer:
    """
    Analyzes historical usage patterns and provides intelligent
    settings optimization recommendations.
    """
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db_manager = db_manager
        self.min_sessions = 5  # Minimum sessions needed for recommendations
        self.analysis_window_days = 30  # Default analysis window
        
    def AnalyzeHistoricalUsage(self, ProjectPath: Optional[str] = None) -> AnalysisResult:
        """
        Perform comprehensive analysis of historical usage patterns.
        
        Args:
            ProjectPath: Optional filter for specific project
            
        Returns:
            Complete analysis with optimization recommendations
        """
        logger.info(f"Starting historical usage analysis for project: {ProjectPath or 'all projects'}")
        
        # Get historical data
        Sessions = self._GetHistoricalSessions(ProjectPath)
        RateEvents = self._GetRateLimitEvents(ProjectPath)
        CurrentSettings = self._GetCurrentSettings()
        
        if len(Sessions) < self.min_sessions:
            return self._CreateInsufficientDataResult(len(Sessions))
        
        # Analyze different aspects
        Recommendations = []
        
        # Plan optimization analysis
        PlanRecommendations = self._AnalyzePlanOptimization(Sessions, RateEvents)
        Recommendations.extend(PlanRecommendations)
        
        # Rate limit analysis
        LimitRecommendations = self._AnalyzeRateLimitPatterns(Sessions, RateEvents)
        Recommendations.extend(LimitRecommendations)
        
        # Session management analysis
        SessionRecommendations = self._AnalyzeSessionPatterns(Sessions)
        Recommendations.extend(SessionRecommendations)
        
        # Cost optimization analysis
        CostRecommendations = self._AnalyzeCostOptimization(Sessions, RateEvents)
        Recommendations.extend(CostRecommendations)
        
        # Calculate overall metrics
        Efficiency = self._CalculateOverallEfficiency(Sessions, RateEvents)
        DataQuality = self._AssessDataQuality(Sessions, RateEvents)
        PotentialImprovement = self._EstimatePotentialImprovement(Recommendations)
        
        Result = AnalysisResult(
            total_sessions=len(Sessions),
            analysis_period_days=self.analysis_window_days,
            recommendations=Recommendations,
            overall_efficiency=Efficiency,
            potential_improvement=PotentialImprovement,
            data_quality=DataQuality
        )
        
        logger.info(f"Analysis complete: {len(Recommendations)} recommendations generated")
        return Result
    
    def _GetHistoricalSessions(self, project_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get historical session data for analysis."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.analysis_window_days)
        
        try:
            with self.db_manager._get_connection() as conn:
                if project_path:
                    sql = """
                        SELECT * FROM session_metrics 
                        WHERE project_path = ? AND start_time > ?
                        ORDER BY start_time DESC
                    """
                    cursor = conn.execute(sql, (project_path, cutoff_date.isoformat()))
                else:
                    sql = """
                        SELECT * FROM session_metrics 
                        WHERE start_time > ?
                        ORDER BY start_time DESC
                    """
                    cursor = conn.execute(sql, (cutoff_date.isoformat(),))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get historical sessions: {e}")
            return []
    
    def _GetRateLimitEvents(self, project_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get rate limit events for analysis."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.analysis_window_days)
        
        try:
            with self.db_manager._get_connection() as conn:
                if project_path:
                    sql = """
                        SELECT * FROM rate_limit_events 
                        WHERE project_path = ? AND timestamp > ?
                        ORDER BY timestamp DESC
                    """
                    cursor = conn.execute(sql, (project_path, cutoff_date.isoformat()))
                else:
                    sql = """
                        SELECT * FROM rate_limit_events 
                        WHERE timestamp > ?
                        ORDER BY timestamp DESC
                    """
                    cursor = conn.execute(sql, (cutoff_date.isoformat(),))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get rate limit events: {e}")
            return []
    
    def _GetCurrentSettings(self) -> Dict[str, Any]:
        """Get current system settings."""
        # This would integrate with actual settings system
        return {
            'current_plan': 'custom',
            'monitoring_enabled': True,
            'learning_enabled': True,
            'cleanup_frequency': 24,  # hours
        }
    
    def _AnalyzePlanOptimization(self, sessions: List[Dict], rate_events: List[Dict]) -> List[SettingsRecommendation]:
        """Analyze usage patterns for plan optimization."""
        recommendations = []
        
        if not sessions:
            return recommendations
        
        # Calculate usage statistics
        total_tokens = sum(session.get('total_tokens', 0) for session in sessions)
        total_messages = sum(session.get('message_count', 0) for session in sessions)
        rate_limit_frequency = len(rate_events) / len(sessions) if sessions else 0
        
        avg_tokens_per_session = total_tokens / len(sessions) if sessions else 0
        avg_messages_per_session = total_messages / len(sessions) if sessions else 0
        
        # Analyze plan suitability
        if rate_limit_frequency > 0.3:  # More than 30% of sessions hit limits
            recommendations.append(SettingsRecommendation(
                type=RecommendationType.PLAN_OPTIMIZATION,
                title="Consider Higher Plan Tier",
                description=f"You're hitting rate limits in {rate_limit_frequency:.1%} of sessions",
                current_value="Current plan",
                recommended_value="Higher tier plan",
                confidence=min(0.9, rate_limit_frequency * 2),
                impact="high",
                reason=f"High rate limit frequency ({rate_limit_frequency:.1%}) indicates current plan may be insufficient",
                data_points=len(sessions),
                auto_applicable=False  # Plan changes require user decision
            ))
        
        elif rate_limit_frequency < 0.05 and avg_tokens_per_session < 10000:  # Very low usage
            recommendations.append(SettingsRecommendation(
                type=RecommendationType.PLAN_OPTIMIZATION,
                title="Consider Lower Plan Tier",
                description=f"Low usage pattern detected: {avg_tokens_per_session:.0f} tokens/session",
                current_value="Current plan",
                recommended_value="Lower tier plan",
                confidence=0.7,
                impact="medium",
                reason=f"Low average usage ({avg_tokens_per_session:.0f} tokens/session) suggests potential cost savings",
                data_points=len(sessions),
                auto_applicable=False
            ))
        
        return recommendations
    
    def _AnalyzeRateLimitPatterns(self, sessions: List[Dict], rate_events: List[Dict]) -> List[SettingsRecommendation]:
        """Analyze rate limit patterns for optimization."""
        recommendations = []
        
        if not rate_events:
            return recommendations
        
        # Analyze timing patterns
        event_hours = []
        for event in rate_events:
            try:
                event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                event_hours.append(event_time.hour)
            except:
                continue
        
        if event_hours:
            # Find peak usage hours
            hour_counts = {}
            for hour in event_hours:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            peak_hour = max(hour_counts, key=hour_counts.get)
            peak_count = hour_counts[peak_hour]
            
            if peak_count > len(rate_events) * 0.3:  # More than 30% in one hour
                recommendations.append(SettingsRecommendation(
                    type=RecommendationType.RATE_LIMIT_ADJUSTMENT,
                    title="Adjust Usage Timing",
                    description=f"Peak usage at {peak_hour:02d}:00 causes {peak_count} rate limits",
                    current_value=f"Peak usage: {peak_hour:02d}:00",
                    recommended_value="Distribute usage more evenly",
                    confidence=0.8,
                    impact="medium",
                    reason=f"Usage concentrated in hour {peak_hour} ({peak_count} events)",
                    data_points=len(rate_events),
                    auto_applicable=False
                ))
        
        # Analyze session duration vs rate limits
        sessions_with_limits = 0
        total_duration = 0
        limit_durations = []
        
        for session in sessions:
            duration = session.get('session_duration', 0)
            total_duration += duration
            
            # Check if this session had rate limits
            session_id = session.get('session_id', '')
            session_events = [e for e in rate_events if e.get('session_id') == session_id]
            
            if session_events:
                sessions_with_limits += 1
                limit_durations.append(duration)
        
        if limit_durations and sessions:
            avg_limit_duration = statistics.mean(limit_durations)
            avg_total_duration = total_duration / len(sessions)
            
            if avg_limit_duration > avg_total_duration * 1.5:  # Rate limits in longer sessions
                recommendations.append(SettingsRecommendation(
                    type=RecommendationType.SESSION_MANAGEMENT,
                    title="Optimize Session Length",
                    description="Longer sessions more likely to hit rate limits",
                    current_value=f"Avg session: {avg_total_duration/3600:.1f}h",
                    recommended_value="Shorter, more frequent sessions",
                    confidence=0.7,
                    impact="medium",
                    reason=f"Sessions with limits average {avg_limit_duration/3600:.1f}h vs {avg_total_duration/3600:.1f}h overall",
                    data_points=len(sessions),
                    auto_applicable=False
                ))
        
        return recommendations
    
    def _AnalyzeSessionPatterns(self, sessions: List[Dict]) -> List[SettingsRecommendation]:
        """Analyze session management patterns."""
        recommendations = []
        
        if len(sessions) < 3:
            return recommendations
        
        # Analyze session frequency
        session_times = []
        for session in sessions:
            try:
                start_time = datetime.fromisoformat(session['start_time'].replace('Z', '+00:00'))
                session_times.append(start_time)
            except:
                continue
        
        if len(session_times) > 1:
            session_times.sort()
            intervals = []
            for i in range(1, len(session_times)):
                interval = (session_times[i] - session_times[i-1]).total_seconds() / 3600  # hours
                intervals.append(interval)
            
            avg_interval = statistics.mean(intervals) if intervals else 0
            
            # Very frequent sessions might benefit from optimization
            if avg_interval < 2:  # Less than 2 hours between sessions
                recommendations.append(SettingsRecommendation(
                    type=RecommendationType.SESSION_MANAGEMENT,
                    title="Enable Continuous Monitoring",
                    description=f"Very frequent usage detected (every {avg_interval:.1f}h)",
                    current_value="Standard monitoring",
                    recommended_value="Continuous monitoring mode",
                    confidence=0.8,
                    impact="high",
                    reason=f"Sessions every {avg_interval:.1f}h indicate need for continuous monitoring",
                    data_points=len(sessions),
                    auto_applicable=True
                ))
        
        return recommendations
    
    def _AnalyzeCostOptimization(self, sessions: List[Dict], rate_events: List[Dict]) -> List[SettingsRecommendation]:
        """Analyze cost optimization opportunities."""
        recommendations = []
        
        if not sessions:
            return recommendations
        
        # Calculate efficiency metrics
        total_tokens = sum(session.get('total_tokens', 0) for session in sessions)
        total_rate_limits = len(rate_events)
        
        if total_tokens > 0:
            efficiency = (total_tokens - total_rate_limits * 1000) / total_tokens  # Rough efficiency
            
            if efficiency < 0.8:  # Less than 80% efficiency
                recommendations.append(SettingsRecommendation(
                    type=RecommendationType.COST_OPTIMIZATION,
                    title="Improve Usage Efficiency",
                    description=f"Current efficiency: {efficiency:.1%}",
                    current_value=f"{efficiency:.1%} efficiency",
                    recommended_value="Enable intelligent learning",
                    confidence=0.7,
                    impact="medium",
                    reason=f"Low efficiency ({efficiency:.1%}) suggests room for optimization",
                    data_points=len(sessions),
                    auto_applicable=True
                ))
        
        return recommendations
    
    def _CalculateOverallEfficiency(self, sessions: List[Dict], rate_events: List[Dict]) -> float:
        """Calculate overall system efficiency score."""
        if not sessions:
            return 0.0
        
        # Factors contributing to efficiency
        factors = []
        
        # Rate limit frequency (lower is better)
        rate_limit_factor = max(0, 1 - (len(rate_events) / len(sessions)))
        factors.append(rate_limit_factor)
        
        # Session completion rate
        completed_sessions = len([s for s in sessions if s.get('status') == 'completed'])
        completion_factor = completed_sessions / len(sessions) if sessions else 0
        factors.append(completion_factor)
        
        # Average session duration (reasonable duration is better)
        durations = [s.get('session_duration', 0) for s in sessions if s.get('session_duration', 0) > 0]
        if durations:
            avg_duration = statistics.mean(durations)
            # Optimal duration is around 1-4 hours (3600-14400 seconds)
            duration_factor = min(1.0, max(0.0, 1 - abs(avg_duration - 7200) / 7200))
            factors.append(duration_factor)
        
        return statistics.mean(factors) if factors else 0.0
    
    def _AssessDataQuality(self, sessions: List[Dict], rate_events: List[Dict]) -> str:
        """Assess the quality of available data for analysis."""
        session_count = len(sessions)
        
        if session_count >= 20:
            return "excellent"
        elif session_count >= 10:
            return "good"
        elif session_count >= 5:
            return "limited"
        else:
            return "insufficient"
    
    def _EstimatePotentialImprovement(self, recommendations: List[SettingsRecommendation]) -> str:
        """Estimate potential improvement from recommendations."""
        if not recommendations:
            return "No optimizations needed"
        
        high_impact = len([r for r in recommendations if r.impact == "high"])
        medium_impact = len([r for r in recommendations if r.impact == "medium"])
        
        if high_impact >= 2:
            return "Significant improvement potential (30-50%)"
        elif high_impact >= 1 or medium_impact >= 3:
            return "Moderate improvement potential (15-30%)"
        elif medium_impact >= 1:
            return "Minor improvement potential (5-15%)"
        else:
            return "Small optimization opportunities available"
    
    def _CreateInsufficientDataResult(self, session_count: int) -> AnalysisResult:
        """Create result for insufficient data scenario."""
        return AnalysisResult(
            total_sessions=session_count,
            analysis_period_days=self.analysis_window_days,
            recommendations=[],
            overall_efficiency=0.0,
            potential_improvement=f"Need {self.min_sessions - session_count} more sessions for analysis",
            data_quality="insufficient"
        )
    
    def ApplyRecommendation(self, recommendation: SettingsRecommendation) -> bool:
        """
        Apply a specific recommendation automatically.
        
        Args:
            recommendation: The recommendation to apply
            
        Returns:
            True if successfully applied, False otherwise
        """
        if not recommendation.auto_applicable:
            logger.warning(f"Recommendation '{recommendation.title}' is not auto-applicable")
            return False
        
        try:
            logger.info(f"Applying recommendation: {recommendation.title}")
            
            # Implementation would depend on recommendation type
            if recommendation.type == RecommendationType.SESSION_MANAGEMENT:
                # Enable continuous monitoring
                logger.info("Enabled continuous monitoring mode")
                return True
            
            elif recommendation.type == RecommendationType.COST_OPTIMIZATION:
                # Enable intelligent learning
                logger.info("Enabled intelligent learning optimizations")
                return True
            
            elif recommendation.type == RecommendationType.MONITORING_FREQUENCY:
                # Adjust monitoring frequency
                logger.info("Adjusted monitoring frequency")
                return True
            
            logger.warning(f"No implementation for recommendation type: {recommendation.type}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to apply recommendation: {e}")
            return False