# File: Bootstrap.py
# Path: /home/herb/Desktop/ClaudeWatch/Src/ClaudeMonitor/Cli/Bootstrap.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 10:54AM

"""Bootstrap utilities for CLI initialization."""

import logging
import os
import sys
from logging import Handler
from pathlib import Path
from typing import List, Optional

from ClaudeMonitor.Utils.TimeUtils import TimezoneHandler


def SetupLogging(
    Level: str = "INFO", LogFile: Optional[Path] = None, DisableConsole: bool = False
) -> None:
    """Configure logging for the application.

    Args:
        Level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        LogFile: Optional file path for logging
        DisableConsole: If True, disable console logging (useful for monitor mode)
    """
    LogLevel = getattr(logging, Level.upper(), logging.INFO)

    Handlers: List[Handler] = []
    if not DisableConsole:
        Handlers.append(logging.StreamHandler(sys.stdout))
    if LogFile:
        Handlers.append(logging.FileHandler(LogFile))

    if not Handlers:
        Handlers.append(logging.NullHandler())

    logging.basicConfig(
        level=LogLevel,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=Handlers,
    )


def SetupEnvironment() -> None:
    """Initialize environment variables and system settings."""
    if sys.stdout.encoding != "utf-8":
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

    os.environ.setdefault(
        "CLAUDE_MONITOR_CONFIG", str(Path.home() / ".claude-monitor" / "config.yaml")
    )
    os.environ.setdefault(
        "CLAUDE_MONITOR_CACHE_DIR", str(Path.home() / ".claude-monitor" / "cache")
    )


def init_timezone(timezone: str = "Europe/Warsaw") -> TimezoneHandler:
    """Initialize timezone handler.

    Args:
        timezone: Timezone string (e.g. "Europe/Warsaw", "UTC")

    Returns:
        Configured TimezoneHandler instance
    """
    tz_handler = TimezoneHandler()
    if timezone != "Europe/Warsaw":
        tz_handler.set_timezone(timezone)
    return tz_handler


def EnsureDirectories() -> None:
    """Ensure required directories exist."""
    Dirs = [
        Path.home() / ".claude-monitor",
        Path.home() / ".claude-monitor" / "cache",
        Path.home() / ".claude-monitor" / "logs",
        Path.home() / ".claude-monitor" / "reports",
    ]

    for Directory in Dirs:
        Directory.mkdir(parents=True, exist_ok=True)
