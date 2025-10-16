# 📘 PS-03 Complete Guide - Everything You Need

**Your one-stop guide for PS-03 Visual Search System**

---

## 🗂️ Documentation Index

Your project has these guides:

1. **DATASET_SETUP.md** - Where to put your 3 datasets
2. **LOCAL_SETUP.md** - Running on your Windows machine
3. **KAGGLE_SETUP.md** - Running on Kaggle with free GPU
4. **GITHUB_GUIDE.md** - Uploading to GitHub
5. **README.md** - Full technical documentation
6. **QUICKSTART.md** - 5-minute quick start
7. **THIS FILE** - Overview and workflow

---

## 🎯 Your Workflow (Start Here!)

### Phase 1: Setup (30 minutes)

1. ✅ **Place Datasets** → Read `DATASET_SETUP.md`
   - Training set (150 TIFFs) → `data/training_set/`
   - Testing set (40 TIFFs) → `data/testing_set/`
   - Sample set (9 TIFFs + JSONs) → `data/sample_set/`

2. ✅ **Install Dependencies** → Read `LOCAL_SETUP.md`
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. ✅ **Create Query Chips** → Read `DATASET_SETUP.md`
   ```cmd
   mkdir "chips\Solar Panel"
   REM Then copy or extract chips
   ```

### Phase 2: Local Testing (15 minutes)

4. ✅ **Build Index** → Read `LOCAL_SETUP.md`
   ```cmd
   python scripts\build_index.py --targets data\testing_set --out cache\indexes
   ```

5. ✅ **Run Search** → Read `LOCAL_SETUP.md`
   ```cmd
   python scripts\run_search.py ^
     --chips "chips\Solar Panel\chip_01.tif" ^
     --index cache\indexes ^
     --name "Solar Panel" ^
     --out outputs\results.txt
   ```

6. ✅ **Verify Results**
   ```cmd
   notepad outputs\results.txt
   ```

### Phase 3: Kaggle Deployment (Optional, 1 hour)

7. ✅ **Upload to GitHub** → Read `GITHUB_GUIDE.md`
   ```cmd
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

8. ✅ **Run on Kaggle** → Read `KAGGLE_SETUP.md`
   - Create Kaggle notebook
   - Clone from GitHub
   - Add datasets
   - Run with free GPU

### Phase 4: Training (Optional, 2-4 hours)

9. ✅ **Train Embedder** → Read `LOCAL_SETUP.md` or `KAGGLE_SETUP.md`
   ```cmd
   python scripts\train_embedder.py --data data\training_set --epochs 50 --device cuda
   ```

---

## ❓ Quick Answers to Your Questions

### Q1: Where do I put my datasets?

**Answer:** See `DATASET_SETUP.md` - Summary:

```
new_ps03/
├── data/
│   ├── training_set/      ← Your train dataset (150 TIFFs)
│   ├── testing_set/       ← Your mock/test dataset (40 TIFFs)
│   └── sample_set/        ← Your sample dataset (9 TIFFs + JSONs)
└── chips/
    └── Solar Panel/       ← Your query chips (use spaces!)
```

### Q2: How do I handle class names with spaces (e.g., "Solar Panel")?

**Answer:** Always use quotes!

```cmd
REM Create folder with spaces
mkdir "chips\Solar Panel"

REM Use in commands with quotes
python scripts\run_search.py ^
  --chips "chips\Solar Panel\chip_01.tif" ^
  --name "Solar Panel" ^
  --out outputs\results.txt
```

**Output will have "Solar Panel" (with space) in the class name column!**

### Q3: How do I run on my Windows machine?

**Answer:** See `LOCAL_SETUP.md` - Quick version:

```cmd
REM 1. Setup
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

REM 2. Build index
python scripts\build_index.py --targets data\testing_set --out cache\indexes

REM 3. Search
python scripts\run_search.py ^
  --chips "chips\Solar Panel\chip_01.tif" ^
  --index cache\indexes ^
  --name "Solar Panel" ^
  --out outputs\results.txt
```

### Q4: How do I run on Kaggle?

**Answer:** See `KAGGLE_SETUP.md` - Quick version:

1. Upload code + datasets to Kaggle
2. Create notebook
3. Clone/extract code
4. Link datasets
5. Run with GPU (free!)

Or clone from GitHub (easier).

### Q5: How do I push to GitHub?

**Answer:** See `GITHUB_GUIDE.md` - Quick version:

```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03

REM First time setup
git init
git config user.name "Your Name"
git config user.email "your@email.com"

REM Stage and commit
git add .
git commit -m "Initial commit: PS-03 visual search"

