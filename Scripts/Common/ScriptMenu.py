#!/usr/bin/env python3
# File: ScriptMenu.py
# Path: Scripts/Common/ScriptMenu.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-07-17
# Last Modified: 2025-07-21  04:55PM
# Symlink Pattern: PROJECT_TOOL

"""
SYMLINK-AWARE Interactive menu system for Common Scripts
Makes script access human-friendly for VS Code workflow.

Symlink Behavior: 
- Designed to work correctly when accessed via symlink
- Pattern: PROJECT_TOOL (works in current directory context)
- Context: Operates relative to project Scripts/Common, not script location
"""

import os
import sys
import subprocess
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

class ScriptMenu:
    def __init__(self):
        # SYMLINK-AWARE: Use current working directory context, not script location
        current_dir = Path.cwd()
        
        # Find Scripts/Common directory relative to current project
        self.script_dir = None
        
        # Try common project patterns
        possible_paths = [
            current_dir / "Scripts" / "Common",  # From project root
            current_dir / "Common",              # From Scripts directory
            current_dir,                         # Already in Common directory
            current_dir.parent / "Common"        # From subdirectory of Scripts
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "ScriptMenu.py").exists():
                self.script_dir = path
                break
        
        if not self.script_dir:
            # Fallback: assume we're in the right place
            self.script_dir = Path.cwd()
            
        self.scripts = self._load_scripts()
    
    def _load_scripts(self):
        """Load and categorize all available scripts"""
        return {
            "🔧 System Maintenance": {
                "1": ("BackupProject.py", "System/BackupProject.py", "Full project backup to Desktop", "simple"),
                "2": ("BackupTemp.py", "System/BackupTemp.py", "Quick backup of specific directories", "simple"),
                "3": ("CodebaseSum.py", "System/CodebaseSum.py", "Generate complete project documentation", "simple"),
            },
            "📊 File Analysis": {
                "4": ("ListFilesByDate.py", "FinderDisplay/ListFilesByDate.py", "Show files by modification date", "simple"),
                "5": ("ListNewPy.py", "FinderDisplay/ListNewPy.py", "List Python files with details", "simple"),
                "6": ("SimpleTree.py", "FinderDisplay/SimpleTree.py", "Show directory structure", "simple"),
                "7": ("VerifyIgnore.py", "Tools/VerifyIgnore.py", "Debug .gitignore patterns", "simple"),
            },
            "🔍 Search Tools": {
                "8": ("FindText.py", "FinderDisplay/FindText.py", "Search for text in files", "prompt"),
                "9": ("FindTextTwo.py", "FinderDisplay/FindTextTwo.py", "Search for two phrases", "prompt"),
                "10": ("AdvancedFileSearcher.py", "FinderDisplay/AdvancedFileSearcher.py", "GUI search tool", "gui"),
            },
            "🌐 GitHub Operations": {
                "11": ("GitHubAutoUpdate.py", "GitHub/GitHubAutoUpdate.py", "Auto commit and push", "confirm"),
                "12": ("GitHubUpdateSite.py", "GitHub/GitHubUpdateSite.py", "Simple GitHub Pages update", "simple"),
                "13": ("GitHubInitialCommit.py", "GitHub/GitHubInitialCommit.py", "Setup new repository", "prompt"),
                "14": ("GitHubTimeMachine.py", "GitHub/GitHubTimeMachine.py", "Browse git history", "gui"),
            },
            "📝 Text Processing": {
                "15": ("MarkdownToText.py", "Tools/MarkdownToText.py", "Convert Markdown to text", "params"),
                "16": ("GPUOCRSpeedTest.py", "Tools/GPUOCRSpeedTest.py", "Test OCR performance", "advanced"),
            },
            "🚀 Deployment": {
                "17": ("UpdateFiles.py", "Deployment/UpdateFiles.py", "Deploy files by header paths", "dangerous"),
            },
            "🗄️ Database Tools": {
                "18": ("SQLiteToMySQL_DataDump.py", "DataBase/SQLiteToMySQL_DataDump.py", "Export to MySQL script", "params"),
                "19": ("SQLiteToMySQL_GenericPort.py", "DataBase/SQLiteToMySQL_GenericPort.py", "Direct migration", "params"),
                "20": ("SQLiteToMySQL_GenericPort_Hardened.py", "DataBase/SQLiteToMySQL_GenericPort_Hardened.py", "Production migration", "dangerous"),
            },
            "🧪 Testing": {
                "21": ("WebAppDiagnostic.py", "CurrentApp/WebAppDiagnostic.py", "Anderson's Library diagnostics", "simple"),
            }
        }
    
    def show_menu(self):
        """Display the main menu"""
        print("\n" + "="*60)
        print("🎯 CSM SCRIPT MENU - Choose Your Tool")
        print("="*60)
        
        for category, scripts in self.scripts.items():
            print(f"\n{category}")
            for key, (name, path, desc, type_) in scripts.items():
                status = self._get_status_icon(type_)
                print(f"  {key}. {status} {name} - {desc}")
        
        print(f"\n  0. Exit")
        print("="*60)
    
    def _get_status_icon(self, script_type):
        """Get status icon based on script type"""
        icons = {
            "simple": "✅",
            "prompt": "📝",
            "params": "⚙️",
            "confirm": "⚠️",
            "dangerous": "🔥",
            "gui": "🖥️",
            "advanced": "🔬"
        }
        return icons.get(script_type, "❓")
    
    def run_script(self, choice):
        """Run the selected script with appropriate handling"""
        # Find the script
        script_info = None
        for category, scripts in self.scripts.items():
            if choice in scripts:
                script_info = scripts[choice]
                break
        
        if not script_info:
            print("❌ Invalid choice!")
            return
        
        name, path, desc, script_type = script_info
        script_path = self.script_dir / path
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return
        
        print(f"\n🚀 Running: {name}")
        print(f"📝 Description: {desc}")
        
        # Handle different script types
        if script_type == "simple":
            self._run_simple(script_path)
        elif script_type == "prompt":
            self._run_with_prompt(script_path, name)
        elif script_type == "params":
            self._run_with_params(script_path, name)
        elif script_type == "confirm":
            self._run_with_confirmation(script_path, name)
        elif script_type == "dangerous":
            self._run_dangerous(script_path, name)
        elif script_type == "gui":
            self._run_gui(script_path, name)
        elif script_type == "advanced":
            self._run_advanced(script_path, name)
    
    def _run_simple(self, script_path):
        """Run simple scripts that need no input"""
        try:
            subprocess.run([sys.executable, str(script_path)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Script failed with error: {e}")
    
    def _run_with_prompt(self, script_path, name):
        """Run scripts that need simple user input"""
        if "FindText" in name:
            search_term = input("🔍 Enter search term: ").strip()
            if search_term:
                try:
                    # Most search scripts accept search term as argument
                    subprocess.run([sys.executable, str(script_path), search_term], check=True)
                except subprocess.CalledProcessError:
                    print("❌ Search failed")
        elif "GitHubInitialCommit" in name:
            repo_name = input("📁 Enter repository name: ").strip()
            if repo_name:
                try:
                    subprocess.run([sys.executable, str(script_path), repo_name], check=True)
                except subprocess.CalledProcessError:
                    print("❌ Repository creation failed")
    
    def _run_with_params(self, script_path, name):
        """Run scripts that need multiple parameters"""
        if "MarkdownToText" in name:
            input_dir = input("📂 Input directory (or press Enter for current): ").strip() or "."
            output_dir = input("📂 Output directory (or press Enter for 'output'): ").strip() or "output"
            
            try:
                subprocess.run([sys.executable, str(script_path), input_dir, output_dir], check=True)
            except subprocess.CalledProcessError:
                print("❌ Conversion failed")
        
        elif "SQLite" in name:
            db_path = input("🗄️ SQLite database path: ").strip()
            if db_path:
                try:
                    subprocess.run([sys.executable, str(script_path), db_path], check=True)
                except subprocess.CalledProcessError:
                    print("❌ Database operation failed")
    
    def _run_with_confirmation(self, script_path, name):
        """Run scripts that need confirmation"""
        print(f"⚠️  {name} will make changes to your system/repository")
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            try:
                subprocess.run([sys.executable, str(script_path)], check=True)
            except subprocess.CalledProcessError:
                print("❌ Operation failed")
        else:
            print("❌ Operation cancelled")
    
    def _run_dangerous(self, script_path, name):
        """Run potentially dangerous scripts with extra warnings"""
        print(f"🔥 WARNING: {name} is a powerful tool that can:")
        if "UpdateFiles" in name:
            print("   - Move files around your entire system")
            print("   - Overwrite existing files")
            print("   - Create new directory structures")
        elif "MySQL" in name:
            print("   - Modify production databases")
            print("   - Potentially lose data if misconfigured")
        
        print("\n⚠️  Make sure you have backups!")
        confirm = input("Type 'I UNDERSTAND THE RISKS' to continue: ").strip()
        
        if confirm == "I UNDERSTAND THE RISKS":
            try:
                subprocess.run([sys.executable, str(script_path)], check=True)
            except subprocess.CalledProcessError:
                print("❌ Operation failed")
        else:
            print("❌ Operation cancelled for safety")
    
    def _run_gui(self, script_path, name):
        """Run GUI scripts with dependency check"""
        print(f"🖥️  {name} requires PySide6 for GUI")
        try:
            import PySide6
            subprocess.run([sys.executable, str(script_path)], check=True)
        except ImportError:
            print("❌ PySide6 not installed. Install with: pip install PySide6")
        except subprocess.CalledProcessError:
            print("❌ GUI application failed")
    
    def _run_advanced(self, script_path, name):
        """Run advanced scripts with dependency warnings"""
        print(f"🔬 {name} may require additional dependencies")
        confirm = input("Continue anyway? (yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            try:
                subprocess.run([sys.executable, str(script_path)], check=True)
            except subprocess.CalledProcessError:
                print("❌ Script failed - check dependencies")
        else:
            print("❌ Operation cancelled")
    
    def run(self):
        """Main menu loop"""
        while True:
            self.show_menu()
            choice = input("\n🎯 Enter your choice (0 to exit): ").strip()
            
            if choice == "0":
                print("👋 Happy scripting!")
                break
            
            self.run_script(choice)
            
            input("\n⏸️  Press Enter to continue...")

if __name__ == "__main__":
    menu = ScriptMenu()
    menu.run()