# File: intelligent_orchestrator.py
# Path: /home/herb/Desktop/ClaudeWatch/Src/ClaudeMonitor/monitoring/intelligent_orchestrator.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-01-26
# Last Modified: 2025-07-26 08:15AM

"""Intelligent orchestrator that coordinates enhanced monitoring with real-time learning."""

import logging
import threading
import time
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List

from ClaudeMonitor.Data.EnhancedDatabase import EnhancedDatabaseManager
from ClaudeMonitor.Monitoring.EnhancedProxyMonitor import EnhancedProxyMonitor
from ClaudeMonitor.Core.Plans import Plans, PlanType

logger = logging.getLogger(__name__)


class IntelligentOrchestrator:
    """Intelligent orchestrator that coordinates all enhanced monitoring components."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the intelligent orchestrator."""
        self.config = config or {}
        
        # Initialize enhanced components
        self.db_manager = EnhancedDatabaseManager()
        self.proxy_monitor = EnhancedProxyMonitor(self.db_manager)
        
        # Runtime state
        self.is_running = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Terminal and session tracking
        self.terminal_id = self._generate_terminal_id()
        self.current_project_path = os.getcwd()
        
        # Performance tracking
        self.learning_stats = {
            'predictions_made': 0,
            'accuracy_improvements': 0,
            'last_learning_update': None
        }

    def _generate_terminal_id(self) -> str:
        """Generate unique terminal identifier."""
        import socket
        import getpass
        
        hostname = socket.gethostname()
        username = getpass.getuser()
        pid = os.getpid()
        timestamp = int(time.time())
        
        return f"{username}@{hostname}:{pid}:{timestamp}"

    def start_intelligent_monitoring(self) -> None:
        """Start the intelligent monitoring system."""
        if self.is_running:
            logger.warning("Intelligent monitoring is already running")
            return
        
        logger.info("Starting intelligent monitoring system...")
        
        try:
            # Register this terminal session
            self._register_terminal_session()
            
            # Start the proxy monitor
            self.proxy_monitor.start_monitoring()
            
            # Start background learning thread
            self.monitoring_thread = threading.Thread(
                target=self._background_monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.is_running = True
            logger.info("Intelligent monitoring system started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start intelligent monitoring: {e}", exc_info=True)
            self.stop_intelligent_monitoring()

    def stop_intelligent_monitoring(self) -> None:
        """Stop the intelligent monitoring system."""
        if not self.is_running:
            return
        
        logger.info("Stopping intelligent monitoring system...")
        
        try:
            self.is_running = False
            
            # Stop proxy monitor
            self.proxy_monitor.stop_monitoring()
            
            # Wait for background thread to finish
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5.0)
            
            # Final session update
            self._update_terminal_session_status('completed')
            
            logger.info("Intelligent monitoring system stopped")
            
        except Exception as e:
            logger.error(f"Error stopping intelligent monitoring: {e}", exc_info=True)

    def _register_terminal_session(self) -> None:
        """Register this terminal session in the database."""
        SessionId = f"{self.terminal_id}#{int(time.time())}"
        
        # First create the session_metrics record (required for foreign key)
        session_metrics = {
            'session_id': SessionId,
            'start_time': datetime.now(timezone.utc).isoformat(),
            'project_path': self.current_project_path,
            'plan_type': 'custom',  # Default plan type
            'total_tokens_used': 0,
            'total_messages_sent': 0,
            'rate_limit_hits': 0,
            'session_duration': 0,
            'efficiency_score': 1.0
        }
        self.db_manager.create_or_update_session_metrics(session_metrics)
        
        # Then register the terminal session
        SessionData = {
            'terminal_id': self.terminal_id,
            'project_path': self.current_project_path,
            'session_id': SessionId,
            'start_time': datetime.now(timezone.utc).isoformat(),
            'process_id': os.getpid()
        }
        
        self.db_manager.register_terminal_session(SessionData)
        logger.info(f"Registered terminal session: {SessionId}")

    def _update_terminal_session_status(self, status: str) -> None:
        """Update terminal session status."""
        # This would update the session status in the database
        logger.debug(f"Terminal session status updated to: {status}")

    def _background_monitoring_loop(self) -> None:
        """Background loop for continuous monitoring and learning."""
        cleanup_counter = 0
        learning_counter = 0
        
        while self.is_running:
            try:
                # Periodic cleanup (every 5 minutes)
                cleanup_counter += 1
                if cleanup_counter >= 300:  # 5 minutes * 60 seconds / 1 second interval
                    self._perform_maintenance()
                    cleanup_counter = 0
                
                # Learning updates (every minute)
                learning_counter += 1
                if learning_counter >= 60:  # 1 minute
                    self._update_learning_algorithms()
                    learning_counter = 0
                
                # Sleep for 1 second
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in background monitoring loop: {e}", exc_info=True)
                time.sleep(5)  # Wait longer on error

    def _perform_maintenance(self) -> None:
        """Perform periodic maintenance tasks."""
        try:
            # Clean up old sessions
            self.proxy_monitor.cleanup_old_sessions()
            
            # Clean up old database data
            self.db_manager.cleanup_old_data(days_to_keep=30)
            
            logger.debug("Maintenance tasks completed")
            
        except Exception as e:
            logger.error(f"Error during maintenance: {e}", exc_info=True)

    def _update_learning_algorithms(self) -> None:
        """Update and improve learning algorithms based on recent data."""
        try:
            # Get recent session analytics
            analytics = self.db_manager.get_session_analytics(
                ProjectPath=self.current_project_path
            )
            
            # Analyze learning performance
            learning_perf = self.db_manager.get_learning_performance()
            
            # Update learning statistics
            self.learning_stats['last_learning_update'] = datetime.now(timezone.utc).isoformat()
            
            # Log learning progress
            if learning_perf['summary'].get('total_predictions', 0) > 0:
                accuracy = learning_perf['summary'].get('average_accuracy', 0)
                logger.debug(f"Learning algorithm accuracy: {accuracy:.2%}")
            
        except Exception as e:
            logger.error(f"Error updating learning algorithms: {e}", exc_info=True)

    def get_real_time_status(self) -> Dict[str, Any]:
        """Get comprehensive real-time monitoring status."""
        try:
            # Get proxy monitor statistics
            proxy_stats = self.proxy_monitor.get_session_statistics()
            
            # Get database analytics
            session_analytics = self.db_manager.get_session_analytics()
            
            # Get multi-terminal stats
            terminal_stats = self.db_manager.get_multi_terminal_stats()
            
            # Get learning performance
            learning_perf = self.db_manager.get_learning_performance()
            
            return {
                'system_status': {
                    'is_running': self.is_running,
                    'terminal_id': self.terminal_id,
                    'current_project': self.current_project_path,
                    'uptime_seconds': time.time() - (self.proxy_monitor.active_sessions.get(
                        list(self.proxy_monitor.active_sessions.keys())[0], 
                        type('obj', (object,), {'start_time': time.time()})()
                    ).StartTime if self.proxy_monitor.active_sessions else time.time())
                },
                'monitoring_stats': proxy_stats,
                'session_analytics': session_analytics,
                'terminal_coordination': terminal_stats,
                'learning_performance': learning_perf,
                'learning_stats': self.learning_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time status: {e}", exc_info=True)
            return {'system_status': {'is_running': self.is_running, 'error': str(e)}}

    def get_intelligent_plan_recommendation(self, current_usage: Dict[str, Any]) -> Dict[str, Any]:
        """Get intelligent plan recommendation based on usage patterns and learned limits."""
        try:
            # Analyze current usage patterns
            current_tokens = current_usage.get('total_tokens', 0)
            current_messages = current_usage.get('message_count', 0)
            session_duration = current_usage.get('elapsed_time', 0)
            
            # Get learned limits for all plans
            learned_limits = {}
            for plan_type in ['pro', 'max5', 'max20', 'custom']:
                limits = self.db_manager.get_plan_limit(plan_type)
                if limits:
                    learned_limits[plan_type] = limits
            
            # Analyze fit for each plan type
            plan_analysis = {}
            for plan_name, limits in learned_limits.items():
                token_utilization = current_tokens / limits.get('token_limit', 1)
                message_utilization = current_messages / limits.get('message_limit', 1)
                
                plan_analysis[plan_name] = {
                    'token_utilization': min(token_utilization, 1.0),
                    'message_utilization': min(message_utilization, 1.0),
                    'overall_fit': 1.0 - max(token_utilization, message_utilization),
                    'confidence': limits.get('confidence_score', 0.5),
                    'limits': limits
                }
            
            # Find best recommendation
            best_plan = max(plan_analysis.items(), 
                          key=lambda x: x[1]['overall_fit'] * x[1]['confidence'])
            
            return {
                'recommended_plan': best_plan[0],
                'confidence': best_plan[1]['confidence'],
                'reason': self._generate_recommendation_reason(best_plan[0], best_plan[1]),
                'all_plans_analysis': plan_analysis,
                'usage_projection': self._project_usage_trajectory(current_usage, session_duration)
            }
            
        except Exception as e:
            logger.error(f"Error generating plan recommendation: {e}", exc_info=True)
            return {'recommended_plan': 'custom', 'confidence': 0.0, 'error': str(e)}

    def _generate_recommendation_reason(self, plan_name: str, analysis: Dict[str, Any]) -> str:
        """Generate human-readable reason for plan recommendation."""
        token_util = analysis['token_utilization']
        message_util = analysis['message_utilization']
        
        if token_util < 0.5 and message_util < 0.5:
            return f"Your usage is well within {plan_name} limits with comfortable headroom"
        elif token_util < 0.8 and message_util < 0.8:
            return f"Your usage fits {plan_name} plan with moderate utilization"
        elif max(token_util, message_util) < 0.95:
            return f"Your usage is approaching {plan_name} limits but still within range"
        else:
            return f"Your usage is at the edge of {plan_name} limits - consider upgrade"

    def _project_usage_trajectory(self, current_usage: Dict[str, Any], session_duration: float) -> Dict[str, Any]:
        """Project usage trajectory for session planning."""
        if session_duration < 300:  # Less than 5 minutes - not enough data
            return {'projection': 'insufficient_data'}
        
        # Calculate usage rates
        tokens_per_hour = (current_usage.get('total_tokens', 0) / session_duration) * 3600
        messages_per_hour = (current_usage.get('message_count', 0) / session_duration) * 3600
        
        # Project for common session lengths
        projections = {}
        for hours in [1, 2, 4, 8]:
            projections[f'{hours}h'] = {
                'projected_tokens': int(tokens_per_hour * hours),
                'projected_messages': int(messages_per_hour * hours)
            }
        
        return {
            'projection': 'calculated',
            'current_rates': {
                'tokens_per_hour': tokens_per_hour,
                'messages_per_hour': messages_per_hour
            },
            'projections': projections
        }

    def export_comprehensive_report(self, output_path: Optional[Path] = None) -> Path:
        """Export comprehensive monitoring report."""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = Path.home() / ".claude-monitor" / f"comprehensive_report_{timestamp}.json"
        
        try:
            # Get all analytics data
            report_data = {
                'report_metadata': {
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'terminal_id': self.terminal_id,
                    'project_path': self.current_project_path,
                    'orchestrator_version': '1.0'
                },
                'real_time_status': self.get_real_time_status(),
                'learning_performance': self.db_manager.get_learning_performance(),
                'multi_terminal_coordination': self.db_manager.get_multi_terminal_stats(),
                'session_analytics': self.db_manager.get_session_analytics()
            }
            
            # Export database analytics
            self.db_manager.export_analytics_data(output_path)
            
            logger.info(f"Comprehensive report exported to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting comprehensive report: {e}", exc_info=True)
            raise

    def __enter__(self):
        """Context manager entry."""
        self.start_intelligent_monitoring()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_intelligent_monitoring()