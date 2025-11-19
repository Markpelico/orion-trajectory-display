# 🚀 GitHub Setup Guide

Your repository is initialized and ready to push to GitHub!

## ✅ What's Already Done

- ✅ Git repository initialized
- ✅ Initial commit created
- ✅ `.gitignore` configured for Python projects
- ✅ All files added and committed
- ✅ Branch set to `main`

## 📋 Next Steps: Push to GitHub

### Option 1: Create New Repository on GitHub (Recommended)

1. **Go to GitHub** and sign in: https://github.com

2. **Create new repository**:
   - Click the ➕ icon (top right) → "New repository"
   - Repository name: `orion-trajectory-display` (or your choice)
   - Description: "Real-time Orion flight trajectory visualization for NASA Trick"
   - Make it **Private** (if for internal NASA use) or **Public**
   - **Do NOT** initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

3. **Connect and push** (GitHub will show you these commands):

```bash
cd "/Users/bigboi2/Desktop/NASA Trick It"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/orion-trajectory-display.git

# Push to GitHub
git push -u origin main
```

**Replace `YOUR_USERNAME`** with your GitHub username!

### Option 2: Use GitHub CLI (if installed)

```bash
cd "/Users/bigboi2/Desktop/NASA Trick It"

# Create repo and push in one command
gh repo create orion-trajectory-display --private --source=. --remote=origin --push
```

## 🔐 Authentication

If prompted for credentials:

### Using Personal Access Token (Recommended)
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full control)
4. Copy the token
5. When git asks for password, paste the token

### Using SSH (Alternative)
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
# Then use SSH URL instead:
git remote add origin git@github.com:YOUR_USERNAME/orion-trajectory-display.git
```

## 📊 Verify Your Repository

After pushing, check on GitHub:
- All files are present
- README.md displays properly
- Commit history shows your initial commit

## 🔄 Future Updates

After making changes:

```bash
cd "/Users/bigboi2/Desktop/NASA Trick It"

# Check what changed
git status

# Add changes
git add .

# Commit with message
git commit -m "Added zoom controls and quit button"

# Push to GitHub
git push
```

## 📝 Git Workflow Quick Reference

### Daily Commands

```bash
# See what changed
git status

# Add specific file
git add flight_trajectory_display.py

# Add all changes
git add .

# Commit changes
git commit -m "Your descriptive message here"

# Push to GitHub
git push

# Pull latest from GitHub
git pull
```

### Viewing History

```bash
# See commit history
git log

# See compact history
git log --oneline

# See what changed in last commit
git show
```

### Branches (for advanced work)

```bash
# Create new branch
git checkout -b feature-name

# Switch branches
git checkout main

# Merge branch
git merge feature-name

# Push branch to GitHub
git push -u origin feature-name
```

## 🏷️ Version Tags (Optional)

To mark releases:

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Initial release with zoom controls"

# Push tags to GitHub
git push --tags

# List tags
git tag -l
```

## 🔍 Current Repository Status

```bash
# Current branch
git branch

# Remote connections
git remote -v

# Last 5 commits
git log --oneline -5
```

## ⚠️ Important Notes

### What's Ignored (.gitignore)
These files/folders won't be tracked:
- `__pycache__/` - Python bytecode
- `*.pyc` - Compiled Python files
- `.DS_Store` - Mac system files
- `*.log` - Log files
- `graphing_data/` - Data output folder

### Sensitive Information
**Never commit:**
- Passwords or API keys
- NASA internal IPs (use placeholders in examples)
- Personal credentials
- Classified information

If you accidentally commit sensitive data, see: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

## 🆘 Troubleshooting

### Problem: "Permission denied (publickey)"
**Solution**: Set up SSH keys (see SSH section above) or use HTTPS with token

### Problem: "Updates were rejected"
**Solution**: Pull first, then push:
```bash
git pull origin main
git push
```

### Problem: "Failed to connect to github.com"
**Solution**: Check internet connection, try HTTPS instead of SSH

### Problem: Changed files but don't want to commit
**Solution**: Discard changes:
```bash
git checkout -- filename.py  # Discard specific file
git reset --hard  # Discard ALL changes (careful!)
```

## 📚 Useful Resources

- **GitHub Docs**: https://docs.github.com
- **Git Cheat Sheet**: https://education.github.com/git-cheat-sheet-education.pdf
- **GitHub Learning Lab**: https://lab.github.com/
- **Oh My Git!** (interactive learning): https://ohmygit.org/

## 👥 Collaboration

If working with teammates:

1. **Give them access**:
   - Go to repo settings → Collaborators
   - Add their GitHub username

2. **They clone**:
```bash
git clone https://github.com/YOUR_USERNAME/orion-trajectory-display.git
cd orion-trajectory-display
```

3. **They make changes and push**:
```bash
git add .
git commit -m "Description of changes"
git push
```

4. **You pull their changes**:
```bash
git pull
```

## 🎯 Quick Setup Summary

**Right now, just run these 3 commands:**

```bash
cd "/Users/bigboi2/Desktop/NASA Trick It"
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git push -u origin main
```

That's it! Your code is now on GitHub! 🎉

---

**Need help?** See the troubleshooting section or ask your team!

