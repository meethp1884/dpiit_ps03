# Dataset Setup Guide - PS-03

## 📁 Where to Put Your Datasets

### Exact Folder Structure

Create this structure inside your `new_ps03` folder:

```
new_ps03/
├── data/
│   ├── training_set/          ← PUT YOUR TRAIN DATASET HERE
│   │   ├── GC01PS03D0001.tif
│   │   ├── GC01PS03D0002.tif
│   │   └── ... (all 150 training TIFFs)
│   │
│   ├── testing_set/           ← PUT YOUR MOCK/TEST DATASET HERE
│   │   ├── GC01PS03T0001.tif
│   │   ├── GC01PS03T0002.tif
│   │   └── ... (all 40 test TIFFs)
│   │
│   └── sample_set/            ← PUT YOUR SAMPLE DATASET HERE
│       ├── GC01PS03S0001.tif
│       ├── GC01PS03S0001.json
│       ├── GC01PS03S0002.tif
│       ├── GC01PS03S0002.json
│       └── ... (all 9 sample TIFFs + JSONs)
│
└── chips/                     ← PUT YOUR QUERY CHIPS HERE (organized by class)
    ├── Solar Panel/           ← Use EXACT class name (spaces allowed!)
    │   ├── chip_01.tif
    │   ├── chip_02.tif
    │   └── chip_03.tif
    │
    ├── Pond-1/
    │   └── chip_01.tif
    │
    └── Swimming Pool/
        └── chip_01.tif
```

---

## 📝 Step-by-Step Dataset Placement

### Step 1: Create Folders

**Windows (Command Prompt):**
```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03
mkdir data\training_set
mkdir data\testing_set
mkdir data\sample_set
mkdir chips
```

**Linux/Mac (Terminal):**
```bash
cd new_ps03
mkdir -p data/training_set
mkdir -p data/testing_set
mkdir -p data/sample_set
mkdir chips
```

### Step 2: Copy Your Datasets

**Option A - Manual Copy (Recommended for beginners):**

1. **Training Set:**
   - Open your training dataset folder
   - Copy ALL .tif files
   - Paste into `new_ps03/data/training_set/`

2. **Testing/Mock Set:**
   - Open your test dataset folder
   - Copy ALL .tif files
   - Paste into `new_ps03/data/testing_set/`

3. **Sample Set:**
   - Open your sample dataset folder
   - Copy ALL .tif AND .json files
   - Paste into `new_ps03/data/sample_set/`

**Option B - Command Line:**

**Windows:**
```cmd
REM Copy training set
xcopy "C:\path\to\your\training_dataset\*.tif" "data\training_set\" /Y

REM Copy testing set
xcopy "C:\path\to\your\test_dataset\*.tif" "data\testing_set\" /Y

REM Copy sample set (TIFFs and JSONs)
xcopy "C:\path\to\your\sample_dataset\*.*" "data\sample_set\" /Y
```

**Linux/Mac:**
```bash
# Copy training set
cp /path/to/your/training_dataset/*.tif data/training_set/

# Copy testing set
cp /path/to/your/test_dataset/*.tif data/testing_set/

# Copy sample set
cp /path/to/your/sample_dataset/* data/sample_set/
```

### Step 3: Verify Datasets

**Windows:**
```cmd
dir data\training_set\*.tif /B | find /C ".tif"
dir data\testing_set\*.tif /B | find /C ".tif"
dir data\sample_set\*.tif /B | find /C ".tif"
```

**Linux/Mac:**
```bash
ls data/training_set/*.tif | wc -l
ls data/testing_set/*.tif | wc -l
ls data/sample_set/*.tif | wc -l
```

Expected output:
- Training set: 150 files
- Testing set: 40 files
- Sample set: 9 files

---

## 🎯 Creating Query Chips

### Method 1: Extract from Sample Set JSONs

```bash
# Windows
python scripts\make_chip_from_json.py ^
  --json data\sample_set\GC01PS03S0001.json ^
  --out "chips\Solar Panel\chip_01.tif"

# Linux/Mac
python scripts/make_chip_from_json.py \
  --json data/sample_set/GC01PS03S0001.json \
  --out "chips/Solar Panel/chip_01.tif"
```

### Method 2: Manual Extraction (if you have coordinates)

Create a simple script or use the Web UI to draw bounding boxes.

### Method 3: Use Existing Chips

If you already have chip files:
```
chips/
└── Solar Panel/          ← Create folder with EXACT class name
    ├── chip_01.tif
    ├── chip_02.tif
    └── chip_03.tif       ← Up to 5 chips per class
```

---

## ⚠️ Important Notes

1. **File Format:** Only .tif or .tiff files (4-band: B,G,R,NIR)
2. **Naming:** Original filenames don't matter, but keep them organized
3. **Class Names:** Use EXACT names (spaces and special characters are OK!)
4. **Chip Limit:** Maximum 5 query chips per class
5. **JSON Files:** Should match TIFF names in sample_set (e.g., `GC01PS03S0001.tif` + `GC01PS03S0001.json`)

---

## ✅ Verification Checklist

- [ ] Training set: 150 TIFF files in `data/training_set/`
- [ ] Testing set: 40 TIFF files in `data/testing_set/`
- [ ] Sample set: 9 TIFF + 9 JSON files in `data/sample_set/`
- [ ] Chips folder created: `chips/`
- [ ] Class folders created with exact names (e.g., `chips/Solar Panel/`)
- [ ] Query chips placed in class folders (1-5 per class)

---

## 🚀 Next Steps

After dataset placement, proceed to:
1. **Local Setup** → See `LOCAL_SETUP.md`
2. **Kaggle Setup** → See `KAGGLE_SETUP.md`
3. **Run Search** → See `README.md` or `QUICKSTART.md`
