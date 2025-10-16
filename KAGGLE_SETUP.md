# Kaggle Setup Guide - PS-03

## 🚀 Running PS-03 on Kaggle

Kaggle provides **free GPU access** which makes training and search much faster!

---

## 📋 Step-by-Step Kaggle Deployment

### Step 1: Prepare Your Project for Kaggle

**On your local machine:**

1. **Create a simplified requirements file for Kaggle:**

Create `requirements_kaggle.txt`:
```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03
notepad requirements_kaggle.txt
```

Paste this (minimal set):
```txt
torch>=2.0.0
torchvision>=0.15.0
numpy>=1.24.0
opencv-python>=4.8.0
rasterio>=1.3.0
pillow>=10.0.0
scikit-image>=0.21.0
scipy>=1.11.0
faiss-cpu>=1.7.4
pyyaml>=6.0
matplotlib>=3.7.0
tqdm>=4.66.0
```

2. **Test locally first** (make sure everything works)

---

### Step 2: Upload to Kaggle

#### Method A: Upload as Kaggle Dataset

1. **Zip your project:**

**Windows:**
```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT
powershell Compress-Archive -Path new_ps03\* -DestinationPath ps03_project.zip
```

**Linux/Mac:**
```bash
cd ~/Desktop/DPIIT
zip -r ps03_project.zip new_ps03/
```

2. **Go to Kaggle:**
   - Visit: https://www.kaggle.com/datasets
   - Click "New Dataset"
   - Upload `ps03_project.zip`
   - Title: "PS03 Visual Search Code"
   - Click "Create"

3. **Upload your datasets separately:**
   - Create dataset: "PS03 Training Set" → upload `training_set/*.tif`
   - Create dataset: "PS03 Testing Set" → upload `testing_set/*.tif`
   - Create dataset: "PS03 Sample Set" → upload `sample_set/*.tif` + `*.json`

#### Method B: Clone from GitHub (see GITHUB_GUIDE.md first)

If you've pushed to GitHub:
```python
# In Kaggle notebook
!git clone https://github.com/yourusername/ps03-visual-search.git
```

---

### Step 3: Create Kaggle Notebook

1. Go to https://www.kaggle.com/code
2. Click "New Notebook"
3. Settings:
   - **Accelerator:** GPU T4 x2 (free)
   - **Internet:** ON
   - **Language:** Python

---

### Step 4: Kaggle Notebook Setup

**Cell 1: Install Dependencies**
```python
!pip install -q rasterio faiss-cpu pyyaml tqdm

# Verify
import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
```

**Cell 2: Add Datasets**
```python
# Add your datasets in Kaggle:
# Right panel → "Add Data" → Search your uploaded datasets → Add

# Kaggle mounts datasets at /kaggle/input/
import os

# Verify datasets
print("Available datasets:")
for root, dirs, files in os.walk('/kaggle/input'):
    level = root.replace('/kaggle/input', '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
```

**Cell 3: Extract Code**
```python
# If you uploaded code as dataset
import shutil
import os

# Copy code from dataset to working directory
code_path = '/kaggle/input/ps03-visual-search-code'
work_path = '/kaggle/working/ps03'

# Create working directory
os.makedirs(work_path, exist_ok=True)

# Copy code files
!cp -r {code_path}/engine {work_path}/
!cp -r {code_path}/scripts {work_path}/
!cp -r {code_path}/configs {work_path}/

# Verify
!ls -la {work_path}
```

**Cell 4: Link Datasets**
```python
import os
import sys

# Add to Python path
sys.path.insert(0, '/kaggle/working/ps03')

# Create data directory structure
os.makedirs('/kaggle/working/ps03/data/training_set', exist_ok=True)
os.makedirs('/kaggle/working/ps03/data/testing_set', exist_ok=True)
os.makedirs('/kaggle/working/ps03/data/sample_set', exist_ok=True)
os.makedirs('/kaggle/working/ps03/chips/Solar Panel', exist_ok=True)
os.makedirs('/kaggle/working/ps03/cache/indexes', exist_ok=True)
os.makedirs('/kaggle/working/ps03/outputs', exist_ok=True)

# Create symbolic links to datasets (faster than copying)
!ln -s /kaggle/input/ps03-training-set/*.tif /kaggle/working/ps03/data/training_set/
!ln -s /kaggle/input/ps03-testing-set/*.tif /kaggle/working/ps03/data/testing_set/
!ln -s /kaggle/input/ps03-sample-set/* /kaggle/working/ps03/data/sample_set/

print("✓ Data linked successfully")
```

