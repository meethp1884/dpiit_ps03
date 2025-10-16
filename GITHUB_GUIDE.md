# GitHub Guide - PS-03

## 📤 Pushing Your Project to GitHub

Complete step-by-step guide to upload your PS-03 project to GitHub.

---

## 🎯 Prerequisites

1. **GitHub Account**: Create at https://github.com/signup (free)
2. **Git Installed**: Download from https://git-scm.com/downloads

**Verify Git installation:**
```cmd
git --version
```

---

## 📋 Step-by-Step GitHub Upload

### Step 1: Create GitHub Repository

1. Go to https://github.com
2. Click the **"+"** button (top right) → **"New repository"**
3. Fill in:
   - **Repository name:** `ps03-visual-search`
   - **Description:** `Visual search system for satellite imagery (PS-03 challenge)`
   - **Visibility:** Choose Public or Private
   - **DO NOT** check "Initialize with README" (we have one)
4. Click **"Create repository"**

GitHub will show you commands - **keep this page open!**

---

### Step 2: Prepare Your Project

**Windows Command Prompt:**

```cmd
REM Navigate to project
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03

REM Initialize Git (if not already done)
git init

REM Configure Git (first time only)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

### Step 3: Create .gitignore (Already Done!)

Your `.gitignore` file already excludes large files. Verify it:

```cmd
type .gitignore
```

**Important:** This prevents uploading:
- Large datasets (`.tif` files)
- Virtual environment (`venv/`)
- Cache files (`*.npy`, `*.index`)
- Model checkpoints (large `.pth` files)

---

### Step 4: Stage Files

```cmd
REM Add all files (respects .gitignore)
git add .

REM Check what will be committed
git status
```

You should see:
- ✅ Python files (.py)
- ✅ Config files (.yaml)
- ✅ Documentation (.md)
- ✅ UI files (.js, .jsx, .css)
- ❌ Data files (.tif) - EXCLUDED
- ❌ Cache files - EXCLUDED
- ❌ Virtual env - EXCLUDED

---

### Step 5: Commit Changes

```cmd
git commit -m "Initial commit: PS-03 visual search system"
```

---

### Step 6: Add Remote and Push

**Replace `yourusername` with your actual GitHub username:**

```cmd
REM Add GitHub remote
git remote add origin https://github.com/yourusername/ps03-visual-search.git

