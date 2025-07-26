#!/usr/bin/env python3
# File: QuickLauncher.py
# Path: Scripts/Common/QuickLauncher.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-07-17
# Last Modified: 2025-07-21  04:55PM
# Symlink Pattern: PROJECT_TOOL

"""
SYMLINK-AWARE Ultra-simple script launcher for common tasks
Perfect for VS Code right-click execution.

Symlink Behavior: 
- Designed to work correctly when accessed via symlink
- Pattern: PROJECT_TOOL (works in current directory context)
- Context: Finds Scripts/Common relative to current project, not script location
"""

import os
import subprocess
import sys
from pathlib import Path

def get_execution_context():
    """
    Symlink-aware context detection following Design Standard v2.3
    
    Returns:
        dict: Execution context information
    """
    context = {
        'working_directory': os.getcwd(),
        'project_name': os.path.basename(os.getcwd()),
        'script_path': sys.argv[0],
        'is_symlinked': Path(sys.argv[0]).is_symlink() if Path(sys.argv[0]).exists() else False,
        'script_real_location': Path(sys.argv[0]).resolve() if Path(sys.argv[0]).exists() else None
    }
    
    # CRITICAL: For project tools, ALWAYS work in current directory (Reality)
    return context

def find_scripts_common_dir():
    """Find Scripts/Common directory relative to current project"""
    current_dir = Path.cwd()
    
    # Try common project patterns
    possible_paths = [
        current_dir / "Scripts" / "Common",  # From project root
        current_dir / "Common",              # From Scripts directory
        current_dir,                         # Already in Common directory
        current_dir.parent / "Common"        # From subdirectory of Scripts
    ]
    
    for path in possible_paths:
        if path.exists() and (path / "QuickLauncher.py").exists():
            return path
    
    # Fallback: assume we're in the right place
    return Path.cwd()

def main():
    """Quick launcher with most common scripts"""
    
    print("🚀 QUICK SCRIPT LAUNCHER")
    print("=" * 40)
    print("1. 📋 List files by date")
    print("2. 🌳 Show project tree")
    print("3. 🔍 Search for text")
    print("4. 💾 Backup project")
    print("5. 📊 Project summary")
    print("6. 🐙 GitHub auto-update")
    print("7. 🔧 Debug .gitignore")
    print("8. 📝 Full menu system")
    print("0. Exit")
    print("=" * 40)
    
    choice = input("Choose (0-8): ").strip()
    
    # SYMLINK-AWARE: Find script directory relative to current context
    script_dir = find_scripts_common_dir()
    
    scripts = {
        "1": "FinderDisplay/ListFilesByDate.py",
        "2": "FinderDisplay/SimpleTree.py", 
        "3": "FinderDisplay/FindText.py",
        "4": "System/BackupProject.py",
        "5": "System/CodebaseSum.py",
        "6": "GitHub/GitHubAutoUpdate.py",
        "7": "Tools/VerifyIgnore.py",
        "8": "ScriptMenu.py"
    }
    
    if choice == "0":
        print("👋 Done!")
        return
    
    if choice in scripts:
        script_path = script_dir / scripts[choice]
        
        if script_path.exists():
            print(f"🚀 Running {script_path.name}...")
            
            # Special handling for search
            if choice == "3":
                search_term = input("🔍 Search for: ").strip()
                if search_term:
                    subprocess.run([sys.executable, str(script_path), search_term])
            elif choice == "6":
                confirm = input("⚠️ This will commit/push to GitHub. Continue? (y/n): ")
                if confirm.lower() in ['y', 'yes']:
                    subprocess.run([sys.executable, str(script_path)])
            else:
                subprocess.run([sys.executable, str(script_path)])
        else:
            print(f"❌ Script not found: {script_path}")
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
