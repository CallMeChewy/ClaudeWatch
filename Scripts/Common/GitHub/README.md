# GitHub Scripts

Automation tools for GitHub repository management and integration.

## 📁 Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `GitHubAutoUpdate.py` | Automated repository synchronization | `python GitHubAutoUpdate.py` |
| `GitHubInitialCommit.py` | Initial repository setup and first commit | `python GitHubInitialCommit.py` |
| `GitHubUpdateSite.py` | Website deployment via GitHub Pages | `python GitHubUpdateSite.py` |
| `GitHubTimeMachine.py` | Repository history navigation and rollback | `python GitHubTimeMachine.py` |
| `TimeTraveiGitHub.py` | Advanced time-based repository operations | `python TimeTraveiGitHub.py` |
| `BackToTheFuture.sh` | Shell script for repository state management | `./BackToTheFuture.sh` |

## 🚀 Core Functionality

### Repository Synchronization
- **Auto-sync**: Keep local and remote repositories synchronized
- **Conflict Resolution**: Handle merge conflicts automatically where possible
- **Branch Management**: Automated branch creation and management
- **Status Monitoring**: Track repository health and sync status

### Automated Workflows
- **Commit Automation**: Batch commits with intelligent messaging
- **Release Management**: Automated release creation and tagging
- **Issue Integration**: Link commits to GitHub issues automatically
- **CI/CD Triggers**: Trigger automated testing and deployment

## 🔧 Configuration

### Setup Requirements
```bash
# Install GitHub CLI (recommended)
gh auth login

# Or set up API token
export GITHUB_TOKEN="your_token_here"

# Python dependencies
pip install pygithub requests
```

### Configuration Files
Create `github_config.json` in the same directory:
```json
{
    "username": "your_github_username",
    "repositories": {
        "CSM": "https://github.com/HerbBowers/CSM.git",
        "GitUp": "https://github.com/HerbBowers/GitUp.git"
    },
    "default_branch": "main",
    "auto_sync_interval": 300
}
```

## 📋 Script Details

### GitHubAutoUpdate.py
Comprehensive repository synchronization tool.

**Features:**
- Automatic pull/push operations
- Conflict detection and resolution
- Multi-repository management
- Scheduled synchronization

**Usage:**
```bash
# Sync all configured repositories
python GitHubAutoUpdate.py --sync-all

# Sync specific repository
python GitHubAutoUpdate.py --repo CSM

# Check status only
python GitHubAutoUpdate.py --status
```

### GitHubInitialCommit.py
Sets up new repositories and creates initial commits.

**Features:**
- Repository initialization
- README and .gitignore creation
- Initial commit with proper structure
- Remote repository creation

**Usage:**
```bash
# Initialize new repository
python GitHubInitialCommit.py --repo-name "NewProject"

# Initialize with custom template
python GitHubInitialCommit.py --repo-name "NewProject" --template python
```

### GitHubUpdateSite.py
Manages GitHub Pages deployment and website updates.

**Features:**
- Automated GitHub Pages deployment
- Static site generation integration
- Content validation before deployment
- Rollback capabilities

**Usage:**
```bash
# Deploy current site content
python GitHubUpdateSite.py --deploy

# Deploy with custom message
python GitHubUpdateSite.py --deploy --message "Updated documentation"
```

### GitHubTimeMachine.py
Advanced repository history navigation and management.

**Features:**
- Time-based repository navigation
- Historical state restoration
- Branch comparison across time periods
- Automated backup before major changes

**Usage:**
```bash
# Go back to state from 1 week ago
python GitHubTimeMachine.py --go-back "1 week"

# Restore specific commit
python GitHubTimeMachine.py --restore-commit abc123def
```

## 🔐 Security Best Practices

### Token Management
- Store tokens in environment variables or secure config files
- Use fine-grained personal access tokens when possible
- Regularly rotate access tokens
- Never commit tokens to repository

### Repository Access
- Use least-privilege access patterns
- Validate repository ownership before operations
- Implement rate limiting to respect GitHub API limits
- Log all operations for audit trail

## 🧪 Testing

### Test GitHub Scripts
```bash
# Test repository access
python GitHubAutoUpdate.py --test-connection

# Dry run operations
python GitHubAutoUpdate.py --dry-run --sync-all

# Validate configuration
python Scripts/Tools/ValidateConfig.py --config github_config.json
```

## 🔄 Integration with CSM

### CSM-Aware Operations
- **Session Archives**: Exclude CSM archive directories from commits
- **Project Detection**: Automatically detect CSM vs GitUp vs other projects
- **Smart Commits**: Generate commit messages based on CSM session activity
- **Restoration Context**: Include session restoration info in commit descriptions

### Example Integration
```python
# Commit with CSM session context
python GitHubAutoUpdate.py --commit-with-session --session-id CSM_20250716_123000
```

## 🚨 Error Handling

### Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| Authentication failed | Invalid token | Check GITHUB_TOKEN environment variable |
| Rate limit exceeded | Too many API calls | Wait or implement backoff strategy |
| Repository not found | Incorrect repo name/URL | Verify repository exists and access permissions |
| Merge conflicts | Conflicting changes | Use conflict resolution scripts or manual merge |

### Debug Mode
```bash
# Enable verbose logging
export GITHUB_DEBUG=1
python GitHubAutoUpdate.py --verbose
```

## 📚 Examples

### Daily Workflow Integration
```bash
# Morning sync routine
python GitHubAutoUpdate.py --sync-all --pull-only

# Evening commit and push
python GitHubAutoUpdate.py --auto-commit --message "Daily development progress"
```

### Automated Release Process
```bash
# Create release from current state
python GitHubAutoUpdate.py --create-release --version "v1.2.0" --notes "Multi-session support added"
```

### Backup and Restore
```bash
# Create backup before major changes
python GitHubTimeMachine.py --create-backup --tag "pre-refactor"

# Restore if needed
python GitHubTimeMachine.py --restore-backup "pre-refactor"
```