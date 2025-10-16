# 🚀 Quick Start with YOUR Data

**Your datasets are uploaded! Follow these exact steps.**

---

## ✅ What You Have

- **Training set**: 75 TIFF files in `data/training_set/` ✓
- **Test/Mock set**: 40 TIFF files in `data/mock_set/` ⚠️ (needs rename)
- **Sample set**: Class folders in `data/sample-set/sample-set/` ⚠️ (needs flatten)
- **Classes**: Solar Panel, Brick Kiln, Pond-1 & Pond-2, etc.

---

## 🔧 Step 1: Fix Folder Structure (1 minute)

**Run this automated script:**

```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03
fix_dataset_structure.bat
```

**This will:**
- ✓ Rename `mock_set` → `testing_set`
- ✓ Flatten `sample-set/sample-set/` → `sample_set/`

**Verify:**
```cmd
dir data /B
```
Should show: `sample_set`, `testing_set`, `training_set`, `utilities`

---

## 🎯 Step 2: Install Dependencies (5 minutes)

```cmd
REM Create virtual environment
python -m venv venv

REM Activate it
venv\Scripts\activate

REM Install packages
pip install -r requirements.txt
```

Wait for installation to complete...

---

## 📦 Step 3: Extract Query Chips (2 minutes)

**Extract chips from ALL classes automatically:**

```cmd
python scripts\batch_extract_chips.py ^
  --sample-dir data\sample_set ^
  --out-dir chips ^
  --max-chips 5
```

**This creates:**
```
chips/
├── Solar Panel/
│   ├── chip_01.tif
│   ├── chip_02.tif
│   └── ... (up to 8 chips)
├── Brick Kiln/
├── Pond-1 & Pond-2/
└── ... (all your classes)
```

---

## 🔍 Step 4: Build FAISS Index (5-10 minutes)

```cmd
python scripts\build_index.py ^
  --targets data\testing_set ^
  --out cache\indexes ^
  --device cpu
```

**On GPU (if you have CUDA):**
```cmd
python scripts\build_index.py ^
  --targets data\testing_set ^
  --out cache\indexes ^
  --device cuda
```

Wait for "✓ Index built successfully"

---

## 🔎 Step 5: Run Visual Search (2 minutes per class)

**Search for "Solar Panel":**

```cmd
python scripts\run_search.py ^
  --chips "chips\Solar Panel\chip_01.tif" "chips\Solar Panel\chip_02.tif" ^
  --index cache\indexes ^
  --name "Solar Panel" ^
  --out outputs\solar_panel_results.txt ^
  --team YourTeamName
```

**Search for "Brick Kiln":**

```cmd
python scripts\run_search.py ^
  --chips "chips\Brick Kiln\chip_01.tif" ^
  --index cache\indexes ^
  --name "Brick Kiln" ^
  --out outputs\brick_kiln_results.txt ^
  --team YourTeamName
```

**Search for "Pond-1 & Pond-2":**

```cmd
python scripts\run_search.py ^
  --chips "chips\Pond-1 & Pond-2\chip_01.tif" ^
  --index cache\indexes ^
  --name "Pond-1 & Pond-2" ^
  --out outputs\pond_results.txt ^
  --team YourTeamName
```

**Repeat for all classes:**
- Playground
- Sheds
- Pond-1,Pond-2 & Playground
- Pond-2,STP & Sheds
- MetroShed,STP & Sheds

---

## 📄 Step 6: Combine Results (1 minute)

```cmd
REM Combine all class results into one submission file
copy /B ^
  outputs\solar_panel_results.txt + ^
  outputs\brick_kiln_results.txt + ^
  outputs\pond_results.txt + ^
  outputs\playground_results.txt + ^
  outputs\sheds_results.txt ^
  outputs\GC_PS03_16-Oct-2025_YourTeamName.txt
```

---

## ✅ View Your Results

```cmd
notepad outputs\GC_PS03_16-Oct-2025_YourTeamName.txt
```

