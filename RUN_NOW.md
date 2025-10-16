# ▶️ RUN NOW - Complete Workflow

**You've fixed the folder structure. Now get results for ALL classes!**

---

## 🎯 Two Options: Automated or Manual

### ⚡ OPTION 1: AUTOMATED (RECOMMENDED)

**Just double-click this file or run:**

```cmd
RUN_COMPLETE_WORKFLOW.bat
```

**This will:**
1. ✅ Extract chips from all 8 classes
2. ✅ Build FAISS index
3. ✅ Search for all classes automatically
4. ✅ Combine results into submission file
5. ✅ Show summary statistics

**Time: ~30 minutes**

**Then view results:**
```cmd
notepad outputs\GC_PS03_16-Oct-2025_YourTeam.txt
```

---

### 🔧 OPTION 2: MANUAL (Step-by-Step)

**If you want to run each step manually:**

#### Step 1: Setup (One-time, 5 minutes)

```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03

REM Create virtual environment (if not done)
python -m venv venv

REM Activate it
venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt
```

#### Step 2: Extract Chips (2 minutes)

```cmd
python scripts\batch_extract_chips.py ^
  --sample-dir data\sample_set ^
  --out-dir chips ^
  --max-chips 5 ^
  --padding 20
```

**This extracts chips from all 8 classes automatically!**

#### Step 3: Build Index (5-10 minutes)

```cmd
python scripts\build_index.py ^
  --targets data\testing_set ^
  --out cache\indexes ^
  --device cpu ^
  --tile-size 512 ^
  --stride 256
```

**On GPU (much faster):**
```cmd
python scripts\build_index.py ^
  --targets data\testing_set ^
  --out cache\indexes ^
  --device cuda ^
  --tile-size 512 ^
  --stride 256
```

#### Step 4: Search for ALL Classes (10-15 minutes)

**Class 1: Solar Panel**
```cmd
python scripts\run_search.py ^
  --chips "chips\Solar Panel\chip_01.tif" "chips\Solar Panel\chip_02.tif" "chips\Solar Panel\chip_03.tif" ^
  --index cache\indexes ^
  --name "Solar Panel" ^
  --out outputs\solar_panel.txt ^
  --team YourTeam ^
  --top-k 1000 ^
  --nms-threshold 0.3
```

**Class 2: Brick Kiln**
```cmd
python scripts\run_search.py ^
  --chips "chips\Brick Kiln\chip_01.tif" "chips\Brick Kiln\chip_02.tif" ^
  --index cache\indexes ^
  --name "Brick Kiln" ^
  --out outputs\brick_kiln.txt ^
  --team YourTeam ^
  --top-k 1000 ^
  --nms-threshold 0.3
```

**Class 3: Pond-1 & Pond-2**
```cmd
python scripts\run_search.py ^
  --chips "chips\Pond-1 & Pond-2\chip_01.tif" ^
  --index cache\indexes ^
  --name "Pond-1 & Pond-2" ^
  --out outputs\pond_1_2.txt ^
  --team YourTeam ^
  --top-k 1000 ^
  --nms-threshold 0.3
```

**Class 4: Pond-1,Pond-2 & Playground**
```cmd
python scripts\run_search.py ^
  --chips "chips\Pond-1,Pond-2 & Playground\chip_01.tif" ^
  --index cache\indexes ^
  --name "Pond-1,Pond-2 & Playground" ^
  --out outputs\pond_playground.txt ^
  --team YourTeam ^
  --top-k 1000 ^
  --nms-threshold 0.3
```

**Class 5: Pond-2,STP & Sheds**
```cmd
python scripts\run_search.py ^
  --chips "chips\Pond-2,STP & Sheds\chip_01.tif" ^
  --index cache\indexes ^
  --name "Pond-2,STP & Sheds" ^
  --out outputs\pond_stp_sheds.txt ^
  --team YourTeam ^
  --top-k 1000 ^
  --nms-threshold 0.3
```

**Class 6: MetroShed,STP & Sheds**
```cmd
python scripts\run_search.py ^
  --chips "chips\MetroShed,STP & Sheds\chip_01.tif" ^
  --index cache\indexes ^
  --name "MetroShed,STP & Sheds" ^
  --out outputs\metro_stp_sheds.txt ^
  --team YourTeam ^
  --top-k 1000 ^
  --nms-threshold 0.3
```

