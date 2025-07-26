# File: RunEnhancedMonitor.py
# Path: /home/herb/Desktop/ClaudeWatch/RunEnhancedMonitor.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-2                                                                                                                                   ;olsd6
# Last Modified: 2025-07-26 10:51AM

"""Production script for running the Enhanced Claude Monitor."""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "Src"))

from ClaudeMonitor.Cli.EnhancedMain import main

if __name__ == "__main__":
    print("🚀 Enhanced Claude Code Usage Monitor")
    print("Intelligent monitoring with real-time learning")
    print("=" * 50)
    
    ExitCode = main()
    sys.exit(ExitCode)