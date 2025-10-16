# 🚨 KAGGLE FIX - Updated Code (No '&' Characters)

## STEP 1: Fix Folder Names (Run This First!)

**Double-click:** `fix_folder_names.bat`

OR run these commands:

```cmd
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03\data\sample_set
ren "MetroShed,STP & Sheds" "MetroShed,STP and Sheds"
ren "Pond-1 & Pond-2" "Pond-1 and Pond-2"
ren "Pond-1,Pond-2 & Playground" "Pond-1,Pond-2 and Playground"
ren "Pond-2,STP & Sheds" "Pond-2,STP and Sheds"
```

---

## STEP 2: Upload to Kaggle

Now upload your **renamed** folders to Kaggle as 3 datasets.

---

## STEP 3: Updated Kaggle Notebook Code

**Copy-paste this UPDATED code (with 'and' instead of '&'):**

```python
# ========================================================================
# PS-03 VISUAL SEARCH - Team AIGR-S47377 (FIXED FOR KAGGLE)
# GitHub: https://github.com/meethp1884/dpiit_ps03
# ========================================================================

# STEP 1: Install dependencies
print("Installing packages...")
!pip install -q rasterio faiss-gpu opencv-python-headless scikit-image pyyaml omegaconf

# STEP 2: Clone GitHub repo
print("\nCloning repository...")
!git clone https://github.com/meethp1884/dpiit_ps03.git
%cd dpiit_ps03

# STEP 3: Link datasets
print("\nLinking datasets...")
!mkdir -p data
!ln -s /kaggle/input/ps03-sample-set data/sample_set
!ln -s /kaggle/input/ps03-training-set data/training_set
!ln -s /kaggle/input/ps03-testing-set data/testing_set

# Verify
!echo "Sample:"; ls data/sample_set/ | head -5
!echo "Training:"; ls data/training_set/*.tif 2>/dev/null | wc -l
!echo "Testing:"; ls data/testing_set/*.tif 2>/dev/null | wc -l

# STEP 4: Extract chips
print("\n" + "="*70)
print("EXTRACTING CHIPS...")
print("="*70)
!python scripts/batch_extract_chips.py \
    --sample-dir data/sample_set \
    --out-dir chips \
    --max-chips 5

# STEP 5: Build index
print("\n" + "="*70)
print("BUILDING FAISS INDEX...")
print("="*70)
!python scripts/build_index.py \
    --targets data/testing_set \
    --out cache/indexes \
    --device cuda \
    --config configs/default.yaml

# STEP 6: Search all classes (UPDATED - NO '&' CHARACTER!)
print("\n" + "="*70)
print("SEARCHING FOR ALL 8 CLASSES...")
print("="*70)

import glob
import os
from datetime import datetime

# UPDATED CLASS NAMES (replaced & with 'and')
classes = [
    "Solar Panel",
    "Brick Kiln",
    "Pond-1 and Pond-2",                    # CHANGED
    "Pond-1,Pond-2 and Playground",         # CHANGED
    "Pond-2,STP and Sheds",                 # CHANGED
    "MetroShed,STP and Sheds",              # CHANGED
    "Playground",
    "Sheds"
]

# Original class names for submission (with &)
original_names = {
    "Pond-1 and Pond-2": "Pond-1 & Pond-2",
    "Pond-1,Pond-2 and Playground": "Pond-1,Pond-2 & Playground",
    "Pond-2,STP and Sheds": "Pond-2,STP & Sheds",
    "MetroShed,STP and Sheds": "MetroShed,STP & Sheds"
}

os.makedirs("outputs", exist_ok=True)

for i, class_name in enumerate(classes, 1):
    print(f"\n[{i}/8] Searching for: {class_name}...")
    
    safe_name = class_name.replace(" ", "_").replace(",", "").replace("&", "and")
    chip_dir = f"chips/{class_name}"
    chips = glob.glob(f"{chip_dir}/*.tif")[:5]
    
    if not chips:
        print(f"  WARNING: No chips for {class_name}")
        continue
    
    print(f"  Using {len(chips)} chips")
    
    # Use ORIGINAL name in submission (with &)
    submission_name = original_names.get(class_name, class_name)
    
    chip_args = " ".join([f'"{c}"' for c in chips])
    output_file = f"outputs/temp_{safe_name}.txt"
    
    cmd = f'''python scripts/run_search.py \
        --chips {chip_args} \
        --index cache/indexes \
        --name "{submission_name}" \
        --out "{output_file}" \
        --team AIGR-S47377 \
        --config configs/default.yaml \
        --device cuda'''
    
    result = os.system(cmd)
    print(f"  {'✓' if result == 0 else '✗'} {class_name}")

# STEP 7: Combine results
print("\n" + "="*70)
print("COMBINING RESULTS...")
print("="*70)

date_str = datetime.now().strftime("%d-%b-%Y")
submission_file = f"outputs/GC_PS03_{date_str}_AIGR-S47377.txt"

temp_files = sorted(glob.glob("outputs/temp_*.txt"))
with open(submission_file, 'w') as outfile:
    for temp_file in temp_files:
        with open(temp_file, 'r') as infile:
            outfile.write(infile.read())

# STEP 8: Show summary
print("\n" + "="*70)
print("SUBMISSION READY!")
print("="*70)

with open(submission_file, 'r') as f:
    lines = f.readlines()

print(f"\nTotal Detections: {len(lines)}")
print(f"\nDetections by Class:")

# Show with ORIGINAL names (with &)
for class_name in classes:
    display_name = original_names.get(class_name, class_name)
    count = sum(1 for line in lines if display_name in line)
    print(f"  {display_name:35s}: {count:4d}")

print(f"\nSubmission File: {submission_file}")

# Preview
print(f"\nFirst 10 detections:")
print("-" * 100)
for i, line in enumerate(lines[:10], 1):
    print(f"{i:2d}. {line.strip()}")

# STEP 9: Download
from shutil import copy
copy(submission_file, '/kaggle/working/')

print(f"\n{'='*70}")
print(f"✓ Ready to download: {os.path.basename(submission_file)}")
print(f"✓ Click 'Output' tab to download")
print(f"{'='*70}")
print("ALL DONE! Team AIGR-S47377 🏆")
print("="*70)
```

---

## 🎯 KEY CHANGES

**1. Folder Names (on disk):**
- `Pond-1 & Pond-2` → `Pond-1 and Pond-2`
- `Pond-1,Pond-2 & Playground` → `Pond-1,Pond-2 and Playground`
- `Pond-2,STP & Sheds` → `Pond-2,STP and Sheds`
- `MetroShed,STP & Sheds` → `MetroShed,STP and Sheds`

**2. Submission File (keeps original):**
- Output still uses `&` in class names (as required by hackathon)

**3. Code Mapping:**
- Searches in renamed folders
- Outputs with original `&` names

---

## ✅ WORKFLOW

1. **Run:** `fix_folder_names.bat` (30 seconds)
2. **Upload to Kaggle:** Renamed folders (5 min)
3. **Run:** Updated notebook code above (15 min)
4. **Download:** Submission file (30 seconds)
5. **Submit!** ✅

---

## 🚀 QUICK COMMANDS

```cmd
REM Fix folder names
cd c:\Users\meeth\OneDrive\Desktop\DPIIT\new_ps03
fix_folder_names.bat

REM Now upload to Kaggle and use code above!
```

---

**Total Time: ~20 minutes** ✅