REM Push to GitHub
git branch -M main
git push -u origin main
```

**If prompted for credentials:**
- **Username:** Your GitHub username
- **Password:** Use a **Personal Access Token** (not your GitHub password)

#### How to Get Personal Access Token:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "PS03 Upload"
4. Expiration: 90 days
5. Check: `repo` (full control)
6. Click "Generate token"
7. **COPY THE TOKEN** (you won't see it again!)
8. Use this token as password when pushing

---

### Step 7: Verify Upload

1. Go to https://github.com/yourusername/ps03-visual-search
2. You should see all your files!

---

## 📂 What Gets Uploaded to GitHub

### ✅ Uploaded (Code & Docs):
```
✓ engine/          (all .py files)
✓ api/             (all .py files)
✓ ui/              (all React files)
✓ scripts/         (all .py files)
✓ configs/         (YAML files)
✓ tests/           (test files)
✓ notebooks/       (Jupyter notebooks)
✓ requirements.txt
✓ README.md
✓ All documentation
✓ .gitignore
✓ Dockerfile
```

### ❌ NOT Uploaded (Large Files):
```
✗ data/*.tif       (datasets - too large)
✗ venv/            (virtual environment)
✗ cache/*.npy      (embeddings cache)
✗ cache/*.index    (FAISS indexes)
✗ outputs/         (result files)
✗ models/*.pth     (large checkpoints)
✗ node_modules/    (npm packages)
```

**This is correct!** You don't want to upload large data files to GitHub.

---

## 🔄 Making Updates Later

After making changes to your code:

```cmd
REM Check what changed
git status

REM Add changes
git add .

REM Commit with descriptive message
git commit -m "Fixed ZNCC scorer bug"

REM Push to GitHub
git push
```

---

## 📥 Cloning on Another Machine (or Kaggle)

To download your project on another computer:

```bash
# Clone repository
git clone https://github.com/yourusername/ps03-visual-search.git

# Navigate to project
cd ps03-visual-search

# Install dependencies
pip install -r requirements.txt

# Add your datasets manually
# (Copy to data/ folder as per DATASET_SETUP.md)
```

---

## 🎯 GitHub + Kaggle Workflow

### Upload Code to GitHub (done above)

### Use in Kaggle:

**Kaggle Notebook - Cell 1:**
```python
# Clone from GitHub
!git clone https://github.com/yourusername/ps03-visual-search.git

# Navigate
%cd ps03-visual-search

# Install
!pip install -q rasterio faiss-cpu pyyaml tqdm
```

**Kaggle Notebook - Cell 2:**
```python
import sys
sys.path.insert(0, '/kaggle/working/ps03-visual-search')

# Add datasets as Kaggle datasets, then link
!ln -s /kaggle/input/your-dataset/*.tif /kaggle/working/ps03-visual-search/data/testing_set/
```

Much easier than uploading code as dataset!

---

## 🔐 GitHub Authentication Options

### Option 1: Personal Access Token (Recommended)

Already covered above. Use this for HTTPS.

### Option 2: SSH Keys (Advanced)

```cmd
REM Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

REM Add to GitHub: Settings → SSH Keys → New SSH Key
REM Paste contents of: C:\Users\meeth\.ssh\id_ed25519.pub

REM Change remote to SSH
git remote set-url origin git@github.com:yourusername/ps03-visual-search.git
```

---

## 📝 Useful Git Commands

### View Status
```cmd
git status
```

### View Commit History
```cmd
git log --oneline
```

### Undo Last Commit (keep changes)
```cmd
git reset --soft HEAD~1
```

### Discard Local Changes
```cmd
git checkout -- filename.py
```

### Pull Latest Changes
```cmd
git pull origin main
```

### Create Branch
```cmd
git checkout -b feature-new-embedder
```

### Merge Branch
```cmd
git checkout main
git merge feature-new-embedder
```

---

## 📚 Example Commit Messages

Good commit messages:
- `"Initial commit: PS-03 visual search system"`
- `"Added support for class names with spaces"`
- `"Fixed FAISS index save/load bug"`
- `"Improved NMS performance"`
- `"Updated README with Kaggle instructions"`

Bad commit messages:
- `"update"`
- `"fix"`
- `"changes"`

---

## 🚨 Important Notes

### DO NOT Commit:
- **Datasets** - Use `.gitignore` (already set up)
- **API Keys** - Never commit secrets
- **Large Models** - Use Git LFS or external storage
- **Personal Data** - Keep private info out

### DO Commit:
- **Code** - All Python, JavaScript files
- **Configs** - YAML, JSON files
- **Documentation** - README, guides
- **Tests** - Test files

---

## 🔍 Verify What Will Be Pushed

Before pushing, check:

```cmd
REM See what's staged
git status

REM See what's ignored
git status --ignored

REM Check file sizes
git ls-files | xargs -I{} ls -lh {}
```

If you see large `.tif` files listed, they're about to be uploaded - **DON'T PUSH!** Fix `.gitignore` first.

---

## 📦 Adding Large Files (Optional - Advanced)

If you need to track large model checkpoints:

### Option 1: Git LFS (Large File Storage)
```cmd
REM Install Git LFS
git lfs install

REM Track large files
git lfs track "*.pth"
git lfs track "models/checkpoints/*.pth"

REM Commit .gitattributes
git add .gitattributes
git commit -m "Added Git LFS tracking"

REM Now large files can be committed
git add models/checkpoints/best.pth
git commit -m "Added pretrained model"
git push
```

### Option 2: External Storage
- Upload to Google Drive / Dropbox
- Add download link in README
- Use `wget` in setup script

**Recommended:** Keep models separate, download as needed.

---

## ✅ Final GitHub Checklist

- [ ] Repository created on GitHub
- [ ] Git installed and configured locally
- [ ] `.gitignore` properly excludes large files
- [ ] All code files committed
- [ ] Pushed to GitHub successfully
- [ ] README.md displays correctly on GitHub
- [ ] Repository set to Public (if you want others to see)
- [ ] Added description and topics (optional but nice)

---

## 🎓 GitHub Repository Topics

Add these topics to your repo for discoverability:
- `satellite-imagery`
- `computer-vision`
- `visual-search`
- `faiss`
- `pytorch`
- `image-retrieval`
- `remote-sensing`

**To add:** Repository page → "⚙️ Settings" → "Topics"

---

## 🌟 Making Your Repo Stand Out

Add these files (optional):

**LICENSE (MIT License is common):**
```cmd
REM Create LICENSE file
notepad LICENSE
```

**CONTRIBUTING.md:**
Guidelines for contributors

**CHANGELOG.md:**
Document version changes

---

## 📞 Troubleshooting GitHub

### Error: "remote origin already exists"
```cmd
git remote remove origin
git remote add origin https://github.com/yourusername/ps03-visual-search.git
```

### Error: "failed to push some refs"
```cmd
REM Pull first, then push
git pull origin main --rebase
git push origin main
```

### Error: "Permission denied"
- Check your Personal Access Token
- Ensure token has `repo` scope
- Token might be expired

### Error: "Large files detected"
```cmd
REM Remove from staging
git rm --cached path/to/large/file

REM Add to .gitignore
echo "path/to/large/file" >> .gitignore

REM Commit
git add .gitignore
git commit -m "Updated .gitignore"
```

---

## 🎯 Complete Example Session

```cmd
REM Start from project directory
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03

REM Initialize (first time only)
git init
git config user.name "Meeth Patel"
git config user.email "meeth@example.com"

REM Stage all files
git add .

REM Check what will be committed
git status

REM Commit
git commit -m "Initial commit: PS-03 visual search system"

REM Add GitHub remote
git remote add origin https://github.com/meethpatel/ps03-visual-search.git

REM Push
git branch -M main
git push -u origin main
```

Done! Your code is now on GitHub! 🎉

---

## 📖 Further Learning

- **Git Tutorial:** https://git-scm.com/docs/gittutorial
- **GitHub Guides:** https://guides.github.com/
- **Git Cheat Sheet:** https://education.github.com/git-cheat-sheet-education.pdf
