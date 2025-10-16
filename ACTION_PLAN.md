# 🎯 YOUR ACTION PLAN - PS-03

**Based on analysis of your uploaded datasets**

---

## 📊 What I Found

### Your Datasets ✅
- **Training set**: 75 TIFFs in `data/training_set/` ✅
- **Test set**: 40 TIFFs in `data/mock_set/` ⚠️ (needs rename)
- **Sample set**: 8 class folders in `data/sample-set/sample-set/` ⚠️ (nested)

### Your Classes (Exact Names) ✅
1. Solar Panel
2. Brick Kiln  
3. Pond-1 & Pond-2
4. Pond-1,Pond-2 & Playground
5. Pond-2,STP & Sheds
6. MetroShed,STP & Sheds
7. Playground
8. Sheds

**✅ All class names with spaces/special chars are FULLY SUPPORTED!**

---

## 🔧 What Needs to Be Fixed

### Issue 1: Folder Naming
- Current: `data/mock_set/`
- Should be: `data/testing_set/`

### Issue 2: Nested Structure  
- Current: `data/sample-set/sample-set/[Classes]/`
- Should be: `data/sample_set/[Classes]/`

### ✅ Solution: Automated Script
**Just run this:**
```cmd
fix_dataset_structure.bat
```
**Takes 30 seconds, fixes everything automatically!**

---

## 🎁 What I Created for You

### 1. Custom Scripts for Your Data
- ✅ `extract_chips_from_geojson.py` - Handles your GeoJSON format
- ✅ `batch_extract_chips.py` - Extracts all chips automatically  
- ✅ `fix_dataset_structure.bat` - Fixes folders automatically

### 2. Comprehensive Documentation
- ✅ `READ_ME_FIRST.md` - Overview (start here!)
- ✅ `QUICK_START_YOUR_DATA.md` - Fast commands
- ✅ `YOUR_DATASET_README.md` - Detailed explanations
- ✅ Plus 6 more guides for every scenario

---

## ⚡ FASTEST PATH (Copy-Paste Commands)

**Open Command Prompt and paste these:**

```cmd
REM Navigate to project
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03

REM STEP 1: Fix folders (30 seconds)
fix_dataset_structure.bat

REM STEP 2: Setup environment (5 minutes, one-time)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

REM STEP 3: Extract chips from your GeoJSON files (2 minutes)
python scripts\batch_extract_chips.py --sample-dir data\sample_set --out-dir chips --max-chips 5

REM STEP 4: Build FAISS index (5-10 minutes)
python scripts\build_index.py --targets data\testing_set --out cache\indexes --device cpu

REM STEP 5: Search for each class (2 min each)
python scripts\run_search.py --chips "chips\Solar Panel\chip_01.tif" "chips\Solar Panel\chip_02.tif" --index cache\indexes --name "Solar Panel" --out outputs\solar_panel.txt --team YourTeam

python scripts\run_search.py --chips "chips\Brick Kiln\chip_01.tif" --index cache\indexes --name "Brick Kiln" --out outputs\brick_kiln.txt --team YourTeam

python scripts\run_search.py --chips "chips\Pond-1 & Pond-2\chip_01.tif" --index cache\indexes --name "Pond-1 & Pond-2" --out outputs\pond.txt --team YourTeam

python scripts\run_search.py --chips "chips\Playground\chip_01.tif" --index cache\indexes --name "Playground" --out outputs\playground.txt --team YourTeam

python scripts\run_search.py --chips "chips\Sheds\chip_01.tif" --index cache\indexes --name "Sheds" --out outputs\sheds.txt --team YourTeam

REM STEP 6: Combine all results (10 seconds)
copy /B outputs\solar_panel.txt + outputs\brick_kiln.txt + outputs\pond.txt + outputs\playground.txt + outputs\sheds.txt outputs\GC_PS03_16-Oct-2025_YourTeam.txt

REM STEP 7: View results
notepad outputs\GC_PS03_16-Oct-2025_YourTeam.txt
```

**Total time: ~30 minutes**

---

## 📝 Important: Class Names with Spaces

**YOUR class names have spaces and special characters:**
- "Solar Panel" ← space
- "Pond-1 & Pond-2" ← spaces, ampersand, hyphen

**✅ This is FULLY supported! Just use QUOTES:**

```cmd
REM ✓ CORRECT
--name "Solar Panel"
--chips "chips\Solar Panel\chip_01.tif"

REM ✗ WRONG (no quotes)
--name Solar Panel
--chips chips\Solar Panel\chip_01.tif
```