**Cell 5: Create/Upload Query Chips**
```python
# Option A: Extract from sample JSON
!cd /kaggle/working/ps03 && python scripts/make_chip_from_json.py \
  --json data/sample_set/GC01PS03S0001.json \
  --out "chips/Solar Panel/chip_01.tif"

# Option B: Upload chips manually via Kaggle UI as a dataset
# Then link them:
# !ln -s /kaggle/input/my-query-chips/*.tif /kaggle/working/ps03/chips/Solar\ Panel/

print("✓ Chips ready")
```

**Cell 6: Build FAISS Index**
```python
!cd /kaggle/working/ps03 && python scripts/build_index.py \
  --targets data/testing_set \
  --out cache/indexes \
  --config configs/default.yaml \
  --device cuda

print("✓ Index built")
```

**Cell 7: Run Search**
```python
!cd /kaggle/working/ps03 && python scripts/run_search.py \
  --chips "chips/Solar Panel/chip_01.tif" "chips/Solar Panel/chip_02.tif" \
  --index cache/indexes \
  --name "Solar Panel" \
  --out outputs/results.txt \
  --device cuda

print("✓ Search complete")
```

**Cell 8: View Results**
```python
import pandas as pd

# Read results
results = []
with open('/kaggle/working/ps03/outputs/results.txt', 'r') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) >= 7:
            results.append({
                'x_min': int(parts[0]),
                'y_min': int(parts[1]),
                'x_max': int(parts[2]),
                'y_max': int(parts[3]),
                'class': parts[4] + (' ' + parts[5] if len(parts) > 7 else ''),
                'image': parts[-2],
                'score': float(parts[-1])
            })

df = pd.DataFrame(results)
print(f"Total detections: {len(df)}")
print(f"Unique images: {df['image'].nunique()}")
print(f"\nTop 10 detections:")
print(df.head(10))

# Show score distribution
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 4))
plt.hist(df['score'], bins=50)
plt.xlabel('Confidence Score')
plt.ylabel('Count')
plt.title('Detection Score Distribution')
plt.show()
```

**Cell 9: Download Results**
```python
# Results are saved to /kaggle/working/ps03/outputs/results.txt
# You can download from Kaggle's output panel
print("Results saved to: /kaggle/working/ps03/outputs/results.txt")
print("Download from: Output tab → results.txt → Download")
```

---

### Step 5: Training on Kaggle (Optional)

**Cell: Train Embedder**
```python
!cd /kaggle/working/ps03 && python scripts/train_embedder.py \
  --data data/training_set \
  --config configs/default.yaml \
  --epochs 50 \
  --device cuda \
  --checkpoint-dir /kaggle/working/models/checkpoints

print("✓ Training complete")
print("Best model: /kaggle/working/models/checkpoints/best.pth")
```

Then use trained model:
```python
!cd /kaggle/working/ps03 && python scripts/run_search.py \
  --chips "chips/Solar Panel/chip_01.tif" \
  --index cache/indexes \
  --name "Solar Panel" \
  --checkpoint /kaggle/working/models/checkpoints/best.pth \
  --out outputs/results_trained.txt \
  --device cuda
```

---

## 📦 Complete Kaggle Notebook Template

**Copy this entire notebook:**

