# File: enhanced_proxy_monitor.py
# Path: /home/herb/Desktop/ClaudeWatch/src/claude_monitor/monitoring/enhanced_proxy_monitor.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-01-26
# Last Modified: 2025-01-26 06:15PM

"""Enhanced proxy monitor with real-time MCP log monitoring and intelligent learning."""

import json
import logging
import re
import time
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from claude_monitor.data.enhanced_database import EnhancedDatabaseManager as DatabaseManager

logger = logging.getLogger(__name__)


class MCPLogHandler(FileSystemEventHandler):
    """Handles MCP log file events for real-time monitoring."""

    def __init__(self, monitor: 'EnhancedProxyMonitor'):
        """Initialize the MCP log handler."""
        self.monitor = monitor
        self.processed_files: Set[str] = set()

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        if event.src_path.endswith('.txt') and 'mcp-logs' in event.src_path:
            self.monitor._process_mcp_log_file(Path(event.src_path))

    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        if event.src_path.endswith('.txt') and 'mcp-logs' in event.src_path:
            self.monitor._process_mcp_log_file(Path(event.src_path))


class RateLimitPatterns:
    """Advanced pattern matching for rate limit messages."""
    
    # Comprehensive rate limit patterns based on actual Claude API responses
    APPROACHING_PATTERNS = [
        r"approaching.*rate\s*limit.*?(\d+).*?tokens?",
        r"usage.*warning.*?(\d+).*?remaining",
        r"rate\s*limit.*?approaching.*?(\d+)",
        r"token.*?usage.*?high.*?(\d+)",
        r"(\d+).*?tokens?.*?remaining.*?session",
    ]
    
    REACHED_PATTERNS = [
        r"rate\s*limit.*?reached.*?(\d+)",
        r"limit.*?exceeded.*?(\d+).*?tokens?",
        r"maximum.*?usage.*?reached.*?(\d+)",
        r"session.*?limit.*?hit.*?(\d+)",
        r"quota.*?exhausted.*?(\d+)",
        r"limit reached\|(\d+)",
    ]
    
    MESSAGE_LIMIT_PATTERNS = [
        r"message.*?limit.*?reached.*?(\d+)",
        r"conversation.*?limit.*?exceeded.*?(\d+)",
        r"(\d+).*?messages?.*?limit.*?reached",
    ]

    @classmethod
    def extract_rate_limit_info(cls, text: str) -> Optional[Dict[str, Any]]:
        """Extract rate limit information from text using advanced patterns."""
        text_lower = text.lower()
        
        # Check for approaching limits
        for pattern in cls.APPROACHING_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return {
                    'type': 'approaching',
                    'limit_value': int(match.group(1)) if match.group(1).isdigit() else None,
                    'raw_text': text.strip(),
                    'pattern_matched': pattern
                }
        
        # Check for reached limits
        for pattern in cls.REACHED_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return {
                    'type': 'reached',
                    'limit_value': int(match.group(1)) if match.group(1).isdigit() else None,
                    'raw_text': text.strip(),
                    'pattern_matched': pattern
                }
        
        # Check for message limits
        for pattern in cls.MESSAGE_LIMIT_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return {
                    'type': 'message_limit',
                    'limit_value': int(match.group(1)) if match.group(1).isdigit() else None,
                    'raw_text': text.strip(),
                    'pattern_matched': pattern
                }
        
        return None


