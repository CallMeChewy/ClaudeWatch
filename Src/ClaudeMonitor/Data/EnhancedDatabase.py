# File: EnhancedDatabase.py
# Path: /home/herb/Desktop/ClaudeWatch/Src/ClaudeMonitor/Data/EnhancedDatabase.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-01-26
# Last Modified: 2025-07-26 10:55AM

"""Enhanced database management with detailed session metrics and learning capabilities."""

import sqlite3
import logging
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class EnhancedDatabaseManager:
    """Enhanced database manager with comprehensive session tracking and analytics."""

    def __init__(self, DbPath: Optional[Path] = None) -> None:
        """Initialize the enhanced database manager."""
        if DbPath is None:
            DbPath = Path.home() / ".claude-monitor" / "enhanced_monitor.db"
        
        self.DbPath = DbPath
        self.DbPath.parent.mkdir(parents=True, exist_ok=True)
        self._create_enhanced_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a new database connection with enhanced settings."""
        conn = sqlite3.connect(self.DbPath)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        return conn

    def _create_enhanced_tables(self) -> None:
        """Create enhanced database tables for detailed session tracking."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Enhanced usage entries with session correlation
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usage_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        input_tokens INTEGER NOT NULL,
                        output_tokens INTEGER NOT NULL,
                        cache_creation_tokens INTEGER DEFAULT 0,
                        cache_read_tokens INTEGER DEFAULT 0,
                        cost_usd REAL NOT NULL,
                        model TEXT NOT NULL,
                        message_id TEXT UNIQUE NOT NULL,
                        request_id TEXT NOT NULL,
                        session_id TEXT,
                        project_path TEXT,
                        FOREIGN KEY (session_id) REFERENCES session_metrics (session_id)
                    )
                """)

                # Enhanced rate limit events with detailed context
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rate_limit_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL, -- 'approaching', 'reached', 'message_limit'
                        session_id TEXT NOT NULL,
                        elapsed_time REAL NOT NULL,
                        limit_value INTEGER, -- Actual limit value extracted from message
                        raw_message TEXT, -- Original rate limit message
                        pattern_matched TEXT, -- Which regex pattern matched
                        project_path TEXT,
                        confidence_score REAL DEFAULT 1.0,
                        FOREIGN KEY (session_id) REFERENCES session_metrics (session_id)
                    )
                """)

                # Enhanced plan limits with statistical confidence
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS plan_limits (
                        plan_name TEXT PRIMARY KEY,
                        token_limit INTEGER,
                        message_limit INTEGER,
                        last_updated TEXT NOT NULL,
                        confidence_score REAL DEFAULT 1.0,
                        sample_size INTEGER DEFAULT 1,
                        variance REAL DEFAULT 0.0
                    )
                """)

                # New: Comprehensive session metrics
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS session_metrics (
                        session_id TEXT PRIMARY KEY,
                        project_path TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        total_tokens INTEGER DEFAULT 0,
                        peak_token_usage INTEGER DEFAULT 0,
                        message_count INTEGER DEFAULT 0,
                        peak_message_count INTEGER DEFAULT 0,
                        cost_estimate REAL DEFAULT 0.0,
                        rate_limit_events_count INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'active', -- 'active', 'completed', 'interrupted'
                        metadata TEXT -- JSON field for additional data
                    )
                """)

                # New: Learning algorithm performance tracking
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS learning_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        plan_type TEXT NOT NULL,
                        predicted_limit INTEGER,
                        actual_limit INTEGER,
                        accuracy_score REAL,
                        session_id TEXT,
                        improvement_delta INTEGER,
                        algorithm_version TEXT DEFAULT '1.0'
                    )
                """)

                # New: Multi-terminal session correlation
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS terminal_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        terminal_id TEXT NOT NULL, -- Unique terminal identifier
                        project_path TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        last_activity TEXT NOT NULL,
                        process_id INTEGER,
                        FOREIGN KEY (session_id) REFERENCES session_metrics (session_id)
                    )
                """)

                # Create indexes for performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_session ON usage_entries(session_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_rate_limit_session ON rate_limit_events(session_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_project ON session_metrics(project_path)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_terminal_project ON terminal_sessions(project_path)")
                
                conn.commit()
                logger.info("Enhanced database tables created or verified successfully.")
                
        except sqlite3.Error as e:
            logger.error(f"Database error during enhanced table creation: {e}", exc_info=True)

    def add_enhanced_rate_limit_event(self, event_data: Dict[str, Any]) -> None:
        """Add a detailed rate limit event with full context."""
        sql = """
            INSERT INTO rate_limit_events 
            (timestamp, event_type, session_id, elapsed_time, limit_value, 
             raw_message, pattern_matched, project_path, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self._get_connection() as conn:
                conn.execute(sql, (
                    datetime.now(timezone.utc).isoformat(),
                    event_data['event_type'],
                    event_data['session_id'],
                    event_data['elapsed_time'],
                    event_data.get('limit_value'),
                    event_data.get('raw_message'),
                    event_data.get('pattern_matched'),
                    event_data.get('project_path'),
                    event_data.get('confidence_score', 1.0)
                ))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to add enhanced rate limit event: {e}", exc_info=True)

    def create_or_update_session_metrics(self, session_data: Dict[str, Any]) -> None:
        """Create or update comprehensive session metrics."""
        sql = """
            INSERT OR REPLACE INTO session_metrics 
            (session_id, project_path, start_time, end_time, total_tokens, 
             peak_token_usage, message_count, peak_message_count, cost_estimate, 
             rate_limit_events_count, status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self._get_connection() as conn:
                conn.execute(sql, (
                    session_data['session_id'],
                    session_data['project_path'],
                    session_data.get('start_time', datetime.now(timezone.utc).isoformat()),
                    session_data.get('end_time'),
                    session_data.get('total_tokens', 0),
                    session_data.get('peak_token_usage', 0),
                    session_data.get('message_count', 0),
                    session_data.get('peak_message_count', 0),
                    session_data.get('cost_estimate', 0.0),
                    session_data.get('rate_limit_events_count', 0),
                    session_data.get('status', 'active'),
                    json.dumps(session_data.get('metadata', {}))
                ))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to update session metrics: {e}", exc_info=True)

    def update_enhanced_plan_limit(self, plan_data: Dict[str, Any]) -> None:
        """Update plan limits with statistical confidence metrics."""
        sql = """
            INSERT OR REPLACE INTO plan_limits 
            (plan_name, token_limit, message_limit, last_updated, 
             confidence_score, sample_size, variance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self._get_connection() as conn:
                conn.execute(sql, (
                    plan_data['plan_name'],
                    plan_data['token_limit'],
                    plan_data['message_limit'],
                    datetime.now(timezone.utc).isoformat(),
                    plan_data.get('confidence_score', 1.0),
                    plan_data.get('sample_size', 1),
                    plan_data.get('variance', 0.0)
                ))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to update enhanced plan limit: {e}", exc_info=True)

    def get_plan_limit(self, plan_name: str) -> Optional[Dict[str, Any]]:
        """Get plan limits for the specified plan."""
        sql = """
            SELECT plan_name, token_limit, message_limit, last_updated, 
                   confidence_score, sample_size, variance
            FROM plan_limits 
            WHERE plan_name = ?
            ORDER BY last_updated DESC
            LIMIT 1
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(sql, (plan_name,))
                row = cursor.fetchone()
                if row:
                    return {
                        'plan_name': row[0],
                        'token_limit': row[1], 
                        'message_limit': row[2],
                        'last_updated': row[3],
                        'confidence_score': row[4],
                        'sample_size': row[5],
                        'variance': row[6]
                    }
                return None
        except sqlite3.Error as e:
            logger.error(f"Failed to get plan limit: {e}", exc_info=True)
            return None

    def add_learning_metric(self, learning_data: Dict[str, Any]) -> None:
        """Track learning algorithm performance."""
        sql = """
            INSERT INTO learning_metrics 
            (timestamp, plan_type, predicted_limit, actual_limit, accuracy_score, 
             session_id, improvement_delta, algorithm_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self._get_connection() as conn:
                conn.execute(sql, (
                    datetime.now(timezone.utc).isoformat(),
                    learning_data['plan_type'],
                    learning_data['predicted_limit'],
                    learning_data['actual_limit'],
                    learning_data.get('accuracy_score'),
                    learning_data.get('session_id'),
                    learning_data.get('improvement_delta'),
                    learning_data.get('algorithm_version', '1.0')
                ))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to add learning metric: {e}", exc_info=True)

    def register_terminal_session(self, terminal_data: Dict[str, Any]) -> None:
        """Register a new terminal session for multi-terminal tracking."""
        sql = """
            INSERT OR REPLACE INTO terminal_sessions 
            (terminal_id, project_path, session_id, start_time, last_activity, process_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            with self._get_connection() as conn:
                conn.execute(sql, (
                    terminal_data['terminal_id'],
                    terminal_data['project_path'],
                    terminal_data['session_id'],
                    terminal_data.get('start_time', datetime.now(timezone.utc).isoformat()),
                    datetime.now(timezone.utc).isoformat(),
                    terminal_data.get('process_id')
                ))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to register terminal session: {e}", exc_info=True)

    def get_session_analytics(self, session_id: Optional[str] = None, 
                            project_path: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive session analytics."""
        try:
            with self._get_connection() as conn:
                # Base query for session metrics
                base_query = "SELECT * FROM session_metrics"
                params = []
                
                if session_id:
                    base_query += " WHERE session_id = ?"
                    params.append(session_id)
                elif project_path:
                    base_query += " WHERE project_path = ?"
                    params.append(project_path)
                
                sessions = conn.execute(base_query, params).fetchall()
                
                analytics = {
                    'sessions': [dict(row) for row in sessions],
                    'summary': {
                        'total_sessions': len(sessions),
                        'active_sessions': 0,
                        'total_tokens': 0,
                        'total_rate_limit_events': 0
                    }
                }
                
                for session in sessions:
                    if session['status'] == 'active':
                        analytics['summary']['active_sessions'] += 1
                    analytics['summary']['total_tokens'] += session['total_tokens'] or 0
                    analytics['summary']['total_rate_limit_events'] += session['rate_limit_events_count'] or 0
                
                return analytics
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get session analytics: {e}", exc_info=True)
            return {'sessions': [], 'summary': {}}

    def get_learning_performance(self, plan_type: Optional[str] = None) -> Dict[str, Any]:
        """Get learning algorithm performance metrics."""
        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM learning_metrics"
                params = []
                
                if plan_type:
                    query += " WHERE plan_type = ?"
                    params.append(plan_type)
                
                query += " ORDER BY timestamp DESC LIMIT 100"
                
                metrics = conn.execute(query, params).fetchall()
                
                if not metrics:
                    return {'performance': [], 'summary': {}}
                
                # Calculate performance statistics
                accuracy_scores = [m['accuracy_score'] for m in metrics if m['accuracy_score']]
                avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
                
                return {
                    'performance': [dict(row) for row in metrics],
                    'summary': {
                        'total_predictions': len(metrics),
                        'average_accuracy': avg_accuracy,
                        'latest_improvement': metrics[0]['improvement_delta'] if metrics else 0
                    }
                }
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get learning performance: {e}", exc_info=True)
            return {'performance': [], 'summary': {}}

    def get_multi_terminal_stats(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """Get multi-terminal session statistics."""
        try:
            with self._get_connection() as conn:
                query = """
                    SELECT ts.*, sm.status, sm.total_tokens 
                    FROM terminal_sessions ts 
                    LEFT JOIN session_metrics sm ON ts.session_id = sm.session_id
                """
                params = []
                
                if project_path:
                    query += " WHERE ts.project_path = ?"
                    params.append(project_path)
                
                query += " ORDER BY ts.last_activity DESC"
                
                terminals = conn.execute(query, params).fetchall()
                
                # Group by project path
                projects = {}
                for terminal in terminals:
                    proj_path = terminal['project_path']
                    if proj_path not in projects:
                        projects[proj_path] = {
                            'terminals': [],
                            'active_count': 0,
                            'total_tokens': 0
                        }
                    
                    projects[proj_path]['terminals'].append(dict(terminal))
                    if terminal['status'] == 'active':
                        projects[proj_path]['active_count'] += 1
                    projects[proj_path]['total_tokens'] += terminal['total_tokens'] or 0
                
                return {
                    'projects': projects,
                    'summary': {
                        'total_terminals': len(terminals),
                        'unique_projects': len(projects),
                        'active_terminals': sum(p['active_count'] for p in projects.values())
                    }
                }
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get multi-terminal stats: {e}", exc_info=True)
            return {'projects': {}, 'summary': {}}

    def cleanup_old_data(self, days_to_keep: int = 30) -> None:
        """Clean up old data to prevent database bloat."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.isoformat()
        
        try:
            with self._get_connection() as conn:
                # Clean up old rate limit events
                conn.execute("DELETE FROM rate_limit_events WHERE timestamp < ?", (cutoff_str,))
                
                # Clean up old learning metrics
                conn.execute("DELETE FROM learning_metrics WHERE timestamp < ?", (cutoff_str,))
                
                # Clean up completed sessions older than cutoff
                conn.execute("""
                    DELETE FROM session_metrics 
                    WHERE status = 'completed' AND end_time < ?
                """, (cutoff_str,))
                
                # Clean up old terminal sessions
                conn.execute("DELETE FROM terminal_sessions WHERE last_activity < ?", (cutoff_str,))
                
                conn.commit()
                logger.info(f"Cleaned up data older than {days_to_keep} days")
                
        except sqlite3.Error as e:
            logger.error(f"Failed to cleanup old data: {e}", exc_info=True)

    def export_analytics_data(self, output_path: Path) -> None:
        """Export comprehensive analytics data for external analysis."""
        try:
            with self._get_connection() as conn:
                # Get all analytics data
                analytics = {
                    'session_metrics': [dict(row) for row in conn.execute("SELECT * FROM session_metrics").fetchall()],
                    'rate_limit_events': [dict(row) for row in conn.execute("SELECT * FROM rate_limit_events").fetchall()],
                    'plan_limits': [dict(row) for row in conn.execute("SELECT * FROM plan_limits").fetchall()],
                    'learning_metrics': [dict(row) for row in conn.execute("SELECT * FROM learning_metrics").fetchall()],
                    'terminal_sessions': [dict(row) for row in conn.execute("SELECT * FROM terminal_sessions").fetchall()],
                    'export_timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                # Write to JSON file
                with open(output_path, 'w') as f:
                    json.dump(analytics, f, indent=2)
                
                logger.info(f"Analytics data exported to {output_path}")
                
        except (sqlite3.Error, IOError) as e:
            logger.error(f"Failed to export analytics data: {e}", exc_info=True)