**Class 7: Playground**
```cmd
python scripts\run_search.py ^
  --chips "chips\Playground\chip_01.tif" ^
  --index cache\indexes ^
  --name "Playground" ^
  --out outputs\playground.txt ^
  --team YourTeam ^
  --top-k 1000 ^
  --nms-threshold 0.3
```

**Class 8: Sheds**
```cmd
python scripts\run_search.py ^
  --chips "chips\Sheds\chip_01.tif" "chips\Sheds\chip_02.tif" ^
  --index cache\indexes ^
  --name "Sheds" ^
  --out outputs\sheds.txt ^
  --team YourTeam ^
  --top-k 1000 ^
  --nms-threshold 0.3
```

#### Step 5: Combine All Results (10 seconds)

```cmd
copy /B ^
  outputs\solar_panel.txt + ^
  outputs\brick_kiln.txt + ^
  outputs\pond_1_2.txt + ^
  outputs\pond_playground.txt + ^
  outputs\pond_stp_sheds.txt + ^
  outputs\metro_stp_sheds.txt + ^
  outputs\playground.txt + ^
  outputs\sheds.txt ^
  outputs\GC_PS03_16-Oct-2025_YourTeam.txt
```

#### Step 6: View Results

```cmd
notepad outputs\GC_PS03_16-Oct-2025_YourTeam.txt
```

---

## 🎯 For Maximum Accuracy

### Use These Settings:

**When building index:**
- `--tile-size 512` (larger tiles capture more context)
- `--stride 256` (50% overlap for better coverage)
- `--device cuda` (if you have GPU)

**When searching:**
- `--top-k 1000` (retrieve more candidates)
- `--nms-threshold 0.3` (balanced merging)
- Use 3-5 chips per class (more examples)

**See `ACCURACY_TIPS.md` for detailed strategies!**

---

## 📊 Expected Output Format

Your final submission file will look like:

```
159 797 331 853 Solar Panel GC01PS03T0013 0.923456
1579 827 1936 873 Solar Panel GC01PS03T0022 0.887234
256 384 512 640 Brick Kiln GC01PS03T0027 0.856789
100 200 300 400 Pond-1 & Pond-2 GC01PS03T0029 0.834567
...
```

**Format:** `x_min y_min x_max y_max ClassName ImageName Score`

**Notice:** Class names appear EXACTLY as you specified (with spaces, ampersands, etc.)!

---

## ✅ Verification

**After running, check:**

```cmd
REM How many chips extracted?
dir chips /S /B | find /C ".tif"

REM Index built?
dir cache\indexes

REM Results generated?
dir outputs

REM Count detections per class
find /C "Solar Panel" outputs\GC_PS03_16-Oct-2025_YourTeam.txt
find /C "Brick Kiln" outputs\GC_PS03_16-Oct-2025_YourTeam.txt
find /C "Pond" outputs\GC_PS03_16-Oct-2025_YourTeam.txt
find /C "Playground" outputs\GC_PS03_16-Oct-2025_YourTeam.txt
find /C "Sheds" outputs\GC_PS03_16-Oct-2025_YourTeam.txt
```

---

## 🚀 Quick Start (Copy-Paste This Entire Block)

```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03
RUN_COMPLETE_WORKFLOW.bat
```

**That's it! Everything runs automatically!**

---

## ⏱️ Timeline

- **Setup (one-time):** 5 minutes
- **Extract chips:** 2 minutes
- **Build index:** 5-10 minutes (CPU) / 2 min (GPU)
- **Search all classes:** 10-15 minutes
- **Combine results:** 10 seconds

**Total: ~25-35 minutes to complete submission!**

---

## 🆘 Troubleshooting

**"python not recognized"**
→ Use full path or add Python to PATH

**"No module named X"**
→ Run: `venv\Scripts\activate` then `pip install -r requirements.txt`

**"File not found"**
→ Check quotes around paths with spaces: `"chips\Solar Panel\chip_01.tif"`

**Slow performance**
→ Use `--device cuda` if you have GPU

**Too few/many detections**
→ Adjust `--top-k` and `--nms-threshold` (see `ACCURACY_TIPS.md`)

---

## 🎯 Summary

**Fastest way:** Run `RUN_COMPLETE_WORKFLOW.bat`

**Manual way:** Follow Step 1-6 above

**For max accuracy:** Read `ACCURACY_TIPS.md`

**Result:** Complete submission file for all 8 classes ready for PS-03!

🎉 **Good luck!**
