# Git Repository Setup Guide

A complete step-by-step guide to initialize a Git repository, create branches, and push to GitHub for team collaboration.

---

## Prerequisites

1. **Git installed** on your system
   - Download from: https://git-scm.com/downloads
   - Verify installation: `git --version`

2. **Git configured** with your credentials:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

3. **GitHub account** (or GitLab/Bitbucket)

---

## Step 1: Create a .gitignore File

Before initializing, create a `.gitignore` file in your project root to exclude unnecessary files.

### For Python/Django Projects:
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtual Environment
.env
.venv/
venv/
ENV/

# Django
*.log
db.sqlite3
media/
staticfiles/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

## Step 2: Create an Empty Repository on GitHub

1. Go to **https://github.com/new**
2. Enter **Repository name** (e.g., `my-project`)
3. Choose **Public** or **Private**
4. ⚠️ **DO NOT** check any initialization options:
   - No README
   - No .gitignore
   - No license
5. Click **Create repository**
6. Copy the repository URL (e.g., `https://github.com/username/my-project.git`)

---

## Step 3: Initialize Git in Your Project

Open terminal/command prompt in your project folder:

```bash
# Navigate to your project directory
cd /path/to/your/project

# Initialize git with 'main' as default branch
git init -b main
```

---

## Step 4: Stage and Commit Files

```bash
# Stage all files
git add .

# Create initial commit
git commit -m "Initial commit: Project setup"
```

---

## Step 5: Create Additional Branches (Optional)

```bash
# Create a feature branch (e.g., for a team member)
git branch feature-branch-name

# Create multiple branches
git branch dev
git branch staging
```

---

## Step 6: Connect to Remote Repository

```bash
# Add GitHub as remote origin
git remote add origin https://github.com/username/repository-name.git

# Verify remote is added
git remote -v
```

---

## Step 7: Push All Branches to GitHub

```bash
# Push main branch and set upstream tracking
git push -u origin main

# Push other branches
git push -u origin feature-branch-name
git push -u origin dev
```

---

## Step 8: Verify Everything

```bash
# Check all branches (local and remote)
git branch -a

# Check repository status
git status
```

---

## For Team Members: Clone the Repository

Once the repository is set up, team members can clone it:

```bash
# Clone the repository
git clone https://github.com/username/repository-name.git

# Navigate into the project
cd repository-name

# List all branches
git branch -a

# Switch to a specific branch
git checkout branch-name
```

---

## Common Git Commands for Collaboration

### Daily Workflow

```bash
# Check current status
git status

# Pull latest changes before starting work
git pull origin main

# Create a new feature branch
git checkout -b feature/new-feature

# Stage changes
git add .
# Or stage specific files
git add filename.py

# Commit changes
git commit -m "Add: description of changes"

# Push changes
git push origin feature/new-feature
```

### Switching Branches

```bash
# Switch to an existing branch
git checkout branch-name

# Create and switch to new branch
git checkout -b new-branch-name
```

### Merging Branches

```bash
# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main

# Merge feature branch into main
git merge feature-branch-name

# Push merged changes
git push origin main
```

### Handling Conflicts

```bash
# If conflicts occur during merge/pull
# 1. Open conflicted files and resolve manually
# 2. Stage resolved files
git add .

# 3. Complete the merge
git commit -m "Resolve merge conflicts"

# 4. Push changes
git push origin branch-name
```

---

## Quick Reference: Complete Setup in One Go

```bash
# 1. Navigate to project
cd /path/to/project

# 2. Initialize with main branch
git init -b main

# 3. Stage all files
git add .

# 4. Initial commit
git commit -m "Initial commit"

# 5. Create feature branches
git branch dev
git branch feature-name

# 6. Add remote
git remote add origin https://github.com/username/repo.git

# 7. Push all branches
git push -u origin main
git push -u origin dev
git push -u origin feature-name
```

---

## Useful Git Aliases (Optional)

Add these to your git config for shortcuts:

```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.cm "commit -m"
git config --global alias.pl "pull origin"
git config --global alias.ps "push origin"
```

Now you can use:
- `git st` instead of `git status`
- `git co main` instead of `git checkout main`
- `git cm "message"` instead of `git commit -m "message"`

---

## Troubleshooting

### "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/username/repo.git
```

### "fatal: not a git repository"
```bash
git init -b main
```

### Authentication Issues
- Use GitHub Personal Access Token instead of password
- Generate at: https://github.com/settings/tokens
- Or set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

---

## Repository Info (This Project)

- **Repository**: https://github.com/atharvsj/nexroar_hrms
- **Default Branch**: main
- **Feature Branch**: atharva
- **Created**: January 31, 2026

---

*Guide created for NEXROAR HRMS Project*