REM Push to GitHub
git remote add origin https://github.com/yourusername/ps03-visual-search.git
git branch -M main
git push -u origin main
```

**Note:** Use Personal Access Token as password (not your GitHub password).

### Q6: Do I need to rename "Solar Panel" to "Solar_Panel"?

**Answer:** NO! Keep your class name as "Solar Panel" (with space).

- Folder: `chips\Solar Panel\`
- Command: `--name "Solar Panel"` (with quotes)
- Output: Will show `Solar Panel` (with space)

Everything works with spaces - just use quotes in commands!

---

## 🚀 Complete Example (Your Exact Case)

### Your Setup:
- Class name: **"Solar Panel"** (with space)
- 3 datasets: training, testing, sample

### Step-by-Step:

**1. Place Datasets (5 min):**
```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03

REM Create folders
mkdir data\training_set
mkdir data\testing_set
mkdir data\sample_set
mkdir "chips\Solar Panel"

REM Copy your datasets (adjust paths)
xcopy "C:\path\to\your\training\*.tif" "data\training_set\" /Y
xcopy "C:\path\to\your\testing\*.tif" "data\testing_set\" /Y
xcopy "C:\path\to\your\sample\*.*" "data\sample_set\" /Y
```

**2. Install (10 min):**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**3. Create Query Chips (5 min):**

Option A - From JSON:
```cmd
python scripts\make_chip_from_json.py ^
  --json data\sample_set\GC01PS03S0001.json ^
  --out "chips\Solar Panel\chip_01.tif"
```

Option B - Copy existing:
```cmd
copy "C:\path\to\your\chip.tif" "chips\Solar Panel\chip_01.tif"
```

**4. Build Index (5-10 min):**
```cmd
python scripts\build_index.py ^
  --targets data\testing_set ^
  --out cache\indexes ^
  --device cpu
```

**5. Run Search (2 min):**
```cmd
python scripts\run_search.py ^
  --chips "chips\Solar Panel\chip_01.tif" "chips\Solar Panel\chip_02.tif" ^
  --index cache\indexes ^
  --name "Solar Panel" ^
  --out outputs\GC_PS03_16-Oct-2025_TeamName\results.txt ^
  --team TeamName
```

**6. View Results:**
```cmd
notepad outputs\GC_PS03_16-Oct-2025_TeamName\results.txt
```

**Output format:**
```
x_min y_min x_max y_max Solar Panel GC01PS03T0001 0.923456
x_min y_min x_max y_max Solar Panel GC01PS03T0002 0.887234
...
```

Notice: **"Solar Panel"** (with space) appears in output!

---

## 📁 Final Folder Structure

After setup, you should have:

```
new_ps03/
├── data/
│   ├── training_set/
│   │   ├── GC01PS03D0001.tif
│   │   └── ... (150 files)
│   ├── testing_set/
│   │   ├── GC01PS03T0001.tif
│   │   └── ... (40 files)
│   └── sample_set/
│       ├── GC01PS03S0001.tif
│       ├── GC01PS03S0001.json
│       └── ... (9 TIFFs + 9 JSONs)
│
├── chips/
│   └── Solar Panel/           ← With space!
│       ├── chip_01.tif
│       └── chip_02.tif
│
├── cache/
│   └── indexes/
│       ├── faiss_index.index
│       └── faiss_index_metadata.pkl
│
├── outputs/
│   └── GC_PS03_16-Oct-2025_TeamName/
│       ├── results.txt        ← Submission file
│       └── results_summary.txt
│
├── venv/                      ← Virtual environment
│
├── engine/                    ← Code (do not modify)
├── api/
├── ui/
├── scripts/
├── configs/
└── [all other files]
```

---

## 🎯 Common Workflows

### Workflow 1: Basic Search
```cmd
venv\Scripts\activate
python scripts\build_index.py --targets data\testing_set --out cache\indexes
python scripts\run_search.py --chips "chips\Solar Panel\chip_01.tif" --index cache\indexes --name "Solar Panel" --out outputs\results.txt
```

### Workflow 2: Multiple Classes
```cmd
REM Search Solar Panel
python scripts\run_search.py --chips "chips\Solar Panel\chip_01.tif" --name "Solar Panel" --index cache\indexes --out outputs\solar_panel.txt

REM Search Pond-1
python scripts\run_search.py --chips "chips\Pond-1\chip_01.tif" --name "Pond-1" --index cache\indexes --out outputs\pond.txt

REM Combine results
copy outputs\solar_panel.txt + outputs\pond.txt outputs\combined.txt
```

### Workflow 3: With Training
```cmd
REM Train embedder
python scripts\train_embedder.py --data data\training_set --epochs 50 --device cuda

REM Rebuild index with trained model
python scripts\build_index.py --targets data\testing_set --out cache\indexes_trained --checkpoint models\checkpoints\best.pth

REM Search with trained model
python scripts\run_search.py --chips "chips\Solar Panel\chip_01.tif" --index cache\indexes_trained --checkpoint models\checkpoints\best.pth --name "Solar Panel" --out outputs\results_trained.txt
```

### Workflow 4: Kaggle
```bash
# In Kaggle notebook
!git clone https://github.com/yourusername/ps03-visual-search.git
%cd ps03-visual-search
!pip install -q rasterio faiss-cpu pyyaml tqdm

