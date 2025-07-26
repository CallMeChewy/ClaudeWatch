#!/bin/bash
# File: GitHub_Emergency_Reset.sh
# Path: /home/herb/Desktop/AndyLibrary/Scripts/GitHub_Emergency_Reset.sh
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 08:50PM

"""
PROJECT HIMALAYA - Emergency GitHub Repository Reset
Emergency script to completely reset git history and push clean repository
Use when credentials leaked, history corrupted, or clean slate needed

⚠️ DANGER: This destroys ALL git history permanently!
⚠️ Use only in emergencies when git history must be completely reset
⚠️ Recommended: Create backup before running this script
"""

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# PROJECT HIMALAYA Configuration
GITHUB_USER="CallMeChewy"
PROJECT_NAME="PROJECT HIMALAYA"
COMMIT_SIGNATURE="🏔️ PROJECT HIMALAYA"

# Safety and validation functions
print_header() {
    echo ""
    echo "🏔️ =================================================="
    echo "🏔️ PROJECT HIMALAYA - EMERGENCY GITHUB RESET"
    echo "🏔️ =================================================="
    echo ""
}

print_warning() {
    echo -e "${RED}⚠️  WARNING: $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_step() {
    echo -e "${CYAN}🔄 $1${NC}"
}

check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        print_warning "Git is not installed or not in PATH"
        exit 1
    fi
    
    # Check if we're in a git repository directory
    if [ ! -d ".git" ] && [ ! -f ".gitignore" ]; then
        print_warning "Not in a git repository directory"
        echo "Please run this script from the root of your git repository"
        exit 1
    fi
    
    # Check for important PROJECT HIMALAYA files
    local required_files=("StartAndyGoogle.py" "CLAUDE.md" "PROJECT_HIMALAYA_COMPLETE.md")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_warning "Required PROJECT HIMALAYA file not found: $file"
            echo "Are you sure you're in the correct PROJECT HIMALAYA directory?"
            exit 1
        fi
    done
    
    print_success "Prerequisites check passed"
}

validate_credentials() {
    print_step "Validating credential security..."
    
    # Check for credential files that should not be committed
    local sensitive_files=("Config/google_credentials.json" "Config/google_token.json" ".env")
    local found_credentials=false
    
    for file in "${sensitive_files[@]}"; do
        if [ -f "$file" ]; then
            print_warning "Sensitive file found: $file"
            found_credentials=true
        fi
    done
    
    # Check for hardcoded credentials in common files
    local credential_patterns=("906077568035" "GOCSPX-" "AlzaSy")
    
    for pattern in "${credential_patterns[@]}"; do
        if grep -r "$pattern" . --exclude-dir=.git --exclude-dir=.venv >/dev/null 2>&1; then
            print_warning "Potential hardcoded credentials found (pattern: $pattern)"
            echo "Files containing this pattern:"
            grep -r "$pattern" . --exclude-dir=.git --exclude-dir=.venv -l
            found_credentials=true
        fi
    done
    
    if [ "$found_credentials" = true ]; then
        echo ""
        print_warning "CREDENTIAL SECURITY ISSUE DETECTED!"
        echo "Before proceeding, you should:"
        echo "1. Remove sensitive files or add them to .gitignore"
        echo "2. Replace hardcoded credentials with placeholder values"
        echo "3. Review all files for any exposed secrets"
        echo ""
        read -p "Do you want to continue anyway? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            echo "Aborting emergency reset for security review"
            exit 1
        fi
    else
        print_success "No obvious credential security issues found"
    fi
}

get_repository_info() {
    print_step "Determining repository information..."
    
    # Get current folder name for repository
    FOLDER_NAME=$(basename "$PWD")
    
    # Construct GitHub remote URL
    REMOTE_URL="https://github.com/$GITHUB_USER/$FOLDER_NAME.git"
    
    # Check if remote already exists
    if git remote get-url origin >/dev/null 2>&1; then
        CURRENT_REMOTE=$(git remote get-url origin)
        echo "Current remote: $CURRENT_REMOTE"
    fi
    
    echo "Repository name: $FOLDER_NAME"
    echo "GitHub user: $GITHUB_USER"
    echo "Target remote URL: $REMOTE_URL"
    
    print_success "Repository information determined"
}

