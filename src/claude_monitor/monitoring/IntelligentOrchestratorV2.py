# File: IntelligentOrchestratorV2.py
# Path: /home/herb/Desktop/ClaudeWatch/src/claude_monitor/monitoring/IntelligentOrchestratorV2.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 04:17AM

"""
Enhanced Intelligent Orchestrator V2 with full multi-session support.
Coordinates independent Claude Code monitoring sessions across different
terminals, SSH connections, and execution contexts.
"""

import logging
import threading
import time
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from pathlib import Path

from claude_monitor.monitoring.MultiSessionCoordinator import MultiSessionCoordinator
from claude_monitor.core.SessionDetector import SessionContext
from claude_monitor.data.enhanced_database import EnhancedDatabaseManager
from claude_monitor.monitoring.enhanced_proxy_monitor import EnhancedProxyMonitor

logger = logging.getLogger(__name__)

class IntelligentOrchestratorV2:
    """
    Enhanced orchestrator with full multi-session support and coordination.
    Manages independent monitoring sessions while ensuring proper isolation
    and resource optimization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the enhanced orchestrator with multi-session support."""
        self.config = config or {}
        
        # Multi-session coordination
        self.coordinator = MultiSessionCoordinator(self.config)
        self.current_session: Optional[SessionContext] = None
        
        # Legacy compatibility - these will be set after session detection
        self.db_manager: Optional[EnhancedDatabaseManager] = None
        self.proxy_monitor: Optional[EnhancedProxyMonitor] = None
        
        # Runtime state
        self.is_running = False
        self.orchestrator_thread: Optional[threading.Thread] = None
        
        # Properties for backward compatibility
        self._terminal_id: Optional[str] = None
        self._current_project_path: Optional[str] = None
        
        # Performance tracking
        self.orchestration_stats = {
            'sessions_coordinated': 0,
            'cross_session_events': 0,
            'resource_optimizations': 0,
            'start_time': datetime.now(timezone.utc)
        }
    
    @property
    def terminal_id(self) -> str:
        """Get terminal ID for backward compatibility."""
        if self.current_session:
            return self.current_session.terminal_id
        return self._terminal_id or "unknown"
    
    @property
    def current_project_path(self) -> str:
        """Get current project path for backward compatibility."""
        if self.current_session:
            return self.current_session.working_directory
        return self._current_project_path or os.getcwd()
    
    def start_intelligent_monitoring(self) -> None:
        """Start intelligent monitoring with multi-session coordination."""
        if self.is_running:
            logger.warning("Intelligent monitoring already running")
            return
        
        logger.info("Starting intelligent monitoring with multi-session support...")
        
        try:
            # Start multi-session coordination and get current session
            self.current_session = self.coordinator.StartCoordination()
            
            # Set up session-specific components for backward compatibility
            self._setup_session_components()
            
            # Start orchestrator thread
            self._start_orchestrator_thread()
            
            self.is_running = True
            self.orchestration_stats['sessions_coordinated'] += 1
            
            logger.info(f"Intelligent monitoring started for session: {self.current_session.isolation_key}")
            logger.info(f"Session type: {self.current_session.session_type}")
            logger.info(f"Terminal: {self.current_session.terminal_device}")
            
            if self.current_session.ssh_connection:
                logger.info(f"SSH connection: {self.current_session.ssh_connection}")
            
        except Exception as e:
            logger.error(f"Failed to start intelligent monitoring: {e}", exc_info=True)
            raise
    
    def stop_intelligent_monitoring(self) -> None:
        """Stop intelligent monitoring and coordination."""
        if not self.is_running:
            return
        
        logger.info("Stopping intelligent monitoring...")
        
        try:
            # Stop orchestrator thread
            self.is_running = False
            if self.orchestrator_thread and self.orchestrator_thread.is_alive():
                self.orchestrator_thread.join(timeout=10)
            
            # Stop coordination for current session
            if self.current_session:
                self.coordinator.StopCoordination(self.current_session.isolation_key)
            
            logger.info("Intelligent monitoring stopped")
            
        except Exception as e:
            logger.error(f"Error stopping intelligent monitoring: {e}", exc_info=True)
    
    def get_real_time_status(self) -> Dict[str, Any]:
        """Get comprehensive real-time status including multi-session info."""
        if not self.current_session:
            return {
                'system_status': {
                    'terminal_id': 'not_initialized',
                    'current_project': os.getcwd(),
                    'is_running': self.is_running
                },
                'monitoring_stats': {},
                'learning_performance': {},
                'multi_session_info': {}
            }
        
        # Get multi-session information
        multi_session_info = self.coordinator.GetActiveSessionsInfo()
        current_session_status = self.coordinator.GetSessionStatus(self.current_session.isolation_key)
        
        # Legacy status format for backward compatibility
        system_status = {
            'terminal_id': self.current_session.terminal_id,
            'current_project': self.current_session.working_directory,
            'is_running': self.is_running,
            'session_type': self.current_session.session_type,
            'isolation_key': self.current_session.isolation_key
        }
        
        # Enhanced monitoring stats
        monitoring_stats = {
            'active_sessions': multi_session_info['active_sessions_count'],
            'current_session_stats': current_session_status.get('monitor_status', {}) if current_session_status else {},
            'total_rate_limit_events': sum(
                session.get('rate_limit_count', 0) 
                for session in multi_session_info['sessions'].values()
            ),
            'session_types': multi_session_info['detector_summary'].get('session_types', {})
        }
        
        # Learning performance (from session-specific components)
        learning_performance = {}
        if self.db_manager:
            try:
                learning_performance = self.db_manager.get_learning_performance()
            except Exception as e:
                logger.debug(f"Could not get learning performance: {e}")
        
        return {
            'system_status': system_status,
            'monitoring_stats': monitoring_stats,
            'learning_performance': learning_performance,
            'multi_session_info': multi_session_info,
            'orchestration_stats': self.orchestration_stats
        }
    
    def export_comprehensive_report(self, output_path: Path) -> Path:
        """Export comprehensive report including multi-session data."""
        report_data = {
            'export_time': datetime.now(timezone.utc).isoformat(),
            'current_session': {
                'session_id': self.current_session.session_id if self.current_session else None,
                'session_type': self.current_session.session_type if self.current_session else None,
                'isolation_key': self.current_session.isolation_key if self.current_session else None,
                'working_directory': self.current_session.working_directory if self.current_session else None
            },
            'real_time_status': self.get_real_time_status(),
            'orchestration_stats': self.orchestration_stats
        }
        
        # Add session-specific database analytics if available
        if self.db_manager:
            try:
                analytics_path = output_path.with_suffix('.analytics.json')
                self.db_manager.export_analytics_data(analytics_path)
                report_data['analytics_exported'] = str(analytics_path)
            except Exception as e:
                logger.error(f"Failed to export analytics: {e}")
                report_data['analytics_error'] = str(e)
        
        # Export multi-session report
        multi_session_path = output_path.with_suffix('.sessions.json')
        self.coordinator.ExportMultiSessionReport(multi_session_path)
        report_data['multi_session_report'] = str(multi_session_path)
        
        # Write main report
        import json
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"Comprehensive report exported to {output_path}")
        return output_path
    
    def get_session_recommendations(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """Get optimization recommendations for current or specified project."""
        if not self.db_manager:
            return {'error': 'Database manager not initialized'}
        
        # This would integrate with the SettingsAnalyzer
        try:
            from claude_monitor.core.SettingsAnalyzer import SettingsAnalyzer
            analyzer = SettingsAnalyzer(self.db_manager)
            analysis = analyzer.AnalyzeHistoricalUsage(project_path or self.current_project_path)
            
            return {
                'analysis_summary': {
                    'total_sessions': analysis.total_sessions,
                    'overall_efficiency': analysis.overall_efficiency,
                    'data_quality': analysis.data_quality,
                    'potential_improvement': analysis.potential_improvement
                },
                'recommendations': [
                    {
                        'type': rec.type.value,
                        'title': rec.title,
                        'description': rec.description,
                        'confidence': rec.confidence,
                        'impact': rec.impact,
                        'auto_applicable': rec.auto_applicable
                    }
                    for rec in analysis.recommendations
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return {'error': str(e)}
    
    def _setup_session_components(self) -> None:
        """Set up session-specific components for backward compatibility."""
        if not self.current_session:
            raise RuntimeError("No current session available")
        
        # Get session-specific monitors from coordinator
        session_status = self.coordinator.GetSessionStatus(self.current_session.isolation_key)
        if not session_status:
            raise RuntimeError("Could not get session status from coordinator")
        
        # Set up components by finding the active monitor
        if self.current_session.isolation_key in self.coordinator.active_monitors:
            monitor = self.coordinator.active_monitors[self.current_session.isolation_key]
            self.db_manager = monitor.db_manager
            self.proxy_monitor = monitor.proxy_monitor
        else:
            # Fallback - create new components (shouldn't happen in normal flow)
            logger.warning("Creating fallback components - this should not happen")
            self.db_manager = EnhancedDatabaseManager(self.config)
            self.proxy_monitor = EnhancedProxyMonitor(self.db_manager)
    
    def _start_orchestrator_thread(self) -> None:
        """Start the orchestrator management thread."""
        def orchestrator_loop():
            """Main orchestrator loop for managing coordination."""
            logger.info("Starting orchestrator management thread...")
            
            last_stats_update = datetime.now(timezone.utc)
            stats_interval = 60  # Update stats every minute
            
            while self.is_running:
                try:
                    # Update orchestration statistics
                    now = datetime.now(timezone.utc)
                    if (now - last_stats_update).total_seconds() > stats_interval:
                        self._update_orchestration_stats()
                        last_stats_update = now
                    
                    # Check for cross-session events
                    self._handle_cross_session_events()
                    
                    # Resource optimization
                    self._optimize_cross_session_resources()
                    
                    time.sleep(30)  # 30-second intervals
                    
                except Exception as e:
                    logger.error(f"Orchestrator loop error: {e}", exc_info=True)
                    time.sleep(5)
            
            logger.info("Orchestrator management thread stopped")
        
        self.orchestrator_thread = threading.Thread(
            target=orchestrator_loop,
            name="OrchestratorManager",
            daemon=True
        )
        self.orchestrator_thread.start()
    
    def _update_orchestration_stats(self) -> None:
        """Update orchestration statistics."""
        multi_session_info = self.coordinator.GetActiveSessionsInfo()
        
        # Update stats based on coordination activity
        self.orchestration_stats.update({
            'current_active_sessions': multi_session_info['active_sessions_count'],
            'session_types_active': len(multi_session_info['detector_summary'].get('session_types', {})),
            'last_stats_update': datetime.now(timezone.utc)
        })
    
    def _handle_cross_session_events(self) -> None:
        """Handle events that affect multiple sessions."""
        # Check for rate limit events that should be shared across sessions
        multi_session_info = self.coordinator.GetActiveSessionsInfo()
        
        # Group sessions by project to identify related sessions
        project_sessions = {}
        for session_data in multi_session_info['sessions'].values():
            project = session_data['working_directory']
            if project not in project_sessions:
                project_sessions[project] = []
            project_sessions[project].append(session_data)
        
        # Handle cross-session events for projects with multiple sessions
        for project, sessions in project_sessions.items():
            if len(sessions) > 1:
                self._coordinate_project_sessions(project, sessions)
    
    def _coordinate_project_sessions(self, project_path: str, sessions: List[Dict[str, Any]]) -> None:
        """Coordinate sessions working on the same project."""
        # Check for recent rate limits that should be shared
        recent_rate_limits = [
            session for session in sessions
            if session['rate_limit_count'] > 0
        ]
        
        if recent_rate_limits:
            # Send coordination message about rate limits
            self.coordinator.SendCoordinationMessage(
                'project_rate_limit_detected',
                {
                    'project_path': project_path,
                    'affected_sessions': len(recent_rate_limits),
                    'total_sessions': len(sessions)
                }
            )
            self.orchestration_stats['cross_session_events'] += 1
    
    def _optimize_cross_session_resources(self) -> None:
        """Optimize resources across sessions."""
        # Placeholder for resource optimization logic
        # Could implement:
        # - Shared database connection pooling
        # - Coordinated cleanup schedules
        # - Load distribution
        # - Conflict resolution
        pass
    
    def __enter__(self):
        """Context manager entry."""
        self.start_intelligent_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_intelligent_monitoring()