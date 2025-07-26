# File: MultiSessionCoordinator.py
# Path: /home/herb/Desktop/ClaudeWatch/src/claude_monitor/monitoring/MultiSessionCoordinator.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 04:16AM

"""
Multi-session coordination system that manages independent Claude Code
monitoring sessions across different terminals, SSH connections, and contexts.
"""

import logging
import threading
import time
import os
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import json
from pathlib import Path

from claude_monitor.core.SessionDetector import SessionDetector, SessionContext
from claude_monitor.data.enhanced_database import EnhancedDatabaseManager
from claude_monitor.monitoring.enhanced_proxy_monitor import EnhancedProxyMonitor

logger = logging.getLogger(__name__)

@dataclass
class SessionMonitor:
    """Individual session monitor with its own context and state."""
    session_context: SessionContext
    proxy_monitor: EnhancedProxyMonitor
    db_manager: EnhancedDatabaseManager
    thread: Optional[threading.Thread] = None
    is_active: bool = True
    last_heartbeat: datetime = None
    rate_limit_count: int = 0
    session_stats: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now(timezone.utc)
        if self.session_stats is None:
            self.session_stats = {
                'tokens_processed': 0,
                'messages_sent': 0,
                'errors_encountered': 0,
                'start_time': datetime.now(timezone.utc)
            }

