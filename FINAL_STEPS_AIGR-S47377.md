# 🎯 FINAL STEPS - Team AIGR-S47377

**Everything is configured with your team name. Follow these exact steps to get your submission file.**

---

## ✅ Configuration Status

- ✅ **Team Name**: AIGR-S47377 (configured in system)
- ✅ **Output Format**: PS-03 Standard (space-delimited)
- ✅ **Output File**: ONE combined file for all 8 classes
- ✅ **Filename**: `GC_PS03_16-Oct-2025_AIGR-S47377.txt`
- ✅ **Accuracy Settings**: Optimized (tile_size=512, top_k=1000, NMS=0.3)

---

## 🚀 STEP-BY-STEP FINAL COMMANDS

### Step 0: Prerequisites (One-Time Setup - 5 minutes)

**If you haven't done this yet:**

```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03

REM Create virtual environment
python -m venv venv

REM Activate it
venv\Scripts\activate

REM Install all dependencies
pip install -r requirements.txt
```

**Wait for installation to complete** (shows "Successfully installed...")

---

### ⚡ AUTOMATED WAY (RECOMMENDED)

**Just run this ONE command:**

```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03
FINAL_RUN_AIGR-S47377.bat
```

**This will:**
1. ✅ Extract chips from all 8 classes (2 min)
2. ✅ Build FAISS index (5-10 min)
3. ✅ Search for all classes (10-15 min)
4. ✅ Combine into ONE file (10 sec)
5. ✅ Show summary and open result

**Total Time: ~25-35 minutes**

**Then skip to "Step 6: Review Results" below!**

---

### 🔧 MANUAL WAY (Step-by-Step)

**If you prefer to run each step manually:**

#### Step 1: Extract Query Chips (2 minutes)

```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03
venv\Scripts\activate

python scripts\batch_extract_chips.py ^
  --sample-dir data\sample_set ^
  --out-dir chips ^
  --max-chips 5 ^
  --padding 20
```

**Wait for:** "✓ Total chips extracted: XX"

---

#### Step 2: Build FAISS Index (5-10 minutes)

```cmd
python scripts\build_index.py ^
  --targets data\testing_set ^
  --out cache\indexes ^
  --config configs\default.yaml ^
  --device cpu
```

**Or with GPU (much faster):**
```cmd
python scripts\build_index.py ^
  --targets data\testing_set ^
  --out cache\indexes ^
  --config configs\default.yaml ^
  --device cuda
```

**Wait for:** "✓ Index built successfully"

---

#### Step 3: Search for ALL 8 Classes (10-15 minutes)

**Class 1: Solar Panel**
```cmd
python scripts\run_search.py ^
  --chips "chips\Solar Panel\chip_01.tif" "chips\Solar Panel\chip_02.tif" "chips\Solar Panel\chip_03.tif" ^
  --index cache\indexes ^
  --name "Solar Panel" ^
  --out outputs\temp_solar_panel.txt ^
  --team AIGR-S47377 ^
  --config configs\default.yaml
```

**Class 2: Brick Kiln**
```cmd
python scripts\run_search.py ^
  --chips "chips\Brick Kiln\chip_01.tif" "chips\Brick Kiln\chip_02.tif" ^
  --index cache\indexes ^
  --name "Brick Kiln" ^
  --out outputs\temp_brick_kiln.txt ^
  --team AIGR-S47377 ^
  --config configs\default.yaml
```

**Class 3: Pond-1 & Pond-2**
```cmd
python scripts\run_search.py ^
  --chips "chips\Pond-1 & Pond-2\chip_01.tif" ^
  --index cache\indexes ^
  --name "Pond-1 & Pond-2" ^
  --out outputs\temp_pond_1_2.txt ^
  --team AIGR-S47377 ^
  --config configs\default.yaml
```

**Class 4: Pond-1,Pond-2 & Playground**
```cmd
python scripts\run_search.py ^
  --chips "chips\Pond-1,Pond-2 & Playground\chip_01.tif" ^
  --index cache\indexes ^
  --name "Pond-1,Pond-2 & Playground" ^
  --out outputs\temp_pond_playground.txt ^
  --team AIGR-S47377 ^
  --config configs\default.yaml
```

**Class 5: Pond-2,STP & Sheds**
```cmd
python scripts\run_search.py ^
  --chips "chips\Pond-2,STP & Sheds\chip_01.tif" ^
  --index cache\indexes ^
  --name "Pond-2,STP & Sheds" ^
  --out outputs\temp_pond_stp_sheds.txt ^
  --team AIGR-S47377 ^
  --config configs\default.yaml
```

**Class 6: MetroShed,STP & Sheds**
```cmd
python scripts\run_search.py ^
  --chips "chips\MetroShed,STP & Sheds\chip_01.tif" ^
  --index cache\indexes ^
  --name "MetroShed,STP & Sheds" ^
  --out outputs\temp_metro_stp_sheds.txt ^
  --team AIGR-S47377 ^
  --config configs\default.yaml
```

**Class 7: Playground**
```cmd
python scripts\run_search.py ^
  --chips "chips\Playground\chip_01.tif" ^
  --index cache\indexes ^
  --name "Playground" ^
  --out outputs\temp_playground.txt ^
  --team AIGR-S47377 ^
  --config configs\default.yaml
```

