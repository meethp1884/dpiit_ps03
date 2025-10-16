# Your Dataset Structure & Usage Guide

## 📁 Current Dataset Structure

After analyzing your uploaded datasets, here's what you have:

```
new_ps03/data/
├── training_set/          ✅ 75 TIFF files (+ JPG previews)
│   ├── GC01PS03D0001.tif
│   ├── GC01PS03D0002.tif
│   └── ... (150 files total: 75 TIF + 75 JPG)
│
├── mock_set/              ⚠️ Should rename to "testing_set"
│   ├── GC01PS03T0013.tif
│   ├── GC01PS03T0022.tif
│   └── ... (81 files: 40 TIF + 40 JPG + README)
│
├── sample-set/            ⚠️ Has nested folder structure
│   └── sample-set/        ⚠️ Nested!
│       ├── Solar Panel/   ✅ Your class folders (keep exact names!)
│       │   ├── GC01PS03D0155.tif
│       │   ├── GC01PS03D0155.json  (GeoJSON format)
│       │   ├── GC01PS03T0240.tif
│       │   └── GC01PS03T0240.json
│       │
│       ├── Brick Kiln/
│       ├── Pond-1 & Pond-2/
│       ├── Pond-1,Pond-2 & Playground/
│       ├── Pond-2,STP & Sheds/
│       ├── MetroShed,STP & Sheds/
│       ├── Playground/
│       └── Sheds/
│
└── utilities/
    └── utilities/
        └── visualize.ipynb
```

---

## ⚠️ Issues to Fix

### Issue 1: Rename `mock_set` to `testing_set`

The scripts expect `testing_set` folder.

**Windows Command:**
```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03\data
rename mock_set testing_set
```

**Or manually:** Right-click `mock_set` → Rename → `testing_set`

### Issue 2: Flatten `sample-set` nested folder

Currently: `sample-set/sample-set/[Class folders]`
Should be: `sample_set/[Class folders]`

**Windows Commands:**
```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03\data

REM Move class folders up one level
move sample-set\sample-set\* sample_set\

REM Clean up
rmdir sample-set /S /Q

REM Rename to use underscore
REM (Already done above with move to sample_set)
```

**Or manually:**
1. Create new folder: `sample_set`
2. Move all class folders from `sample-set/sample-set/` to `sample_set/`
3. Delete empty `sample-set` folder

---

## 🎯 Your Class Names (EXACT - Keep These!)

Your sample-set has these classes with **special characters and spaces**:

1. **Solar Panel** ← Space
2. **Brick Kiln** ← Space
3. **Pond-1 & Pond-2** ← Spaces, ampersand, hyphen
4. **Pond-1,Pond-2 & Playground** ← Complex
5. **Pond-2,STP & Sheds** ← Complex
6. **MetroShed,STP & Sheds** ← Complex
7. **Playground** ← Simple
8. **Sheds** ← Simple

**✅ The code SUPPORTS all these names! Just use quotes in commands.**

---

## 🔧 GeoJSON Format

Your JSON files use GeoJSON format with MultiPolygon geometries:

```json
{
  "type": "FeatureCollection",
  "name": "GC01PS03D0155",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "Class Name": "Solar Panel"
      },
      "geometry": {
        "type": "MultiPolygon",
        "coordinates": [...]
      }
    }
  ]
}
```

**I've created a special script to handle this format!**

---

## 🚀 Step-by-Step: Extract Chips & Run Search

### Step 1: Fix Folder Structure (5 minutes)

```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03\data

REM Rename mock_set to testing_set
rename mock_set testing_set

REM Flatten sample-set
move sample-set\sample-set sample_set_temp
rmdir sample-set /S /Q
rename sample_set_temp sample_set
```

Verify:
```cmd
dir /B
```

Should show:
```
sample_set
testing_set
training_set
utilities
```

### Step 2: Extract Chips from GeoJSON (5 minutes)

**Option A: Extract chips for ONE class (e.g., Solar Panel)**

```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03

REM Activate virtual environment
venv\Scripts\activate

REM Extract chips from Solar Panel
python scripts\extract_chips_from_geojson.py ^
  --json "data\sample_set\Solar Panel\GC01PS03D0155.json" ^
  --out-dir chips ^
  --max-chips 5 ^
  --padding 10
```

This creates: `chips\Solar Panel\chip_01.tif`, `chip_02.tif`, etc.

**Option B: Extract ALL chips from ALL classes**

```cmd
python scripts\batch_extract_chips.py ^
  --sample-dir data\sample_set ^
  --out-dir chips ^
  --max-chips 5 ^
  --padding 10
```

This processes all class folders automatically!

### Step 3: Build FAISS Index (5-10 minutes)

```cmd
python scripts\build_index.py ^
  --targets data\testing_set ^
  --out cache\indexes ^
  --device cpu
```

### Step 4: Run Search (2 minutes)

**Search for "Solar Panel" class:**