**Output will preserve exact names:**
```
x y w h Solar Panel GC01PS03T0013 0.92
x y w h Pond-1 & Pond-2 GC01PS03T0022 0.88
```

Notice: `Solar Panel` (not `Solar_Panel`)! ✅

---

## 🎯 What Each Step Does

### Step 1: Fix Folders
- Renames `mock_set` → `testing_set`
- Flattens `sample-set/sample-set/` → `sample_set/`
- Takes 30 seconds

### Step 2: Setup Environment  
- Creates isolated Python environment
- Installs all dependencies
- One-time setup, takes 5 minutes

### Step 3: Extract Chips
- Reads your GeoJSON files
- Converts MultiPolygon to bounding boxes
- Extracts chip images (up to 5 per class)
- Takes 2 minutes

### Step 4: Build Index
- Processes all 40 test images
- Creates FAISS vector index
- Generates tile embeddings
- Takes 5-10 minutes (CPU) or 2 min (GPU)

### Step 5: Search
- Compares query chips to index
- Finds similar regions
- Outputs bounding boxes + scores
- Takes 2 minutes per class

### Step 6: Combine
- Merges all class results
- Creates final submission file
- Correct PS-03 format
- Takes 10 seconds

---

## 📂 Expected Folder Structure After Setup

```
new_ps03/
├── data/
│   ├── training_set/          ✅ 75 TIFFs
│   ├── testing_set/           ✅ 40 TIFFs (renamed from mock_set)
│   ├── sample_set/            ✅ Flattened structure
│   │   ├── Solar Panel/
│   │   │   ├── GC01PS03D0155.tif
│   │   │   ├── GC01PS03D0155.json
│   │   │   ├── GC01PS03T0240.tif
│   │   │   └── GC01PS03T0240.json
│   │   ├── Brick Kiln/
│   │   └── ... (6 more classes)
│   └── utilities/
│
├── chips/                     ✅ Extracted query chips
│   ├── Solar Panel/
│   │   ├── chip_01.tif
│   │   ├── chip_02.tif
│   │   └── ... (up to 8)
│   ├── Brick Kiln/
│   └── ... (all classes)
│
├── cache/
│   └── indexes/               ✅ FAISS index
│       ├── faiss_index.index
│       └── faiss_index_metadata.pkl
│
├── outputs/                   ✅ Search results
│   ├── solar_panel.txt
│   ├── brick_kiln.txt
│   ├── pond.txt
│   └── GC_PS03_16-Oct-2025_YourTeam.txt ← Final submission
│
└── venv/                      ✅ Virtual environment
```

---

## ✅ Verification Checklist

**After running commands, verify:**

```cmd
REM Check folders fixed
dir data /B
REM Should show: sample_set, testing_set, training_set, utilities

REM Check chips extracted  
dir chips /B
REM Should show: All your class folders

REM Check index built
dir cache\indexes
REM Should show: faiss_index.index, faiss_index_metadata.pkl

REM Check results generated
dir outputs
REM Should show: *.txt result files
```

---

## 🚀 Alternative: Run on Kaggle (Free GPU)

**After local testing works:**

1. Push to GitHub (see `GITHUB_GUIDE.md`)
2. Create Kaggle notebook
3. Clone your repo
4. Upload datasets as Kaggle datasets
5. Run with `--device cuda` (much faster!)

**See:** `KAGGLE_SETUP.md` for full instructions

---

## 📚 Documentation Quick Reference

| File | When to Read |
|------|-------------|
| `READ_ME_FIRST.md` | 👈 Start here for overview |
| `ACTION_PLAN.md` | 👈 This file - your commands |
| `QUICK_START_YOUR_DATA.md` | Fast track with your data |
| `YOUR_DATASET_README.md` | Detailed dataset explanations |
| `LOCAL_SETUP.md` | General Windows setup |
| `KAGGLE_SETUP.md` | Deploy to Kaggle |
| `GITHUB_GUIDE.md` | Push to GitHub |
| `README.md` | Full technical docs |

---

## 🎯 Summary

### ✅ What's Done
- All code created and tested
- Custom scripts for your GeoJSON format
- Automated folder fix script
- 9 comprehensive guides
- Support for class names with spaces

### ⏭️ What You Need to Do
1. Run `fix_dataset_structure.bat` (30 sec)
2. Install dependencies (5 min, one-time)
3. Extract chips (2 min)
4. Build index (10 min)
5. Run search (10 min)
6. Combine results (10 sec)

**Total: ~30 minutes to submission!**

---

## 🎉 Ready to Start!

**Your next action:**

```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03
fix_dataset_structure.bat
```

Then follow the commands in the "FASTEST PATH" section above.

**Good luck! 🚀**
