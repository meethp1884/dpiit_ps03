# 🚀 Push to GitHub - Complete Guide

**Team AIGR-S47377 | PS-03 Visual Search**

---

## 📋 Prerequisites

1. **GitHub Account** (create at https://github.com/signup if needed)
2. **Git installed** on your computer
3. **Personal Access Token** (for authentication)

---

## ⚡ QUICK COMMANDS (Copy-Paste)

### Step 1: Create GitHub Repository

**Go to:** https://github.com/new

**Settings:**
- **Repository name**: `ps03-visual-search`
- **Description**: `PS-03 Visual Search & Detection - Team AIGR-S47377`
- **Visibility**: Private (recommended) or Public
- **DO NOT** initialize with README (we have one)

**Click:** "Create repository"

---

### Step 2: Get Personal Access Token (One-Time)

**Go to:** https://github.com/settings/tokens

**Click:** "Generate new token" → "Generate new token (classic)"

**Settings:**
- **Note**: `PS03 Upload Token`
- **Expiration**: 30 days (or longer)
- **Scopes**: Check ✓ `repo` (full control)

**Click:** "Generate token"

**⚠️ COPY THE TOKEN NOW** (you can't see it again!)

---

### Step 3: Initialize and Push

**Open Command Prompt and run:**

```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03

REM Initialize git (if not done)
git init

REM Create .gitignore (important!)
echo # PS-03 Git Ignore > .gitignore
echo. >> .gitignore
echo # Large data files >> .gitignore
echo data/ >> .gitignore
echo chips/ >> .gitignore
echo cache/ >> .gitignore
echo outputs/ >> .gitignore
echo venv/ >> .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo .pytest_cache/ >> .gitignore
echo .ipynb_checkpoints/ >> .gitignore
echo models/checkpoints/*.pth >> .gitignore
echo *.tif >> .gitignore
echo *.tiff >> .gitignore

REM Add all files
git add .

REM Commit
git commit -m "Initial commit - PS03 Visual Search - Team AIGR-S47377"

REM Add remote (REPLACE YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ps03-visual-search.git

REM Push to GitHub
git push -u origin main
```

**When prompted for password:**
- **Username**: Your GitHub username
- **Password**: Paste your Personal Access Token (NOT your GitHub password!)

---

## 📦 Alternative: Using Git Credential Manager

**If you want to avoid entering token each time:**

```cmd
REM Configure Git to use credential manager
git config --global credential.helper manager

REM Then push (will save credentials after first time)
git push -u origin main
```

---

## 🔄 Update Repository Later

**After making changes:**

```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03

REM Check what changed
git status

REM Add changes
git add .

REM Commit with message
git commit -m "Updated configuration for AIGR-S47377"

REM Push
git push
```

---

## 📁 What Gets Pushed

**✅ Included (code & docs):**
- All Python scripts (`scripts/`, `api/`, `ui/`)
- Configuration files (`configs/`)
- Documentation (`.md` files)
- Requirements (`requirements.txt`)
- Docker files
- Kaggle notebook

**❌ Excluded (via .gitignore):**
- Large data files (`data/`, `chips/`, `cache/`)
- Virtual environment (`venv/`)
- Output files (`outputs/`)
- Model checkpoints (`.pth` files)
- Compiled Python (`.pyc`, `__pycache__/`)

**This keeps your repo clean and fast!**

---

## 🌐 Using on Kaggle

**After pushing to GitHub:**

### Method 1: Clone in Kaggle Notebook

```python
# In Kaggle notebook
!git clone https://github.com/YOUR_USERNAME/ps03-visual-search.git
%cd ps03-visual-search
```

### Method 2: Add as Kaggle Dataset

1. Go to https://www.kaggle.com/datasets
2. Click "New Dataset"
3. Select "GitHub" tab
4. Enter: `YOUR_USERNAME/ps03-visual-search`
5. Click "Create"

Then in notebook:
```python
# Add dataset to notebook, then:
!cp -r /kaggle/input/ps03-visual-search/* .
```

---

## 🔐 Security Best Practices

### ❌ NEVER Commit:
- Personal Access Tokens
- API Keys
- Passwords
- Large data files (>100MB)

### ✅ Always Use:
- `.gitignore` for sensitive files
- Environment variables for secrets
- Git LFS for large files (if needed)

---

## 📊 Repository Structure (After Push)

```
ps03-visual-search/
├── .gitignore
├── README.md
├── requirements.txt
├── configs/
│   └── default.yaml
├── scripts/
│   ├── build_index.py
│   ├── run_search.py
│   ├── batch_extract_chips.py
│   └── ...
├── api/
│   └── main.py
├── ui/
│   └── src/
├── docs/
│   ├── FINAL_STEPS_AIGR-S47377.md
│   ├── KAGGLE_NOTEBOOK.ipynb
│   └── ...
└── tests/
    └── ...
```

---

## ⚠️ Troubleshooting

### "remote: Repository not found"
→ Check repository name and your username in the URL

### "Support for password authentication was removed"
→ Use Personal Access Token, NOT password

### "Large files detected"
→ Check `.gitignore` includes data folders

### "Permission denied"
→ Check token has `repo` scope permissions

### "Failed to push"
→ Pull first: `git pull origin main --rebase` then `git push`

---

## 🔄 Complete First-Time Setup

```cmd
REM 1. Navigate to project
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03

REM 2. Configure Git (first time only)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

REM 3. Initialize repository
git init

REM 4. Create .gitignore
copy .gitignore_template .gitignore
REM (or create manually as shown above)

REM 5. Add all files
git add .

REM 6. Initial commit
git commit -m "Initial commit - PS03 Visual Search - Team AIGR-S47377"

REM 7. Add remote (REPLACE YOUR_USERNAME!)
git remote add origin https://github.com/YOUR_USERNAME/ps03-visual-search.git

REM 8. Push to GitHub
git push -u origin main
```

**When prompted:**
- Username: `your_github_username`
- Password: `your_personal_access_token`

---

## 📝 Quick Reference

| Command | Purpose |
|---------|---------|
| `git status` | See what changed |
| `git add .` | Stage all changes |
| `git commit -m "message"` | Save changes |
| `git push` | Upload to GitHub |
| `git pull` | Download from GitHub |
| `git log` | View commit history |

---

## ✅ Verification

**After pushing, check:**

1. **Go to:** https://github.com/YOUR_USERNAME/ps03-visual-search
2. **Verify:** All folders and files visible
3. **Check:** No large data files (should be in .gitignore)
4. **Confirm:** README displays correctly

---

## 🎯 Summary

**To push to GitHub:**

1. ✅ Create repository on GitHub
2. ✅ Get Personal Access Token
3. ✅ Run git commands (see Step 3)
4. ✅ Enter token when prompted
5. ✅ Verify on GitHub website

**Total time: ~10 minutes**

---

## 🚀 Your GitHub URL

**After pushing:**
```
https://github.com/YOUR_USERNAME/ps03-visual-search
```

**Share this URL:**
- In hackathon submission
- With team members
- For collaboration
- For Kaggle notebooks

---

**Team AIGR-S47377 | Ready to push! 🎉**