```cmd
python scripts\run_search.py ^
  --chips "chips\Solar Panel\chip_01.tif" "chips\Solar Panel\chip_02.tif" ^
  --index cache\indexes ^
  --name "Solar Panel" ^
  --out outputs\solar_panel_results.txt ^
  --team YourTeamName
```

**Search for "Brick Kiln" class:**

```cmd
python scripts\run_search.py ^
  --chips "chips\Brick Kiln\chip_01.tif" ^
  --index cache\indexes ^
  --name "Brick Kiln" ^
  --out outputs\brick_kiln_results.txt ^
  --team YourTeamName
```

**Search for complex class names (use quotes!):**

```cmd
python scripts\run_search.py ^
  --chips "chips\Pond-1 & Pond-2\chip_01.tif" ^
  --index cache\indexes ^
  --name "Pond-1 & Pond-2" ^
  --out outputs\pond_results.txt ^
  --team YourTeamName
```

### Step 5: Combine Results for All Classes

```cmd
REM Create combined submission file
copy outputs\solar_panel_results.txt + outputs\brick_kiln_results.txt + outputs\pond_results.txt outputs\combined_submission.txt
```

---

## 📊 Expected Output Format

Your results file will look like:

```
159 797 331 853 Solar Panel GC01PS03T0013 0.923456
1579 827 1936 873 Solar Panel GC01PS03T0022 0.887234
...
x y w h Brick Kiln GC01PS03T0027 0.856789
...
x y w h Pond-1 & Pond-2 GC01PS03T0029 0.834567
```

**Notice:** Class names appear **exactly as you specified** (with spaces, ampersands, etc.)!

---

## 🎯 Quick Commands (After Setup)

**Full workflow for one class:**

```cmd
REM Activate environment
venv\Scripts\activate

REM Extract chips
python scripts\extract_chips_from_geojson.py ^
  --json "data\sample_set\Solar Panel\GC01PS03D0155.json" ^
  --out-dir chips

REM Build index (only once)
python scripts\build_index.py --targets data\testing_set --out cache\indexes

REM Search
python scripts\run_search.py ^
  --chips "chips\Solar Panel\chip_01.tif" ^
  --index cache\indexes ^
  --name "Solar Panel" ^
  --out outputs\results.txt
```

**Batch process all classes:**

```cmd
venv\Scripts\activate

REM Extract all chips
python scripts\batch_extract_chips.py --sample-dir data\sample_set --out-dir chips

REM Build index (only once)
python scripts\build_index.py --targets data\testing_set --out cache\indexes

REM Search each class (repeat for all classes)
python scripts\run_search.py --chips "chips\Solar Panel\chip_*.tif" --index cache\indexes --name "Solar Panel" --out outputs\solar.txt
python scripts\run_search.py --chips "chips\Brick Kiln\chip_*.tif" --index cache\indexes --name "Brick Kiln" --out outputs\brick.txt
REM ... etc

REM Combine all results
copy outputs\solar.txt + outputs\brick.txt + ... outputs\final_submission.txt
```

---

## 📝 Important Notes

### ✅ Class Names with Spaces/Special Characters

**Always use QUOTES around:**
- File paths: `"chips\Solar Panel\chip_01.tif"`
- Class names: `--name "Solar Panel"`
- Folder paths: `"data\sample_set\Pond-1 & Pond-2"`

### ✅ Output Format

The output file will use your **EXACT class names**:
- `Solar Panel` (not `Solar_Panel`)
- `Pond-1 & Pond-2` (not `Pond_1_and_Pond_2`)

This is **correct** for PS-03 submission!

### ✅ Multiple Annotations per Image

Some JSON files have multiple bounding boxes (e.g., `GC01PS03D0155.json` has 8 Solar Panel annotations). The script extracts up to `--max-chips` (default 5) chips per file.

### ✅ Padding

The `--padding 10` adds 10 pixels around each bounding box to capture context. Adjust if needed.

---

## 🔍 Verify Your Setup

**Check folder structure:**
```cmd
dir data /B
```
Should show: `sample_set`, `testing_set`, `training_set`, `utilities`

**Check class folders:**
```cmd
dir "data\sample_set" /B
```
Should show all your class folders

**Check extracted chips:**
```cmd
dir "chips\Solar Panel" /B
```
Should show: `chip_01.tif`, `chip_02.tif`, etc.

---

## 🎓 Summary of Changes

1. ✅ **Rename `mock_set` → `testing_set`**
2. ✅ **Flatten `sample-set/sample-set/` → `sample_set/`**
3. ✅ **Use new scripts:**
   - `extract_chips_from_geojson.py` - Extract from one JSON
   - `batch_extract_chips.py` - Extract from all JSONs
4. ✅ **Always use quotes for class names with spaces**
5. ✅ **Output will preserve exact class names**

---

## 🚀 Next Steps

1. Fix folder structure (commands above)
2. Extract chips using batch script
3. Build index
4. Run search for each class
5. Combine results into final submission

Good luck! 🎉
