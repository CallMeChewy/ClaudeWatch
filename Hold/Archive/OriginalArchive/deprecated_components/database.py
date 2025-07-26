"""Database management for Claude Monitor."""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages the SQLite database for storing monitoring data."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Initialize the database manager."""
        if db_path is None:
            db_path = Path.home() / ".claude-monitor" / "monitor.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a new database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usage_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        input_tokens INTEGER NOT NULL,
                        output_tokens INTEGER NOT NULL,
                        cost_usd REAL NOT NULL,
                        model TEXT NOT NULL,
                        message_id TEXT UNIQUE NOT NULL,
                        request_id TEXT NOT NULL,
                        session_id TEXT
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rate_limit_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL, -- 'approaching' or 'reached'
                        session_id TEXT,
                        elapsed_time REAL
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS plan_limits (
                        plan_name TEXT PRIMARY KEY,
                        token_limit INTEGER,
                        message_limit INTEGER,
                        last_updated TEXT NOT NULL
                    )
                """)
                conn.commit()
                logger.info("Database tables created or verified successfully.")
        except sqlite3.Error as e:
            logger.error(f"Database error during table creation: {e}", exc_info=True)

    def add_usage_entry(self, entry: Dict[str, Any]) -> None:
        """Add a single usage entry to the database."""
        sql = """
            INSERT OR IGNORE INTO usage_entries 
            (timestamp, input_tokens, output_tokens, cost_usd, model, message_id, request_id, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self._get_connection() as conn:
                conn.execute(sql, (
                    entry['timestamp'].isoformat(),
                    entry['input_tokens'],
                    entry['output_tokens'],
                    entry['cost_usd'],
                    entry['model'],
                    entry['message_id'],
                    entry['request_id'],
                    entry.get('session_id')
                ))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to add usage entry: {e}", exc_info=True)

    def add_rate_limit_event(self, event_type: str, session_id: str, elapsed_time: float) -> None:
        """Log a rate limit event."""
        sql = """
            INSERT INTO rate_limit_events (timestamp, event_type, session_id, elapsed_time)
            VALUES (datetime('now'), ?, ?, ?)
        """
        try:
            with self._get_connection() as conn:
                conn.execute(sql, (event_type, session_id, elapsed_time))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to log rate limit event: {e}", exc_info=True)

    def update_plan_limit(self, plan_name: str, token_limit: int, message_limit: int) -> None:
        """Update or insert a learned plan limit."""
        sql = """
            INSERT OR REPLACE INTO plan_limits (plan_name, token_limit, message_limit, last_updated)
            VALUES (?, ?, ?, datetime('now'))
        """
        try:
            with self._get_connection() as conn:
                conn.execute(sql, (plan_name, token_limit, message_limit))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to update plan limit for {plan_name}: {e}", exc_info=True)

    def get_plan_limit(self, plan_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a learned plan limit."""
        sql = "SELECT token_limit, message_limit FROM plan_limits WHERE plan_name = ?"
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(sql, (plan_name,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve plan limit for {plan_name}: {e}", exc_info=True)
            return None

    def get_all_usage_entries(self) -> List[Dict[str, Any]]:
        """Retrieve all usage entries."""
        sql = "SELECT * FROM usage_entries ORDER BY timestamp"
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(sql)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve usage entries: {e}", exc_info=True)
            return []