# Add datasets as Kaggle datasets, then
!ln -s /kaggle/input/ps03-testing/*.tif /kaggle/working/ps03-visual-search/data/testing_set/

# Run search
!python scripts/build_index.py --targets data/testing_set --out cache/indexes --device cuda
!python scripts/run_search.py --chips "chips/Solar Panel/chip_01.tif" --index cache/indexes --name "Solar Panel" --out outputs/results.txt --device cuda
```

---

## 🔧 Troubleshooting Quick Reference

| Problem | Solution | Guide |
|---------|----------|-------|
| "python not recognized" | Add Python to PATH or use full path | LOCAL_SETUP.md |
| "No module named X" | `pip install -r requirements.txt` | LOCAL_SETUP.md |
| Spaces in class names | Use quotes: `--name "Solar Panel"` | THIS FILE |
| Dataset not found | Check paths in DATASET_SETUP.md | DATASET_SETUP.md |
| CUDA out of memory | Use `--device cpu` | LOCAL_SETUP.md |
| GitHub push fails | Use Personal Access Token | GITHUB_GUIDE.md |
| Large files in Git | Check .gitignore, don't commit .tif | GITHUB_GUIDE.md |
| Kaggle dataset mount | Use symlinks: `!ln -s /kaggle/input/...` | KAGGLE_SETUP.md |

---

## ✅ Pre-Flight Checklist

Before running search:

- [ ] Python 3.8+ installed
- [ ] Virtual environment activated
- [ ] All packages installed (`pip install -r requirements.txt`)
- [ ] Training set in `data/training_set/` (150 files)
- [ ] Testing set in `data/testing_set/` (40 files)
- [ ] Sample set in `data/sample_set/` (9+9 files)
- [ ] Query chips in `chips/[ClassName]/` (1-5 files)
- [ ] Class name uses quotes if it has spaces
- [ ] FAISS index built (`cache/indexes/`)

---

## 📞 Getting Help

1. **Check relevant guide:**
   - Datasets → `DATASET_SETUP.md`
   - Local → `LOCAL_SETUP.md`
   - Kaggle → `KAGGLE_SETUP.md`
   - GitHub → `GITHUB_GUIDE.md`
   - Technical → `README.md`

2. **Verify setup:**
   ```cmd
   python -c "from engine import read_tiff; print('OK')"
   ```

3. **Check file paths:**
   ```cmd
   dir data\testing_set\*.tif
   dir "chips\Solar Panel\*.tif"
   ```

4. **Read error messages carefully** - they usually tell you what's wrong!

---

## 🎓 Learning Path

**Beginner:** Start here
1. Read `DATASET_SETUP.md` - Understand folder structure
2. Read `QUICKSTART.md` - Get first result in 5 minutes
3. Try basic search locally

**Intermediate:** Deploy to cloud
4. Read `GITHUB_GUIDE.md` - Upload your code
5. Read `KAGGLE_SETUP.md` - Use free GPU
6. Run on Kaggle

**Advanced:** Train and optimize
7. Train embedder on your data
8. Tune hyperparameters in `configs/default.yaml`
9. Read `README.md` for architecture details

---

## 🎯 Success Criteria

You've successfully completed PS-03 when you can:

- ✅ Place all 3 datasets in correct folders
- ✅ Create query chips for your classes
- ✅ Build FAISS index from testing set
- ✅ Run search and generate results file
- ✅ Results file is in correct PS-03 format
- ✅ Class names appear correctly (with spaces if needed)
- ✅ Code is on GitHub (optional)
- ✅ Can run on Kaggle with GPU (optional)

---

## 🚀 What to Do Next

**You're at this step:**
1. ✅ Project created and organized
2. **→ Place your datasets** (read `DATASET_SETUP.md`)
3. Install and run locally (read `LOCAL_SETUP.md`)
4. Upload to GitHub (read `GITHUB_GUIDE.md`)
5. Deploy to Kaggle (read `KAGGLE_SETUP.md`)

**Start with `DATASET_SETUP.md` now!**

---

## 📚 All Documentation Files

| File | Purpose | When to Read |
|------|---------|--------------|
| `COMPLETE_GUIDE.md` | This file - overview | Start here |
| `DATASET_SETUP.md` | Where to put datasets | First step |
| `LOCAL_SETUP.md` | Run on Windows | Second step |
| `KAGGLE_SETUP.md` | Run on Kaggle | Optional |
| `GITHUB_GUIDE.md` | Push to GitHub | Before Kaggle |
| `README.md` | Full technical docs | Reference |
| `QUICKSTART.md` | 5-min quick start | Quick test |
| `PROJECT_SUMMARY.md` | What's built | Overview |

---

**🎉 You have everything you need to succeed in PS-03!**

**Next Step:** Open `DATASET_SETUP.md` and place your datasets! 🚀
