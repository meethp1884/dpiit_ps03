# 🚀 START HERE - PS-03 Visual Search

## Welcome! Your PS-03 project is ready to use.

---

## ⚡ Quick Navigation

**Choose your path:**

### 🆕 First Time User?
👉 **Read:** `COMPLETE_GUIDE.md` (overview of everything)
👉 **Then:** `DATASET_SETUP.md` (where to put your files)
👉 **Then:** `LOCAL_SETUP.md` (run on your machine)

### ⏱️ Want Quickest Start?
👉 **Read:** `QUICKSTART.md` (5 minutes to first result)

### 🔍 Looking for Something Specific?

| I want to... | Read this file |
|--------------|---------------|
| Know where to put my datasets (train/test/sample) | `DATASET_SETUP.md` |
| Run on my Windows machine | `LOCAL_SETUP.md` |
| Run on Kaggle with free GPU | `KAGGLE_SETUP.md` |
| Push my code to GitHub | `GITHUB_GUIDE.md` |
| Handle class names with spaces ("Solar Panel") | `LOCAL_SETUP.md` or `COMPLETE_GUIDE.md` |
| Understand the technical details | `README.md` |
| See what was built | `PROJECT_SUMMARY.md` |

---

## 📋 Your Question Checklist

### ✅ Where do I put my 3 datasets?
**Answer in:** `DATASET_SETUP.md`

Quick answer:
```
new_ps03/
├── data/
│   ├── training_set/    ← Your training dataset (150 TIFFs)
│   ├── testing_set/     ← Your test/mock dataset (40 TIFFs)
│   └── sample_set/      ← Your sample dataset (9 TIFFs + JSONs)
```

### ✅ How do I run on my machine?
**Answer in:** `LOCAL_SETUP.md`

Quick commands:
```cmd
venv\Scripts\activate
python scripts\build_index.py --targets data\testing_set --out cache\indexes
python scripts\run_search.py --chips "chips\Solar Panel\chip_01.tif" --index cache\indexes --name "Solar Panel" --out outputs\results.txt
```

### ✅ How do I run on Kaggle?
**Answer in:** `KAGGLE_SETUP.md`

Quick steps:
1. Upload code + data to Kaggle
2. Create notebook with GPU
3. Run scripts
4. Download results

### ✅ How do I push to GitHub?
**Answer in:** `GITHUB_GUIDE.md`

Quick commands:
```cmd
git init
git add .
git commit -m "Initial commit"
git push origin main
```

### ✅ My class is "Solar Panel" (with space) - do I rename it?
**Answer:** NO! Keep the space, just use quotes.

**In commands:**
```cmd
mkdir "chips\Solar Panel"
python scripts\run_search.py --name "Solar Panel" --chips "chips\Solar Panel\chip_01.tif" ...
```

**In output:**
```
x_min y_min x_max y_max Solar Panel filename.tif 0.92
```

---

## 🎯 Recommended Reading Order

### Day 1 (1-2 hours)
1. ✅ `START_HERE.md` (this file) - 5 min
2. ✅ `COMPLETE_GUIDE.md` - Overview - 10 min
3. ✅ `DATASET_SETUP.md` - Place datasets - 20 min
4. ✅ `LOCAL_SETUP.md` - Install & run - 30 min
5. ✅ Run your first search! - 15 min

### Day 2 (Optional - 2-3 hours)
6. ✅ `GITHUB_GUIDE.md` - Upload code - 30 min
7. ✅ `KAGGLE_SETUP.md` - Deploy to cloud - 1 hour
8. ✅ Train embedder - 1-2 hours

### Anytime (Reference)
9. 📖 `README.md` - Technical documentation
10. 📖 `PROJECT_SUMMARY.md` - What was built

---

## ⚡ Ultra-Quick Start (Experienced Users)

```cmd
REM 1. Place datasets
mkdir data\training_set data\testing_set data\sample_set "chips\Solar Panel"
REM (Copy your TIFFs to these folders)

REM 2. Install
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

REM 3. Build & Search
python scripts\build_index.py --targets data\testing_set --out cache\indexes
python scripts\run_search.py --chips "chips\Solar Panel\chip_01.tif" --index cache\indexes --name "Solar Panel" --out outputs\results.txt
```

Done! Results in `outputs\results.txt`

---

## 📁 Project Structure

