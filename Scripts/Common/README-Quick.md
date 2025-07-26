# Quick Script Reference - The "What Does This Do?" Guide

**File:** README-Quick.md  
**Path:** Scripts/README-Quick.md  
**Standard:** AIDEV-PascalCase-2.1  
**Created:** 2025-07-17  
**Last Modified:** 2025-07-17  10:15AM

---

## 🚀 **One-Line Script Summaries**

### **🔧 System Maintenance**

- **BackupProject.py** - Full project backup to Desktop (respects .gitignore)
- **BackupTemp.py** - Quick backup of specific directories
- **CodebaseSum.py** - Generate complete project documentation snapshot

### **📊 File Analysis**

- **ListFilesByDate.py** - Show files sorted by modification date
- **ListNewPy.py** - List Python files with sizes and dates
- **NewPyDump.py** - Export Python file inventory to CSV
- **SimpleTree.py** - Show directory structure (respects .gitignore)
- **VerifyIgnore.py** - Debug .gitignore patterns

### **🔍 Search Tools**

- **FindText.py** - Simple text search in files
- **FindTextTwo.py** - Search for two phrases on same line
- **AdvancedFileSearcher.py** - GUI search tool (requires PySide6)

### **🌐 GitHub Operations**

- **GitHubAutoUpdate.py** - Auto add/commit/push to GitHub
- **GitHubUpdateSite.py** - Simple GitHub Pages updates
- **GitHubInitialCommit.py** - Set up new GitHub repository
- **GitHubTimeMachine.py** - Browse git history with GUI
- **TimeTraveiGitHub.py** - Advanced git file comparison

### **🗄️ Database Tools**

- **SQLiteToMySQL_DataDump.py** - Export SQLite to MySQL script
- **SQLiteToMySQL_GenericPort.py** - Direct SQLite→MySQL migration
- **SQLiteToMySQL_GenericPort_Hardened.py** - Production migration tool

### **📝 Text Processing**

- **MarkdownToText.py** - Convert Markdown files to plain text ⚠️ NEEDS PARAMS
- **GPUOCRSpeedTest.py** - Test OCR performance (GPU vs CPU)

### **🚀 Deployment**

- **UpdateFiles.py** - Deploy files based on header paths ⚠️ POWERFUL/DANGEROUS

### **🧪 Testing**

- **WebAppDiagnostic.py** - Check Anderson's Library web app health

---

## ⚠️ **Safety Warnings**

### **🔥 DANGEROUS - USE WITH CAUTION**

- **UpdateFiles.py** - Moves files around entire system based on headers
- **GitHubAutoUpdate.py** - Automatically commits and pushes to GitHub
- **SQLiteToMySQL_GenericPort_Hardened.py** - Production database operations

### **⚠️ REQUIRES PARAMETERS**

- **MarkdownToText.py** - Needs input/output directories
- **SQLiteToMySQL_*.py** - Need database paths/credentials
- **GPUOCRSpeedTest.py** - Needs test image files

### **📋 REQUIRES DEPENDENCIES**

- **AdvancedFileSearcher.py** - Needs PySide6
- **GitHubTimeMachine.py** - Needs PySide6
- **TimeTraveiGitHub.py** - Needs PySide6
- **GPUOCRSpeedTest.py** - Needs torch, easyocr, paddleocr

---

## 🎯 **Common Use Cases**

### **"I need to..."**

- **Backup my project** → `BackupProject.py`
- **See what files changed recently** → `ListFilesByDate.py`
- **Find text in my files** → `FindText.py`
- **Check my directory structure** → `SimpleTree.py`
- **Push to GitHub** → `GitHubAutoUpdate.py`
- **See git history** → `GitHubTimeMachine.py`
- **Convert markdown to text** → `MarkdownToText.py` (needs params)
- **Get project overview** → `CodebaseSum.py`

### **"I'm debugging..."**

- **Why is my file ignored?** → `VerifyIgnore.py`
- **What Python files do I have?** → `ListNewPy.py`
- **Is my web app working?** → `WebAppDiagnostic.py`

### **"I'm setting up..."**

- **New GitHub repo** → `GitHubInitialCommit.py`
- **Database migration** → `SQLiteToMySQL_GenericPort.py`
- **File deployment** → `UpdateFiles.py` (CAREFUL!)

---

## 🤔 **Potentially Deprecated/Questionable**

### **May Need Review:**

- **FindTextTwo.py** - Seems very specific, might be outdated
- **NewPyDump.py** - CSV export might be redundant with other tools
- **TimeTraveiGitHub.py** - Similar to GitHubTimeMachine.py, might be duplicate
- **BackupTemp.py** - Very simple, might be superseded by BackupProject.py

### **Project-Specific:**

- **WebAppDiagnostic.py** - Anderson's Library specific
- **GPUOCRSpeedTest.py** - Very specific use case

---

## 📱 **Perfect for Menu System**

### **No-Brainer Scripts** (Just run them):

```
✅ BackupProject.py
✅ ListFilesByDate.py  
✅ ListNewPy.py
✅ SimpleTree.py
✅ VerifyIgnore.py
✅ CodebaseSum.py
✅ GitHubAutoUpdate.py
✅ GitHubUpdateSite.py
```

### **Need Simple Prompts:**

```
📝 FindText.py → "Search for what?"
📝 MarkdownToText.py → "Input dir?" "Output dir?"
📝 GitHubInitialCommit.py → "Repo name?"
```

### **Need Careful Confirmation:**

```
⚠️ UpdateFiles.py → "Are you sure? This moves files!"
⚠️ SQLiteToMySQL_*.py → "Database path?"
```

---

**Next Step:** Create a simple menu system that groups these logically and handles the parameter collection for you!