```python
# ==============================================================================
# PS-03 Visual Search on Kaggle
# ==============================================================================

# ---- CELL 1: Setup ----
!pip install -q rasterio faiss-cpu pyyaml tqdm
import torch
print(f"CUDA: {torch.cuda.is_available()}")

# ---- CELL 2: Prepare Environment ----
import os, sys, shutil

# Extract code (assuming uploaded as dataset)
!cp -r /kaggle/input/ps03-code/* /kaggle/working/ps03/
sys.path.insert(0, '/kaggle/working/ps03')

# Create directories
for d in ['data/training_set', 'data/testing_set', 'data/sample_set', 
          'chips/Solar Panel', 'cache/indexes', 'outputs', 'models/checkpoints']:
    os.makedirs(f'/kaggle/working/ps03/{d}', exist_ok=True)

# Link datasets
!ln -s /kaggle/input/ps03-training/*.tif /kaggle/working/ps03/data/training_set/
!ln -s /kaggle/input/ps03-testing/*.tif /kaggle/working/ps03/data/testing_set/
!ln -s /kaggle/input/ps03-samples/* /kaggle/working/ps03/data/sample_set/

# ---- CELL 3: Create Chips ----
!cd /kaggle/working/ps03 && python scripts/make_chip_from_json.py \
  --json data/sample_set/GC01PS03S0001.json \
  --out "chips/Solar Panel/chip_01.tif"

# ---- CELL 4: Build Index ----
!cd /kaggle/working/ps03 && python scripts/build_index.py \
  --targets data/testing_set --out cache/indexes --device cuda

# ---- CELL 5: Run Search ----
!cd /kaggle/working/ps03 && python scripts/run_search.py \
  --chips "chips/Solar Panel/chip_01.tif" \
  --index cache/indexes --name "Solar Panel" \
  --out outputs/results.txt --device cuda

# ---- CELL 6: View Results ----
with open('/kaggle/working/ps03/outputs/results.txt') as f:
    lines = f.readlines()
    print(f"Total detections: {len(lines)}")
    print("\nFirst 10 detections:")
    for line in lines[:10]:
        print(line.strip())
```

---

## 🎯 Handling "Solar Panel" Class Name on Kaggle

**On Kaggle, spaces in paths work fine:**

```python
# No problem with spaces!
os.makedirs('chips/Solar Panel', exist_ok=True)

!python scripts/run_search.py \
  --chips "chips/Solar Panel/chip_01.tif" \
  --name "Solar Panel" \
  --out outputs/results.txt
```

Output will have `Solar Panel` (with space) in the class column!

---

## ⚡ Kaggle Tips

1. **GPU is FREE**: Always enable GPU (Settings → Accelerator → GPU T4 x2)
2. **30 hours/week**: You get 30 GPU hours per week (resets weekly)
3. **Save outputs**: Download results before notebook times out
4. **Commit notebook**: Save versions as you go
5. **Internet ON**: Required for pip installs

---

## 📊 Expected Performance on Kaggle GPU

- **Build Index (40 images):** 2-5 minutes
- **Search (5 chips):** 30 seconds - 1 minute
- **Training (50 epochs):** 20-40 minutes

Much faster than CPU!

---

## 🔧 Common Kaggle Issues

### Issue: "No such file or directory"
**Solution:** Check dataset paths
```python
# List all available data
!ls -R /kaggle/input/
```

### Issue: "Module not found"
**Solution:** Install in notebook
```python
!pip install rasterio faiss-cpu
```

### Issue: "CUDA out of memory"
**Solution:** Reduce batch size
```python
# Edit config before running
import yaml
with open('/kaggle/working/ps03/configs/default.yaml', 'r') as f:
    config = yaml.safe_load(f)
config['training']['batch_size'] = 16  # Reduce from 32
with open('/kaggle/working/ps03/configs/default.yaml', 'w') as f:
    yaml.dump(config, f)
```

---

## 📥 Downloading Results from Kaggle

1. Run notebook until search completes
2. Right panel → "Output" tab
3. Find `results.txt`
4. Click "..." → Download

Or use Kaggle API:
```bash
kaggle kernels output yourusername/notebook-name -p outputs/
```

---

## ✅ Verification

Run this in a cell to verify everything:
```python
import os
import sys

checks = {
    'Code': os.path.exists('/kaggle/working/ps03/engine'),
    'Training Data': len(os.listdir('/kaggle/working/ps03/data/training_set')) > 0,
    'Testing Data': len(os.listdir('/kaggle/working/ps03/data/testing_set')) > 0,
    'Chips': os.path.exists('/kaggle/working/ps03/chips/Solar Panel'),
    'CUDA': torch.cuda.is_available()
}

for name, status in checks.items():
    print(f"{'✓' if status else '✗'} {name}: {status}")
```

All should show ✓!

---

## 🎓 Advanced: Kaggle Kernel with Direct Dataset Upload

For easier setup, create a public GitHub repo (see GITHUB_GUIDE.md), then:

```python
# In Kaggle notebook
!git clone https://github.com/yourusername/ps03-visual-search.git
%cd ps03-visual-search
!pip install -r requirements_kaggle.txt
```

Much simpler!