**Format:**
```
x_min y_min x_max y_max Solar Panel GC01PS03T0013 0.923456
x_min y_min x_max y_max Solar Panel GC01PS03T0022 0.887234
x_min y_min x_max y_max Brick Kiln GC01PS03T0027 0.856789
x_min y_min x_max y_max Pond-1 & Pond-2 GC01PS03T0029 0.834567
...
```

**Notice:** Class names appear EXACTLY as you specified (with spaces and special characters)!

---

## 🎯 All Commands in One Block

**Copy-paste this entire block:**

```cmd
REM Fix structure
fix_dataset_structure.bat

REM Activate environment
venv\Scripts\activate

REM Extract chips
python scripts\batch_extract_chips.py --sample-dir data\sample_set --out-dir chips

REM Build index
python scripts\build_index.py --targets data\testing_set --out cache\indexes --device cpu

REM Search all classes
python scripts\run_search.py --chips "chips\Solar Panel\chip_01.tif" "chips\Solar Panel\chip_02.tif" --index cache\indexes --name "Solar Panel" --out outputs\solar.txt --team YourTeam
python scripts\run_search.py --chips "chips\Brick Kiln\chip_01.tif" --index cache\indexes --name "Brick Kiln" --out outputs\brick.txt --team YourTeam
python scripts\run_search.py --chips "chips\Pond-1 & Pond-2\chip_01.tif" --index cache\indexes --name "Pond-1 & Pond-2" --out outputs\pond.txt --team YourTeam
python scripts\run_search.py --chips "chips\Playground\chip_01.tif" --index cache\indexes --name "Playground" --out outputs\playground.txt --team YourTeam
python scripts\run_search.py --chips "chips\Sheds\chip_01.tif" --index cache\indexes --name "Sheds" --out outputs\sheds.txt --team YourTeam

REM Combine results
copy /B outputs\solar.txt + outputs\brick.txt + outputs\pond.txt + outputs\playground.txt + outputs\sheds.txt outputs\final_submission.txt

REM View results
notepad outputs\final_submission.txt
```

---

## 📊 Expected Timeline

- **Step 1 (Fix folders):** 1 minute
- **Step 2 (Install):** 5 minutes
- **Step 3 (Extract chips):** 2 minutes
- **Step 4 (Build index):** 5-10 minutes (CPU) / 2 minutes (GPU)
- **Step 5 (Search all classes):** 10-15 minutes
- **Step 6 (Combine):** 1 minute

**Total: ~25-35 minutes to complete submission!**

---

## ⚠️ Important Notes

1. **Always use quotes** for class names with spaces:
   - `"Solar Panel"` ✓
   - `Solar Panel` ✗

2. **Class names are preserved** in output:
   - Input: `"Solar Panel"`
   - Output: `Solar Panel GC01PS03T0013 0.92`

3. **Multiple chips per class** improves accuracy:
   - Use 2-5 chips per class
   - Script extracts up to 5 from each JSON automatically

4. **GPU is much faster** but optional:
   - CPU: ~10 minutes for indexing
   - GPU: ~2 minutes for indexing

---

## 🆘 Troubleshooting

**"python not recognized"**
→ Use full path: `C:\Users\meeth\AppData\Local\Programs\Python\Python39\python.exe`

**"No module named 'rasterio'"**
→ Run: `pip install -r requirements.txt`

**"File not found" errors**
→ Check paths use quotes: `"chips\Solar Panel\chip_01.tif"`

**"CUDA out of memory"**
→ Use `--device cpu` instead of `--device cuda`

---

## ✅ Verification Checklist

Before running search:
- [ ] Folder structure fixed (testing_set, sample_set exist)
- [ ] Virtual environment activated (`(venv)` in prompt)
- [ ] Dependencies installed
- [ ] Chips extracted (check `chips/` folder)
- [ ] Index built (check `cache/indexes/` folder)

---

## 🚀 You're Ready!

Run the commands above and you'll have your PS-03 submission file in ~30 minutes!

**Good luck! 🎉**
