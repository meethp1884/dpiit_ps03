# Local Machine Setup Guide - PS-03

## 🖥️ Running on Your Local Machine (Windows)

### Prerequisites

- Windows 10/11
- Python 3.8 or higher
- 8GB RAM minimum (16GB recommended)
- CUDA GPU (optional, for faster training)

---

## 📋 Step-by-Step Installation

### Step 1: Install Python

1. Download Python from https://www.python.org/downloads/
2. During installation, **CHECK "Add Python to PATH"**
3. Verify installation:
   ```cmd
   python --version
   ```
   Should show: `Python 3.x.x`

### Step 2: Navigate to Project

```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03
```

### Step 3: Create Virtual Environment

```cmd
python -m venv venv
```

### Step 4: Activate Virtual Environment

```cmd
venv\Scripts\activate
```

You should see `(venv)` before your command prompt.

### Step 5: Install Dependencies

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

**This will take 5-10 minutes.** Wait for all packages to install.

### Step 6: Verify Installation

```cmd
python -c "import torch; import rasterio; import faiss; print('All packages installed successfully!')"
```

If you see "All packages installed successfully!", you're ready!

---

## 🎯 Using Class Names with Spaces (e.g., "Solar Panel")

### The Solution: Use Quotes!

Your class name is `Solar Panel` (with space), not `Solar_Panel`.

**CORRECT Ways to Handle Spaces:**

### Method 1: Use Quotes in Commands (RECOMMENDED)

```cmd
REM Create chip folder with spaces
mkdir "chips\Solar Panel"

REM Run search with class name in quotes
python scripts\run_search.py ^
  --chips "chips\Solar Panel\chip_01.tif" "chips\Solar Panel\chip_02.tif" ^
  --index cache\indexes ^
  --name "Solar Panel" ^
  --out outputs\results.txt
```

### Method 2: Escape Spaces (Alternative)

```cmd
REM Using backslash before space
python scripts\run_search.py ^
  --chips chips\Solar^ Panel\chip_01.tif ^
  --name Solar^ Panel ^
  --out outputs\results.txt
```

### Method 3: Use PowerShell (Modern Windows)

```powershell
python scripts\run_search.py `
  --chips "chips\Solar Panel\chip_01.tif" `
  --name "Solar Panel" `
  --out outputs\results.txt
```

---

## 🚀 Complete Workflow on Local Machine

### Step 1: Place Your Datasets

Follow `DATASET_SETUP.md` to place your 3 datasets:
- Training set → `data/training_set/`
- Testing set → `data/testing_set/`
- Sample set → `data/sample_set/`

### Step 2: Create Query Chips

**Option A - From Sample JSONs:**
```cmd
REM Extract chip from JSON annotation
python scripts\make_chip_from_json.py ^
  --json data\sample_set\GC01PS03S0001.json ^
  --out "chips\Solar Panel\chip_01.tif"
```

**Option B - Manual Placement:**
```cmd
REM Create class folder
mkdir "chips\Solar Panel"

REM Copy your pre-made chips
copy "C:\path\to\your\chip.tif" "chips\Solar Panel\chip_01.tif"
```

### Step 3: Build FAISS Index

```cmd
REM Activate virtual environment
venv\Scripts\activate

REM Build index from testing set
python scripts\build_index.py ^
  --targets data\testing_set ^
  --out cache\indexes ^
  --config configs\default.yaml ^
  --device cpu
```

**On GPU (if you have CUDA):**
```cmd
python scripts\build_index.py ^
  --targets data\testing_set ^
  --out cache\indexes ^
  --device cuda
```

**Time:** 5-15 minutes depending on CPU/GPU.

### Step 4: Run Visual Search

```cmd
REM Search with your chips (use quotes for spaces!)
python scripts\run_search.py ^
  --chips "chips\Solar Panel\chip_01.tif" "chips\Solar Panel\chip_02.tif" ^
  --index cache\indexes ^
  --name "Solar Panel" ^
  --out outputs\runs\GC_PS03_16-Oct-2025_TeamName\results.txt ^
  --team TeamName
```

**Output file:** `outputs\runs\GC_PS03_16-Oct-2025_TeamName\results.txt`

**Format:**
```
x_min y_min x_max y_max Solar Panel GC01PS03T0001 0.923456
x_min y_min x_max y_max Solar Panel GC01PS03T0002 0.887234
```

Notice: Class name is `Solar Panel` (with space) in output!

### Step 5: View Results

```cmd
REM Open results file
notepad outputs\runs\GC_PS03_16-Oct-2025_TeamName\results.txt

