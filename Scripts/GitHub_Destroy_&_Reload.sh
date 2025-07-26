#!/bin/bash

# Get current folder name
FOLDER_NAME=$(basename "$PWD")

# GitHub username
GITHUB_USER="CallMeChewy"

# GitHub remote URL
REMOTE_URL="https://github.com/$GITHUB_USER/$FOLDER_NAME.git"

echo "⚙️ Resetting Git repo in: $FOLDER_NAME"
echo "🌐 Remote URL will be: $REMOTE_URL"

# Remove old .git history
rm -rf .git

# Reinitialize Git repo
git init

# Add remote origin
git remote add origin "$REMOTE_URL"

# Stage all files
git add .

# Create new initial commit
git commit -m "Initial commit"

# Push to GitHub (forcefully)
git push -f origin main

echo "✅ Fresh initial commit pushed to $REMOTE_URL"