```
new_ps03/
├── 📘 START_HERE.md              ← You are here!
├── 📘 COMPLETE_GUIDE.md           ← Overview of everything
├── 📘 DATASET_SETUP.md            ← Where to put datasets
├── 📘 LOCAL_SETUP.md              ← Run on Windows
├── 📘 KAGGLE_SETUP.md             ← Run on Kaggle
├── 📘 GITHUB_GUIDE.md             ← Push to GitHub
├── 📘 README.md                   ← Technical docs
├── 📘 QUICKSTART.md               ← 5-min quick start
├── 📘 PROJECT_SUMMARY.md          ← What was built
│
├── 🐍 engine/                     ← Core Python modules
├── 🌐 api/                        ← FastAPI backend
├── ⚛️ ui/                         ← React frontend
├── 🔧 scripts/                    ← CLI tools
├── ⚙️ configs/                    ← Configuration
├── 🧪 tests/                      ← Unit tests
│
├── 📁 data/                       ← Your datasets go here
├── 📁 chips/                      ← Your query chips
├── 📁 cache/                      ← Generated indexes
├── 📁 outputs/                    ← Search results
└── 📦 venv/                       ← Virtual environment
```

---

## 🎓 Learning Path

**Complete Beginner:**
→ Read `COMPLETE_GUIDE.md` for gentle introduction
→ Follow `DATASET_SETUP.md` step-by-step
→ Use `LOCAL_SETUP.md` with detailed explanations

**Some Experience:**
→ Skim `COMPLETE_GUIDE.md` 
→ Check `DATASET_SETUP.md` for folder structure
→ Jump to `LOCAL_SETUP.md` workflow section

**Experienced Developer:**
→ Read this file
→ Check `README.md` architecture section
→ Run commands from "Ultra-Quick Start" above

---

## ✅ What You Need

### Required (to run search):
- ✅ Python 3.8+
- ✅ Your 3 datasets (train, test, sample)
- ✅ Query chips (1-5 per class)
- ✅ 8GB RAM minimum
- ✅ Windows/Linux/Mac

### Optional (for better performance):
- CUDA GPU (10x faster)
- 16GB RAM (for large datasets)
- Kaggle account (free GPU)
- GitHub account (for code backup)

---

## 🚨 Important Notes

### ✅ DO:
- Use quotes for class names with spaces: `"Solar Panel"`
- Place datasets in correct folders (see `DATASET_SETUP.md`)
- Activate virtual environment before running
- Read error messages - they tell you what's wrong!

### ❌ DON'T:
- Rename "Solar Panel" to "Solar_Panel" (keep original name!)
- Upload large .tif files to GitHub (.gitignore excludes them)
- Run without virtual environment
- Skip dataset setup step

---

## 🎯 Your Next Step

**Based on what you need:**

### If you haven't placed datasets yet:
👉 **Open:** `DATASET_SETUP.md`

### If datasets are placed:
👉 **Open:** `LOCAL_SETUP.md` (install & run)

### If everything is set up and you want quick commands:
👉 **Open:** `QUICKSTART.md`

### If you want to understand everything first:
👉 **Open:** `COMPLETE_GUIDE.md`

### If you want technical details:
👉 **Open:** `README.md`

---

## 💡 Pro Tips

1. **Always use virtual environment:**
   ```cmd
   venv\Scripts\activate
   ```

2. **Use quotes for paths with spaces:**
   ```cmd
   --chips "chips\Solar Panel\chip_01.tif"
   --name "Solar Panel"
   ```

3. **Start with CPU, switch to GPU later:**
   ```cmd
   --device cpu    # Safe, works everywhere
   --device cuda   # Faster, needs GPU
   ```

4. **Check status frequently:**
   ```cmd
   git status           # For Git
   python --version     # For Python
   dir data\testing_set # For datasets
   ```

5. **Read the specific guide for your task** - don't try to remember everything!

---

## 🆘 Need Help?

**Error occurred?**
1. Read the error message (it usually tells you what's wrong)
2. Check the relevant guide (see table above)
3. Verify your setup (datasets, virtual env, paths)

**Not sure what to do?**
1. Start with `COMPLETE_GUIDE.md`
2. Follow recommended reading order
3. Take it one step at a time

**Want to understand more?**
1. Check `README.md` for technical details
2. Look at code in `engine/` folder
3. Read inline documentation

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Activate env | `venv\Scripts\activate` |
| Build index | `python scripts\build_index.py --targets data\testing_set --out cache\indexes` |
| Run search | `python scripts\run_search.py --chips "chips\Solar Panel\chip_01.tif" --index cache\indexes --name "Solar Panel" --out outputs\results.txt` |
| Train model | `python scripts\train_embedder.py --data data\training_set --epochs 50 --device cuda` |
| View results | `notepad outputs\results.txt` |
| Git push | `git add . && git commit -m "message" && git push` |

---

## 🎉 Ready to Begin!

**Your project is complete and ready to use.**

All code, documentation, and examples are in place.

**Recommended first step:**

If datasets are not placed yet → Open `DATASET_SETUP.md`

If datasets are placed → Open `LOCAL_SETUP.md`

If you want overview first → Open `COMPLETE_GUIDE.md`

---

**Good luck with PS-03! 🚀**