REM Or view summary
type outputs\runs\GC_PS03_16-Oct-2025_TeamName\results_summary.txt
```

---

## 🌐 Using Web UI (Local)

### Start Backend API

```cmd
REM Terminal 1 - Start API
venv\Scripts\activate
python api\main.py
```

Keep this terminal open. API runs at `http://localhost:8000`

### Start Frontend UI

```cmd
REM Terminal 2 - Start React UI (new terminal)
cd ui
npm install
npm start
```

Browser opens at `http://localhost:3000`

### Using the UI

1. **Upload Tab:**
   - Click "Upload TIFF chips" → Select your chip files
   - Enter index path: `cache\indexes`
   - Click "Load Index"

2. **Search Tab:**
   - Enter class name: `Solar Panel` (with space!)
   - Click "Run Search"

3. **Results Tab:**
   - View detections
   - Click "Export Submission" to download results file

---

## 🎓 Training Embedder (Optional)

To improve accuracy, train on your training set:

```cmd
REM Train for 50 epochs on CPU
python scripts\train_embedder.py ^
  --data data\training_set ^
  --config configs\default.yaml ^
  --epochs 50 ^
  --device cpu

REM On GPU (much faster)
python scripts\train_embedder.py ^
  --data data\training_set ^
  --epochs 50 ^
  --device cuda
```

**Time:**
- CPU: 2-4 hours
- GPU: 20-40 minutes

Trained model saved to: `models\checkpoints\best.pth`

### Use Trained Model

```cmd
REM Search with trained embedder
python scripts\run_search.py ^
  --chips "chips\Solar Panel\chip_01.tif" ^
  --index cache\indexes ^
  --name "Solar Panel" ^
  --checkpoint models\checkpoints\best.pth ^
  --out outputs\results.txt
```

---

## 📊 Evaluation (If You Have Ground Truth)

```cmd
python scripts\eval_local_map.py ^
  --submission outputs\results.txt ^
  --ground-truth data\sample_set ^
  --iou-thresholds 0.5 0.75 0.9
```

---

## 🔧 Common Issues on Windows

### Issue 1: "python not recognized"
**Solution:**
```cmd
REM Use full path
C:\Users\meeth\AppData\Local\Programs\Python\Python39\python.exe --version

REM Or reinstall Python with "Add to PATH" checked
```

### Issue 2: "No module named 'xxx'"
**Solution:**
```cmd
REM Ensure virtual environment is activated
venv\Scripts\activate

REM Reinstall
pip install -r requirements.txt
```

### Issue 3: File path errors with spaces
**Solution:**
```cmd
REM Always use quotes around paths with spaces
--chips "chips\Solar Panel\chip_01.tif"
--name "Solar Panel"
```

### Issue 4: "CUDA out of memory"
**Solution:**
```cmd
REM Use CPU instead
--device cpu

REM Or reduce batch size in configs\default.yaml
```

### Issue 5: Slow on CPU
**Solution:**
- Reduce tile size in `configs\default.yaml` (384 → 256)
- Reduce top_k_per_chip (500 → 100)
- Use fewer query chips (1-2 instead of 5)

---

## 📁 Important Windows Paths

```
Project Root:    c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03\
Virtual Env:     c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03\venv\
Data:            c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03\data\
Chips:           c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03\chips\
Outputs:         c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03\outputs\
Config:          c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03\configs\default.yaml
```

---

## ✅ Quick Test

Run this to verify everything works:

```cmd
REM Activate environment
venv\Scripts\activate

REM Test imports
python -c "from engine import read_tiff, get_embedder; print('✓ Engine OK')"

REM Test FAISS
python -c "import faiss; print('✓ FAISS OK')"

REM Test config
python -c "import yaml; c=yaml.safe_load(open('configs/default.yaml')); print('✓ Config OK')"
```

All should print "✓ OK"!

---

## 🎯 Summary Commands

**Complete workflow in 4 commands:**

```cmd
REM 1. Activate
venv\Scripts\activate

REM 2. Build index
python scripts\build_index.py --targets data\testing_set --out cache\indexes

REM 3. Search (use quotes for spaces!)
python scripts\run_search.py --chips "chips\Solar Panel\chip_01.tif" --index cache\indexes --name "Solar Panel" --out outputs\results.txt

REM 4. View results
notepad outputs\results.txt
```

Done! 🎉
