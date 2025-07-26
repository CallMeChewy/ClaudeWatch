# Utility Scripts

Collection of utility scripts organized by functionality to support CSM development and operations.

## 📁 Directory Structure

### Core Script Categories

| Directory                    | Purpose                                  | Scripts                                                    |
| ---------------------------- | ---------------------------------------- | ---------------------------------------------------------- |
| [`GitHub/`](GitHub/)         | Git automation and repository management | GitHub API integration, automated commits, repository sync |
| [`DataBase/`](DataBase/)     | Database utilities and migration tools   | SQLite to MySQL conversion, data management                |
| [`System/`](System/)         | Project maintenance and backup utilities | Backup automation, codebase analysis, cleanup              |
| [`Tools/`](Tools/)           | Development and verification utilities   | Browser switching, OCR testing, file verification          |
| [`Deployment/`](Deployment/) | File deployment and update automation    | Automated file updates, deployment pipelines               |

## 🚀 Quick Reference

### Most Used Scripts

```bash
# Project backup and maintenance
python Scripts/System/BackupProject.py
python Scripts/System/CodebaseSum.py

# GitHub operations
python Scripts/GitHub/GitHubAutoUpdate.py
python Scripts/GitHub/GitHubInitialCommit.py

# File operations and deployment
python Scripts/Deployment/UpdateFiles.py
python Scripts/Tools/VerifyIgnore.py
```

### File Organization Tools

```bash
# List files by date
python Scripts/FinderDisplay/ListFilesByDate.py

# Generate project tree
python Scripts/FinderDisplay/SimpleTree.py

# Search for specific content
python Scripts/FinderDisplay/FindText.py
```

## 📋 Script Standards

All scripts in this directory follow **Design Standard v2.1**:

### File Header Requirements

```python
# File: [EXACT FILENAME WITH EXTENSION]
# Path: Scripts/[category]/[filename.py]
# Standard: AIDEV-PascalCase-2.1
# Created: YYYY-MM-DD
# Last Modified: YYYY-MM-DD  HH:MM[AM|PM]
"""
Description: [SPECIFIC PURPOSE - NO GENERIC DESCRIPTIONS]
"""
```

### Coding Standards

- Use actual timestamps (never placeholders like HH:MM)
- Clear, specific descriptions of functionality
- Proper error handling and user feedback
- Consistent naming conventions (PascalCase for files)

## 🔧 Installation and Dependencies

### Common Dependencies

```bash
# Most scripts require these packages
pip install requests pathlib subprocess

# GitHub scripts specifically need
pip install pygithub  # or direct API calls

# Database scripts need
pip install sqlite3 mysql-connector-python
```

### Usage Patterns

```bash
# Run from CSM root directory
python Scripts/[category]/[script_name].py

# Many scripts accept command line arguments
python Scripts/[category]/[script_name].py --help
```

## 📊 Script Categories Detail

### GitHub Scripts ([`GitHub/`](GitHub/))

Automation tools for GitHub repository management:

- **Repository Synchronization**: Keep local and remote repos in sync
- **Automated Commits**: Batch commit operations with proper messaging
- **Issue Management**: Create and update GitHub issues programmatically
- **Release Automation**: Automated release creation and deployment

### Database Scripts ([`DataBase/`](DataBase/))

Database migration and management utilities:

- **SQLite to MySQL**: Complete database migration with data preservation
- **Schema Management**: Database schema updates and modifications
- **Data Validation**: Verify data integrity during migrations
- **Backup and Restore**: Database backup and restoration utilities

### System Scripts ([`System/`](System/))

Project maintenance and system utilities:

- **Project Backup**: Complete project backup with selective exclusions
- **Codebase Analysis**: Generate project summaries and statistics
- **File Management**: Organize and clean up project files
- **Environment Setup**: Project environment configuration and validation

### Tools Scripts ([`Tools/`](Tools/))

Development utilities and verification tools:

- **File Verification**: Validate file integrity and format compliance
- **Performance Testing**: OCR speed tests and benchmarking
- **Browser Management**: Switch default browsers for development
- **Format Conversion**: Convert between different file formats

### Deployment Scripts ([`deployment/`](deployment/))

Automated deployment and file management:

- **File Updates**: Automated file synchronization and updates
- **Deployment Pipelines**: Multi-stage deployment automation
- **Configuration Management**: Deploy configuration files across environments
- **Rollback Utilities**: Safe rollback mechanisms for failed deployments

## 🧪 Testing Scripts

```bash
# Test script functionality
python scripts/[category]/[script_name].py --dry-run

# Validate against standards
python scripts/tools/VerifyIgnore.py
```

## 🛡️ Security Considerations

### Safe Practices

- **No Hardcoded Secrets**: All credentials via environment variables or config files
- **Path Validation**: Prevent directory traversal attacks
- **Input Sanitization**: Validate all user inputs and file paths
- **Permissions**: Run with minimal required permissions

### Configuration Files

```bash
# Example config structure
scripts/config/
├── github_config.example.json
├── database_config.example.json
└── deployment_config.example.json
```

## 🔄 Integration with CSM

### CSM-Aware Scripts

Many scripts are designed to work with CSM monitoring:

- **Backup Scripts**: Exclude CSM archive directories appropriately
- **GitHub Scripts**: Handle CSM session files correctly
- **Deployment Scripts**: Respect CSM project boundaries

### Example Integration

```python
# Script that works with CSM sessions
from enhanced_claude_monitor import MultiSessionClaudeMonitor

def backup_with_csm_awareness():
    monitor = MultiSessionClaudeMonitor()
    active_sessions = monitor.active_sessions

    for session in active_sessions.values():
        # Backup excluding active session archives
        exclude_paths = [session.get_archive_path()]
        create_backup(session.project_path, exclude=exclude_paths)
```

## 📚 Contributing

### Adding New Scripts

1. **Choose Appropriate Category**: Place in correct subdirectory
2. **Follow Standards**: Use Design Standard v2.1 file headers
3. **Document Functionality**: Clear description and usage examples
4. **Test Thoroughly**: Validate with various inputs and edge cases
5. **Update README**: Add to appropriate category documentation

### Script Template

```python
#!/usr/bin/env python3
# File: NewScript.py
# Path: scripts/[category]/NewScript.py
# Standard: AIDEV-PascalCase-2.1
# Created: YYYY-MM-DD
# Last Modified: YYYY-MM-DD  HH:MM[AM|PM]
"""
Description: [Clear description of what this script does]
Usage: python NewScript.py [arguments]
"""

import sys
from pathlib import Path

def main():
    """Main function with clear purpose"""
    pass

if __name__ == "__main__":
    main()
```

## 🚀 Future Enhancements

### Planned Additions

- **CI/CD Integration**: Scripts for automated testing and deployment
- **Monitoring Tools**: System health monitoring and alerting
- **Performance Scripts**: Automated performance testing and optimization
- **Documentation Generation**: Automated documentation updates

### Integration Opportunities

- **VS Code Extension**: Scripts callable from VS Code interface
- **GitHub Actions**: Integration with GitHub Actions workflows
- **Project Himalaya**: Cross-component script sharing and standardization