**Class 8: Sheds**
```cmd
python scripts\run_search.py ^
  --chips "chips\Sheds\chip_01.tif" "chips\Sheds\chip_02.tif" ^
  --index cache\indexes ^
  --name "Sheds" ^
  --out outputs\temp_sheds.txt ^
  --team AIGR-S47377 ^
  --config configs\default.yaml
```

---

#### Step 4: Combine ALL Results into ONE File (10 seconds)

```cmd
copy /B ^
  outputs\temp_solar_panel.txt + ^
  outputs\temp_brick_kiln.txt + ^
  outputs\temp_pond_1_2.txt + ^
  outputs\temp_pond_playground.txt + ^
  outputs\temp_pond_stp_sheds.txt + ^
  outputs\temp_metro_stp_sheds.txt + ^
  outputs\temp_playground.txt + ^
  outputs\temp_sheds.txt ^
  outputs\GC_PS03_16-Oct-2025_AIGR-S47377.txt
```

---

#### Step 5: Clean Up Temp Files

```cmd
del /Q outputs\temp_*.txt
```

---

### Step 6: Review Results

```cmd
notepad outputs\GC_PS03_16-Oct-2025_AIGR-S47377.txt
```

---

## 📊 Expected Output Format (PS-03 Standard)

Your final file will contain ONE line per detection:

```
x_min y_min x_max y_max class_name target_filename score
```

**Example:**
```
159 797 331 853 Solar Panel GC01PS03T0013 0.923456
1579 827 1936 873 Solar Panel GC01PS03T0022 0.887234
256 384 512 640 Brick Kiln GC01PS03T0027 0.856789
100 200 300 400 Pond-1 & Pond-2 GC01PS03T0029 0.834567
50 100 150 200 Playground GC01PS03T0041 0.801234
...
```

**Key Points:**
- ✅ **Space-delimited** (not comma)
- ✅ **Class names with spaces preserved** (e.g., "Solar Panel", "Pond-1 & Pond-2")
- ✅ **All classes in ONE file**
- ✅ **Sorted by confidence score** (highest first per class)
- ✅ **Format matches PS-03 requirements exactly**

---

## ✅ Verification Checklist

**Before submitting, verify:**

- [ ] File name: `GC_PS03_16-Oct-2025_AIGR-S47377.txt`
- [ ] Format: Space-delimited (7 columns)
- [ ] Contains detections from all 8 classes
- [ ] Class names match your sample-set exactly
- [ ] Bounding boxes are integers (x_min, y_min, x_max, y_max)
- [ ] Confidence scores are floats (0-1 range)
- [ ] Target filenames are correct (GC01PS03T00XX)

**Check counts:**
```cmd
REM Total detections
find /C "" < outputs\GC_PS03_16-Oct-2025_AIGR-S47377.txt

REM Per class
findstr "Solar Panel" outputs\GC_PS03_16-Oct-2025_AIGR-S47377.txt | find /C ""
findstr "Brick Kiln" outputs\GC_PS03_16-Oct-2025_AIGR-S47377.txt | find /C ""
findstr "Pond" outputs\GC_PS03_16-Oct-2025_AIGR-S47377.txt | find /C ""
findstr "Playground" outputs\GC_PS03_16-Oct-2025_AIGR-S47377.txt | find /C ""
findstr "Sheds" outputs\GC_PS03_16-Oct-2025_AIGR-S47377.txt | find /C ""
```

---

## 🎯 Optimized Configuration (Already Set)

Your `configs/default.yaml` is pre-configured for maximum accuracy:

- ✅ **Tile size**: 512 pixels (better context)
- ✅ **Stride**: 256 pixels (50% overlap)
- ✅ **Top-K**: 1000 candidates (better recall)
- ✅ **NMS threshold**: 0.3 (balanced merging)
- ✅ **Score threshold**: 0.4 (quality detections)
- ✅ **Team name**: AIGR-S47377 (embedded)

---

## ⏱️ Timeline

| Step | Time (CPU) | Time (GPU) |
|------|-----------|-----------|
| Install (one-time) | 5 min | 5 min |
| Extract chips | 2 min | 2 min |
| Build index | 5-10 min | 2 min |
| Search 8 classes | 10-15 min | 5-8 min |
| Combine results | 10 sec | 10 sec |
| **TOTAL** | **25-35 min** | **15-20 min** |

---

## 🆘 Troubleshooting

**"python not recognized"**
→ Use full path: `C:\Users\meeth\AppData\Local\Programs\Python\Python39\python.exe`

**"No module named X"**
→ Run: `venv\Scripts\activate` then `pip install -r requirements.txt`

**"CUDA out of memory"**
→ Use `--device cpu` instead of `--device cuda`

**"No chips found"**
→ Check: `dir "chips\Solar Panel"` - should show .tif files

**Empty output file**
→ Check index exists: `dir cache\indexes`

---

## 🏆 Final Submission

**Your submission file:**
```
outputs\GC_PS03_16-Oct-2025_AIGR-S47377.txt
```

**Contains:**
- All 8 classes in ONE file
- PS-03 standard format
- Team name: AIGR-S47377
- Ready to submit to hackathon portal

---

## 🚀 ONE-LINE COMMAND (Easiest)

```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03 && FINAL_RUN_AIGR-S47377.bat
```

**Done! Wait 25-35 minutes and your submission file will be ready!**

🎉 **Good luck, Team AIGR-S47377!**