class SessionMetrics:
    """Tracks detailed session metrics for learning."""
    
    def __init__(self, session_id: str, project_path: str):
        """Initialize session metrics."""
        self.session_id = session_id
        self.project_path = project_path
        self.start_time = time.time()
        self.token_usage: List[int] = []
        self.message_count = 0
        self.cost_accumulator = 0.0
        self.rate_limit_events: List[Dict[str, Any]] = []
        self.peak_token_usage = 0
        self.peak_message_count = 0

    def add_token_usage(self, tokens: int):
        """Add token usage data point."""
        self.token_usage.append(tokens)
        self.peak_token_usage = max(self.peak_token_usage, tokens)

    def add_message(self):
        """Increment message count."""
        self.message_count += 1
        self.peak_message_count = max(self.peak_message_count, self.message_count)

    def add_rate_limit_event(self, event_data: Dict[str, Any]):
        """Add a rate limit event."""
        event_data['timestamp'] = time.time()
        event_data['elapsed_time'] = time.time() - self.start_time
        self.rate_limit_events.append(event_data)

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current session metrics."""
        return {
            'session_id': self.session_id,
            'project_path': self.project_path,
            'elapsed_time': time.time() - self.start_time,
            'total_tokens': sum(self.token_usage),
            'peak_token_usage': self.peak_token_usage,
            'message_count': self.message_count,
            'peak_message_count': self.peak_message_count,
            'rate_limit_events': len(self.rate_limit_events),
            'cost_estimate': self.cost_accumulator
        }


class EnhancedProxyMonitor:
    """Enhanced proxy monitor with real-time MCP log monitoring and intelligent learning."""

    def __init__(self, db_manager: DatabaseManager, cache_path: Optional[str] = None):
        """Initialize the enhanced proxy monitor."""
        self.db_manager = db_manager
        self.cache_path = Path(cache_path) if cache_path else Path.home() / ".cache" / "claude-cli-nodejs"
        
        # Session tracking
        self.active_sessions: Dict[str, SessionMetrics] = {}
        self.session_lock = threading.Lock()
        
        # File monitoring
        self.observer = Observer()
        self.log_handler = MCPLogHandler(self)
        self._setup_file_monitoring()
        
        # Pattern matching
        self.patterns = RateLimitPatterns()
        
        # Statistics for learning
        self.learned_limits: Dict[str, Dict[str, int]] = {}
        self._load_learned_limits()

    def _setup_file_monitoring(self):
        """Setup real-time file monitoring for MCP logs."""
        if self.cache_path.exists():
            self.observer.schedule(self.log_handler, str(self.cache_path), recursive=True)
            logger.info(f"Started monitoring MCP logs at {self.cache_path}")
        else:
            logger.warning(f"MCP log path does not exist: {self.cache_path}")

    def start_monitoring(self):
        """Start the file monitoring system."""
        self.observer.start()
        logger.info("Enhanced proxy monitor started")

    def stop_monitoring(self):
        """Stop the file monitoring system."""
        self.observer.stop()
        self.observer.join()
        logger.info("Enhanced proxy monitor stopped")

    def get_session_id_from_path(self, file_path: Path) -> str:
        """Extract session ID from MCP log file path."""
        # Extract project path from directory structure
        # Example: /-home-herb-Desktop-ClaudeWatch/ -> /home/herb/Desktop/ClaudeWatch
        path_str = str(file_path)
        
        # Look for encoded project paths in the file path
        parts = file_path.parts
        for part in parts:
            if part.startswith('-home-') and (part.endswith('-') or 'mcp-logs' in path_str):
                # Convert encoded path back to normal path
                # Remove leading/trailing dashes and convert internal dashes to slashes
                clean_part = part.strip('-')
                project_path = '/' + clean_part.replace('-', '/')  # Add leading slash
                timestamp = file_path.stem  # Filename without extension
                return f"{project_path}#{timestamp}"
        
        # Fallback to file path if pattern not matched
        return str(file_path)

    def _process_mcp_log_file(self, file_path: Path):
        """Process an MCP log file for rate limit information."""
        try:
            session_id = self.get_session_id_from_path(file_path)
            
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Look for rate limit patterns in the content
            for line in content.split('\n'):
                rate_limit_info = self.patterns.extract_rate_limit_info(line)
                if rate_limit_info:
                    self._handle_rate_limit_event(session_id, file_path, rate_limit_info)
                
        except Exception as e:
            logger.error(f"Error processing MCP log file {file_path}: {e}")

    def _handle_rate_limit_event(self, session_id: str, file_path: Path, rate_limit_info: Dict[str, Any]):
        """Handle a detected rate limit event."""
        with self.session_lock:
            # Get or create session metrics
            if session_id not in self.active_sessions:
                project_path = self._extract_project_path(file_path)
                self.active_sessions[session_id] = SessionMetrics(session_id, project_path)
            
            session = self.active_sessions[session_id]
            session.add_rate_limit_event(rate_limit_info)
            
            # Log to database
            self.db_manager.add_rate_limit_event(
                event_type=rate_limit_info['type'],
                session_id=session_id,
                elapsed_time=session.get_current_metrics()['elapsed_time']
            )
            
            # Update learned limits based on this event
            self._update_intelligent_limits(session, rate_limit_info)
            
            logger.info(f"Rate limit event detected: {rate_limit_info['type']} in session {session_id}")

    def _extract_project_path(self, file_path: Path) -> str:
        """Extract the project path from MCP log file path."""
        parts = file_path.parts
        for i, part in enumerate(parts):
            if part.startswith('-home-') and part.endswith('-'):
                return part[1:-1].replace('-', '/')
        return str(file_path.parent)

    def _update_intelligent_limits(self, session: SessionMetrics, rate_limit_info: Dict[str, Any]):
        """Update learned limits using intelligent analysis instead of fixed reduction."""
        try:
            project_path = session.project_path
            current_metrics = session.get_current_metrics()
            
            # Determine plan type based on usage patterns
            plan_type = self._determine_plan_type(current_metrics)
            
            if rate_limit_info['type'] in ['reached', 'approaching']:
                # Use the actual limit value if extracted from the message
                if rate_limit_info.get('limit_value'):
                    observed_limit = rate_limit_info['limit_value']
                    
                    # Store learned limit with statistical confidence
                    self._store_learned_limit(
                        plan_type=plan_type,
                        limit_type='token',
                        observed_value=observed_limit,
                        session_metrics=current_metrics
                    )
                    
            elif rate_limit_info['type'] == 'message_limit':
                if rate_limit_info.get('limit_value'):
                    observed_limit = rate_limit_info['limit_value']
                    
                    self._store_learned_limit(
                        plan_type=plan_type,
                        limit_type='message',
                        observed_value=observed_limit,
                        session_metrics=current_metrics
                    )
            
        except Exception as e:
            logger.error(f"Error updating intelligent limits: {e}")

    def _determine_plan_type(self, metrics: Dict[str, Any]) -> str:
        """Determine plan type based on usage patterns."""
        peak_tokens = metrics.get('peak_token_usage', 0)
        
        # Use observed usage patterns to determine plan type
        if peak_tokens > 150000:
            return 'max20'
        elif peak_tokens > 60000:
            return 'max5'
        elif peak_tokens > 15000:
            return 'pro'
        else:
            return 'custom'

    def _store_learned_limit(self, plan_type: str, limit_type: str, observed_value: int, session_metrics: Dict[str, Any]):
        """Store learned limit with statistical analysis."""
        # Get existing learned limits for this plan
        existing_limits = self.db_manager.get_plan_limit(plan_type) or {}
        
        # Calculate confidence-weighted average with new observation
        existing_value = existing_limits.get(f'{limit_type}_limit', observed_value)
        
        # Simple weighted average - could be enhanced with more sophisticated ML
        confidence = min(session_metrics.get('elapsed_time', 0) / 3600, 1.0)  # Higher confidence with longer sessions
        new_value = int(existing_value * (1 - confidence) + observed_value * confidence)
        
        # Update database
        if limit_type == 'token':
            self.db_manager.update_plan_limit(
                plan_name=plan_type,
                token_limit=new_value,
                message_limit=existing_limits.get('message_limit', 250)
            )
        else:
            self.db_manager.update_plan_limit(
                plan_name=plan_type,
                token_limit=existing_limits.get('token_limit', 19000),
                message_limit=new_value
            )
        
        logger.info(f"Updated learned {limit_type} limit for {plan_type}: {new_value}")

    def _load_learned_limits(self):
        """Load previously learned limits from database."""
        try:
            # Load all plan limits from database
            for plan_type in ['pro', 'max5', 'max20', 'custom']:
                limits = self.db_manager.get_plan_limit(plan_type)
                if limits:
                    self.learned_limits[plan_type] = limits
        except Exception as e:
            logger.error(f"Error loading learned limits: {e}")

    def get_session_statistics(self) -> Dict[str, Any]:
        """Get comprehensive session statistics."""
        with self.session_lock:
            stats = {
                'active_sessions': len(self.active_sessions),
                'total_rate_limit_events': sum(len(s.rate_limit_events) for s in self.active_sessions.values()),
                'learned_limits': self.learned_limits,
                'sessions': {}
            }
            
            for session_id, session in self.active_sessions.items():
                stats['sessions'][session_id] = session.get_current_metrics()
            
            return stats

    def cleanup_old_sessions(self, max_age_hours: int = 6):
        """Clean up old session data to prevent memory bloat."""
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        with self.session_lock:
            expired_sessions = [
                session_id for session_id, session in self.active_sessions.items()
                if session.start_time < cutoff_time
            ]
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
                logger.debug(f"Cleaned up expired session: {session_id}")

    def __enter__(self):
        """Context manager entry."""
        self.start_monitoring()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_monitoring()