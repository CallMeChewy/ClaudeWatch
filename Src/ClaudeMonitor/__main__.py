# File: Main.py
# Path: /home/herb/Desktop/ClaudeWatch/Src/ClaudeMonitor/__main__.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 04:24AM

"""Module execution entry point for Claude Monitor.

Allows running the package as a module: python -m claude_monitor
"""

import sys
from typing import NoReturn

from .cli.main import main


def _main() -> NoReturn:
    """Entry point that properly handles exit codes and never returns."""
    exit_code = main()
    sys.exit(exit_code)


if __name__ == "__main__":
    _main()
