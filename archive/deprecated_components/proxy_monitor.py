"""Proxy monitor for intercepting and handling CLI messages."""

import logging
import re
import time
from typing import Optional

from claude_monitor.data.database import DatabaseManager

logger = logging.getLogger(__name__)

class ProxyMonitor:
    """Monitors CLI output for rate-limit warnings and other messages."""

    def __init__(self, db_manager: DatabaseManager, session_id: str):
        """Initialize the proxy monitor."""
        self.db_manager = db_manager
        self.session_id = session_id
        self.start_time = time.time()

    def process_cli_output(self, output: str) -> None:
        """Process a chunk of CLI output."""
        if "approaching rate limit" in output.lower():
            self._log_rate_limit_event("approaching")
        elif "rate limit reached" in output.lower():
            self._log_rate_limit_event("reached")
        
        # Example of how to update learned limits
        # This would be more sophisticated in a real implementation
        if "rate limit reached" in output.lower():
            self._update_learned_limits()

    def _log_rate_limit_event(self, event_type: str) -> None:
        """Log a rate-limit event to the database."""
        elapsed_time = time.time() - self.start_time
        self.db_manager.add_rate_limit_event(
            event_type=event_type,
            session_id=self.session_id,
            elapsed_time=elapsed_time,
        )
        logger.info(f"Logged rate-limit event: {event_type} for session {self.session_id}")

    def _update_learned_limits(self) -> None:
        """Update learned plan limits based on observed events."""
        # This is a placeholder for a more complex learning algorithm.
        # For now, we'll just decrement the token limit by a fixed amount.
        plan_name = "pro" # This would be dynamically determined
        current_limits = self.db_manager.get_plan_limit(plan_name)
        
        if current_limits:
            new_token_limit = current_limits["token_limit"] * 0.95
            new_message_limit = current_limits["message_limit"] * 0.95
            
            self.db_manager.update_plan_limit(
                plan_name=plan_name,
                token_limit=int(new_token_limit),
                message_limit=int(new_message_limit),
            )
            logger.info(f"Updated learned limits for plan {plan_name}.")
