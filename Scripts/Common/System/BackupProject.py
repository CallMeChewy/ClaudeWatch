#!/usr/bin/env python3
# File: BackupProject.py
# Path: Scripts/System/BackupProject.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-06-20
# Last Modified: 2025-07-19

"""
Project backup script that respects .gitignore files by using Git to list files.
"""

import os
import shutil
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def get_files_to_backup(project_root):
    """Use Git to get a list of all files to be backed up."""
    files = []
    
    # Get tracked files
    tracked_files_proc = subprocess.run(
        ['git', 'ls-files'], 
        cwd=project_root, 
        capture_output=True, 
        text=True
    )
    if tracked_files_proc.returncode == 0:
        files.extend(tracked_files_proc.stdout.strip().split('\n'))

    # Get untracked files (that are not ignored)
    untracked_files_proc = subprocess.run(
        ['git', 'ls-files', '--others', '--exclude-standard'], 
        cwd=project_root, 
        capture_output=True, 
        text=True
    )
    if untracked_files_proc.returncode == 0:
        files.extend(untracked_files_proc.stdout.strip().split('\n'))
        
    # Filter out empty strings that can result from empty output
    return [f for f in files if f]

def backup_project(project_name=None):
    """Backup the current project using Git to list files."""
    src_dir = Path(os.getcwd())
    if not project_name:
        project_name = src_dir.name

    backup_dir = Path.home() / "Desktop" / "Projects_Backup"
    date_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{project_name}_{date_stamp}"
    
    if backup_path.exists():
        shutil.rmtree(backup_path)
    
    print(f"Backing up project: {project_name}")
    
    try:
        files_to_copy = get_files_to_backup(src_dir)
        if not files_to_copy:
            print("No files to back up. Is this a git repository?")
            return None

        print(f"Found {len(files_to_copy)} files to back up.")

        for file_path_str in files_to_copy:
            source_file_path = src_dir / file_path_str
            dest_file_path = backup_path / file_path_str
            
            # Create parent directories in the destination
            dest_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if source_file_path.is_file():
                shutil.copy2(source_file_path, dest_file_path)

        print(f"Project backed up to: {backup_path}")
        return str(backup_path)
    except Exception as e:
        print(f"Error during backup: {e}")
        # Clean up partial backup
        if backup_path.exists():
            shutil.rmtree(backup_path)
        return None

def main():
    """Main entry point"""
    project_name = None
    if len(sys.argv) > 1:
        project_name = sys.argv[1]
    
    backup_project(project_name)

if __name__ == "__main__":
    main()