class MultiSessionCoordinator:
    """
    Coordinates multiple independent Claude Code monitoring sessions,
    ensuring proper isolation and resource management.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session_detector = SessionDetector()
        self.active_monitors: Dict[str, SessionMonitor] = {}
        self.coordinator_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.coordination_lock = threading.RLock()
        self.message_queue = queue.Queue()
        self.heartbeat_interval = 30  # seconds
        self.cleanup_interval = 300   # 5 minutes
        self.session_timeout = 3600   # 1 hour without heartbeat
        
        # Performance tracking
        self.coordination_stats = {
            'sessions_started': 0,
            'sessions_completed': 0,
            'conflicts_resolved': 0,
            'resources_shared': 0
        }
    
    def StartCoordination(self) -> SessionContext:
        """
        Start coordination system and return current session context.
        
        Returns:
            SessionContext for the current session
        """
        logger.info("Starting multi-session coordination...")
        
        # Detect current session
        current_session = self.session_detector.DetectCurrentSession()
        
        # Check if we already have a monitor for this session
        isolation_key = current_session.isolation_key
        
        with self.coordination_lock:
            if isolation_key in self.active_monitors:
                logger.info(f"Reusing existing monitor for session: {isolation_key}")
                monitor = self.active_monitors[isolation_key]
                monitor.last_heartbeat = datetime.now(timezone.utc)
                return monitor.session_context
            
            # Create new session monitor
            monitor = self._create_session_monitor(current_session)
            self.active_monitors[isolation_key] = monitor
            self.coordination_stats['sessions_started'] += 1
            
            # Start coordinator thread if not running
            if not self.is_running:
                self._start_coordinator_thread()
            
            # Start this session's monitoring
            self._start_session_monitoring(monitor)
            
            logger.info(f"Started new session monitor: {isolation_key}")
            logger.info(f"Total active sessions: {len(self.active_monitors)}")
            
            return current_session
    
    def StopCoordination(self, isolation_key: Optional[str] = None) -> None:
        """
        Stop coordination for specific session or all sessions.
        
        Args:
            isolation_key: If provided, stop only this session. Otherwise stop all.
        """
        with self.coordination_lock:
            if isolation_key:
                # Stop specific session
                if isolation_key in self.active_monitors:
                    self._stop_session_monitor(isolation_key)
                    logger.info(f"Stopped session monitor: {isolation_key}")
            else:
                # Stop all sessions
                logger.info("Stopping all session monitors...")
                session_keys = list(self.active_monitors.keys())
                for key in session_keys:
                    self._stop_session_monitor(key)
                
                # Stop coordinator thread
                self.is_running = False
                if self.coordinator_thread and self.coordinator_thread.is_alive():
                    self.coordinator_thread.join(timeout=5)
                
                logger.info("Multi-session coordination stopped")
    
    def GetActiveSessionsInfo(self) -> Dict[str, Any]:
        """Get information about all active sessions."""
        with self.coordination_lock:
            sessions_info = {}
            
            for isolation_key, monitor in self.active_monitors.items():
                context = monitor.session_context
                sessions_info[isolation_key] = {
                    'session_id': context.session_id,
                    'session_type': context.session_type,
                    'user': context.user,
                    'hostname': context.hostname,
                    'working_directory': context.working_directory,
                    'terminal_device': context.terminal_device,
                    'ssh_connection': context.ssh_connection,
                    'local_ip': context.local_ip,
                    'remote_ip': context.remote_ip,
                    'start_time': context.start_time.isoformat(),
                    'last_heartbeat': monitor.last_heartbeat.isoformat(),
                    'is_active': monitor.is_active,
                    'rate_limit_count': monitor.rate_limit_count,
                    'session_stats': monitor.session_stats
                }
            
            return {
                'active_sessions_count': len(self.active_monitors),
                'sessions': sessions_info,
                'coordination_stats': self.coordination_stats,
                'detector_summary': self.session_detector.GetSessionSummary()
            }
    
    def GetSessionStatus(self, isolation_key: str) -> Optional[Dict[str, Any]]:
        """Get detailed status for a specific session."""
        with self.coordination_lock:
            if isolation_key not in self.active_monitors:
                return None
            
            monitor = self.active_monitors[isolation_key]
            context = monitor.session_context
            
            # Get real-time status from proxy monitor
            proxy_status = {}
            try:
                if hasattr(monitor.proxy_monitor, 'get_monitoring_status'):
                    proxy_status = monitor.proxy_monitor.get_monitoring_status()
            except Exception as e:
                logger.warning(f"Failed to get proxy status for {isolation_key}: {e}")
            
            return {
                'session_context': {
                    'session_id': context.session_id,
                    'terminal_id': context.terminal_id,
                    'session_type': context.session_type,
                    'isolation_key': context.isolation_key,
                    'working_directory': context.working_directory,
                    'start_time': context.start_time.isoformat()
                },
                'monitor_status': {
                    'is_active': monitor.is_active,
                    'last_heartbeat': monitor.last_heartbeat.isoformat(),
                    'rate_limit_count': monitor.rate_limit_count,
                    'session_stats': monitor.session_stats
                },
                'proxy_status': proxy_status
            }
    
    def SendCoordinationMessage(self, message_type: str, data: Any, target_session: Optional[str] = None) -> None:
        """Send coordination message between sessions."""
        message = {
            'type': message_type,
            'data': data,
            'target': target_session,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': getattr(threading.current_thread(), 'session_key', 'coordinator')
        }
        
        self.message_queue.put(message)
        logger.debug(f"Sent coordination message: {message_type}")
    
    def _create_session_monitor(self, session_context: SessionContext) -> SessionMonitor:
        """Create a new session monitor for the given context."""
        # Create isolated database manager for this session
        # Use session-specific database path for true isolation
        session_db_path = Path.home() / ".claude-monitor" / f"session_{hash(session_context.isolation_key) % 10000}.db"
        db_manager = EnhancedDatabaseManager(session_db_path)
        
        # Create proxy monitor for this session
        proxy_monitor = EnhancedProxyMonitor(db_manager)
        
        # Configure proxy monitor for session-specific monitoring
        proxy_monitor.session_context = session_context
        
        return SessionMonitor(
            session_context=session_context,
            proxy_monitor=proxy_monitor,
            db_manager=db_manager,
            last_heartbeat=datetime.now(timezone.utc)
        )
    
    def _start_session_monitoring(self, monitor: SessionMonitor) -> None:
        """Start monitoring thread for a specific session."""
        def session_monitoring_loop():
            """Main monitoring loop for this session."""
            threading.current_thread().session_key = monitor.session_context.isolation_key
            
            try:
                logger.info(f"Starting monitoring for session: {monitor.session_context.isolation_key}")
                
                # Start proxy monitoring
                monitor.proxy_monitor.start_monitoring()
                
                # Session monitoring loop
                while monitor.is_active and self.is_running:
                    # Update heartbeat
                    monitor.last_heartbeat = datetime.now(timezone.utc)
                    
                    # Check for coordination messages
                    self._process_session_messages(monitor)
                    
                    # Update session stats
                    self._update_session_stats(monitor)
                    
                    # Sleep before next iteration
                    time.sleep(10)  # 10 second intervals
                    
            except Exception as e:
                logger.error(f"Session monitoring error for {monitor.session_context.isolation_key}: {e}", exc_info=True)
            finally:
                # Clean shutdown
                try:
                    monitor.proxy_monitor.stop_monitoring()
                except Exception as e:
                    logger.error(f"Error stopping proxy monitor: {e}")
                
                logger.info(f"Session monitoring stopped: {monitor.session_context.isolation_key}")
        
        # Start monitoring thread
        monitor.thread = threading.Thread(
            target=session_monitoring_loop,
            name=f"SessionMonitor-{monitor.session_context.isolation_key}",
            daemon=True
        )
        monitor.thread.start()
    
    def _start_coordinator_thread(self) -> None:
        """Start the main coordinator thread."""
        def coordination_loop():
            """Main coordination loop."""
            logger.info("Starting coordination thread...")
            
            last_cleanup = datetime.now(timezone.utc)
            
            while self.is_running:
                try:
                    # Process coordination messages
                    self._process_coordination_messages()
                    
                    # Periodic cleanup
                    now = datetime.now(timezone.utc)
                    if (now - last_cleanup).total_seconds() > self.cleanup_interval:
                        self._cleanup_inactive_sessions()
                        last_cleanup = now
                    
                    # Conflict resolution
                    self._resolve_session_conflicts()
                    
                    # Resource optimization
                    self._optimize_resource_sharing()
                    
                    time.sleep(self.heartbeat_interval)
                    
                except Exception as e:
                    logger.error(f"Coordination loop error: {e}", exc_info=True)
                    time.sleep(5)  # Brief pause before retry
            
            logger.info("Coordination thread stopped")
        
        self.is_running = True
        self.coordinator_thread = threading.Thread(
            target=coordination_loop,
            name="MultiSessionCoordinator",
            daemon=True
        )
        self.coordinator_thread.start()
    
    def _stop_session_monitor(self, isolation_key: str) -> None:
        """Stop a specific session monitor."""
        if isolation_key not in self.active_monitors:
            return
        
        monitor = self.active_monitors[isolation_key]
        monitor.is_active = False
        
        # Stop proxy monitoring
        try:
            monitor.proxy_monitor.stop_monitoring()
        except Exception as e:
            logger.error(f"Error stopping proxy monitor for {isolation_key}: {e}")
        
        # Wait for thread to finish
        if monitor.thread and monitor.thread.is_alive():
            monitor.thread.join(timeout=10)
        
        # Update stats
        monitor.session_stats['end_time'] = datetime.now(timezone.utc)
        self.coordination_stats['sessions_completed'] += 1
        
        # Remove from active monitors
        del self.active_monitors[isolation_key]
    
    def _process_coordination_messages(self) -> None:
        """Process messages in the coordination queue."""
        processed = 0
        
        while processed < 10:  # Limit processing per cycle
            try:
                message = self.message_queue.get_nowait()
                self._handle_coordination_message(message)
                processed += 1
            except queue.Empty:
                break
    
    def _handle_coordination_message(self, message: Dict[str, Any]) -> None:
        """Handle a specific coordination message."""
        message_type = message.get('type')
        
        if message_type == 'rate_limit_detected':
            self._handle_rate_limit_message(message)
        elif message_type == 'session_conflict':
            self._handle_session_conflict(message)
        elif message_type == 'resource_request':
            self._handle_resource_request(message)
        elif message_type == 'heartbeat':
            self._handle_heartbeat_message(message)
        else:
            logger.debug(f"Unknown coordination message type: {message_type}")
    
    def _handle_rate_limit_message(self, message: Dict[str, Any]) -> None:
        """Handle rate limit detection across sessions."""
        source_session = message.get('source')
        
        # Notify other sessions in the same project
        if source_session in self.active_monitors:
            source_monitor = self.active_monitors[source_session]
            project_path = source_monitor.session_context.working_directory
            
            for key, monitor in self.active_monitors.items():
                if key != source_session and monitor.session_context.working_directory == project_path:
                    # Notify session about rate limit in project
                    logger.info(f"Notifying session {key} about rate limit in {project_path}")
                    monitor.rate_limit_count += 1
    
    def _process_session_messages(self, monitor: SessionMonitor) -> None:
        """Process messages for a specific session."""
        # Implementation would depend on specific messaging needs
        pass
    
    def _update_session_stats(self, monitor: SessionMonitor) -> None:
        """Update statistics for a session."""
        # Get current stats from proxy monitor
        try:
            if hasattr(monitor.proxy_monitor, 'get_session_stats'):
                current_stats = monitor.proxy_monitor.get_session_stats()
                monitor.session_stats.update(current_stats)
        except Exception as e:
            logger.debug(f"Could not update session stats: {e}")
    
    def _cleanup_inactive_sessions(self) -> None:
        """Clean up sessions that are no longer active."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=self.session_timeout)
        inactive_keys = []
        
        with self.coordination_lock:
            for key, monitor in self.active_monitors.items():
                # Check if session process still exists
                if not self.session_detector.IsSessionActive(key):
                    inactive_keys.append(key)
                # Check heartbeat timeout
                elif monitor.last_heartbeat < cutoff_time:
                    inactive_keys.append(key)
                    logger.warning(f"Session {key} timed out (no heartbeat)")
        
        # Clean up inactive sessions
        for key in inactive_keys:
            logger.info(f"Cleaning up inactive session: {key}")
            self._stop_session_monitor(key)
    
    def _resolve_session_conflicts(self) -> None:
        """Resolve conflicts between sessions."""
        # Check for resource conflicts, duplicate monitoring, etc.
        conflicts_resolved = 0
        
        with self.coordination_lock:
            # Group sessions by project path
            project_sessions = {}
            for key, monitor in self.active_monitors.items():
                project = monitor.session_context.working_directory
                if project not in project_sessions:
                    project_sessions[project] = []
                project_sessions[project].append((key, monitor))
            
            # Check for conflicts within projects
            for project, sessions in project_sessions.items():
                if len(sessions) > 1:
                    conflicts_resolved += self._resolve_project_conflicts(project, sessions)
        
        if conflicts_resolved > 0:
            self.coordination_stats['conflicts_resolved'] += conflicts_resolved
    
    def _resolve_project_conflicts(self, project_path: str, sessions: List[Tuple[str, SessionMonitor]]) -> int:
        """Resolve conflicts between sessions in the same project."""
        # For now, just log the conflicts - in the future we could implement
        # more sophisticated conflict resolution
        logger.info(f"Multiple sessions detected for project {project_path}: {len(sessions)} sessions")
        
        # Could implement:
        # - Resource sharing coordination
        # - Load balancing
        # - Duplicate detection prevention
        # - Master/slave session coordination
        
        return 0
    
    def _optimize_resource_sharing(self) -> None:
        """Optimize resource sharing between sessions."""
        # Could implement:
        # - Shared database connections
        # - Shared file watchers for same directories
        # - Coordinated cleanup schedules
        # - Load distribution
        pass
    
    def ExportMultiSessionReport(self, output_path: Path) -> None:
        """Export comprehensive multi-session report."""
        with self.coordination_lock:
            report_data = {
                'export_time': datetime.now(timezone.utc).isoformat(),
                'active_sessions': self.GetActiveSessionsInfo(),
                'coordination_stats': self.coordination_stats,
                'session_detector_data': self.session_detector.GetSessionSummary()
            }
            
            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            logger.info(f"Multi-session report exported to {output_path}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.StopCoordination()