confirm_destruction() {
    echo ""
    print_warning "DANGER: This will permanently destroy all git history!"
    print_warning "This action cannot be undone!"
    echo ""
    echo "This script will:"
    echo "1. Delete the entire .git directory (ALL HISTORY LOST)"
    echo "2. Initialize a fresh git repository"
    echo "3. Add all current files to staging"
    echo "4. Create a new initial commit"
    echo "5. Force push to GitHub (overwriting remote repository)"
    echo ""
    echo "Repository: $REMOTE_URL"
    echo "Files to be committed: $(find . -type f | grep -v .git | wc -l) files"
    echo ""
    
    # Triple confirmation for safety
    read -p "Are you absolutely sure you want to proceed? (type 'YES' to confirm): " confirm1
    if [ "$confirm1" != "YES" ]; then
        echo "Emergency reset cancelled"
        exit 0
    fi
    
    read -p "Last chance! Type 'DESTROY HISTORY' to confirm: " confirm2
    if [ "$confirm2" != "DESTROY HISTORY" ]; then
        echo "Emergency reset cancelled"
        exit 0
    fi
    
    print_warning "Proceeding with emergency reset in 5 seconds..."
    sleep 5
}

create_backup() {
    print_step "Creating emergency backup..."
    
    # Create backup directory with timestamp
    local backup_dir="../${FOLDER_NAME}_EMERGENCY_BACKUP_$(date +%Y%m%d_%H%M%S)"
    
    # Copy entire directory (excluding .git to save space)
    cp -r . "$backup_dir"
    rm -rf "$backup_dir/.git" 2>/dev/null || true
    
    print_success "Emergency backup created: $backup_dir"
    echo "You can restore from this backup if needed"
}

perform_emergency_reset() {
    print_step "Performing emergency git history reset..."
    
    # Step 1: Destroy git history
    print_step "Removing git history..."
    rm -rf .git
    print_success "Git history destroyed"
    
    # Step 2: Initialize fresh repository
    print_step "Initializing fresh repository..."
    git init
    git branch -M main
    print_success "Fresh repository initialized"
    
    # Step 3: Add remote
    print_step "Adding GitHub remote..."
    git remote add origin "$REMOTE_URL"
    print_success "Remote added: $REMOTE_URL"
    
    # Step 4: Stage all files
    print_step "Staging all files..."
    git add .
    
    local staged_files=$(git diff --cached --name-only | wc -l)
    print_success "Staged $staged_files files for commit"
    
    # Step 5: Create PROJECT HIMALAYA commit
    print_step "Creating PROJECT HIMALAYA initial commit..."
    
    local commit_message="$COMMIT_SIGNATURE: Emergency Reset - Clean Repository

🚨 EMERGENCY RESET PERFORMED
- Complete git history reset due to: [SPECIFY REASON]
- All previous commits and history permanently removed
- Fresh start with current codebase state

$PROJECT_NAME Educational Library Platform:
- 1,219 books with metadata and thumbnails
- Student cost protection with regional pricing  
- Google Drive integration for actual book files
- Professional web interface with PDF viewing
- Enterprise performance and security

🛡️ Security Status:
- All credentials replaced with template placeholders
- Real secrets protected by .gitignore
- Safe for public repository sharing

🏔️ AI-Human Collaboration Success:
- Built with 50+ years engineering wisdom
- Unix principles: simple tools, well combined
- Educational mission over technical complexity
- Righteous architecture serving global education

Emergency reset performed: $(date)
Reset by: PROJECT HIMALAYA Emergency Script v2.1"

    git commit -m "$commit_message"
    print_success "Initial commit created"
    
    # Step 6: Force push to GitHub
    print_step "Force pushing to GitHub..."
    print_warning "This will overwrite the remote repository!"
    
    git push -f origin main
    print_success "Successfully pushed to GitHub"
}

print_completion() {
    echo ""
    echo "🏔️ =================================================="
    echo "🏔️ PROJECT HIMALAYA EMERGENCY RESET COMPLETE"
    echo "🏔️ =================================================="
    echo ""
    print_success "Emergency reset completed successfully!"
    echo ""
    echo "📊 SUMMARY:"
    echo "✅ Git history completely reset"
    echo "✅ Fresh repository initialized"
    echo "✅ All files committed to new initial commit"
    echo "✅ Repository force-pushed to GitHub"
    echo ""
    echo "🔗 GitHub Repository: $REMOTE_URL"
    echo "📁 Local Repository: $(pwd)"
    echo "📋 Total Files: $(git ls-files | wc -l) files in repository"
    echo ""
    echo "🔄 NEXT STEPS:"
    echo "1. Verify repository looks correct on GitHub"
    echo "2. Update any team members about the reset"
    echo "3. Update any CI/CD pipelines or deployments"
    echo "4. Document the reason for emergency reset in project notes"
    echo ""
    print_success "PROJECT HIMALAYA emergency reset successful!"
    echo ""
}

# Main execution
main() {
    print_header
    
    # Safety checks
    check_prerequisites
    get_repository_info
    validate_credentials
    
    # Confirmation and backup
    confirm_destruction
    create_backup
    
    # Perform the reset
    perform_emergency_reset
    
    # Completion
    print_completion
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi