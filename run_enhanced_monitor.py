# File: run_enhanced_monitor.py
# Path: /home/herb/Desktop/ClaudeWatch/run_enhanced_monitor.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 08:07AM

"""Production script for running the Enhanced Claude Monitor."""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from claude_monitor.cli.enhanced_main import main

if __name__ == "__main__":
    print("🚀 Enhanced Claude Code Usage Monitor")
    print("Intelligent monitoring with real-time learning")
    print("=" * 50)
    
    exit_code = main()
    sys.exit(exit_code)