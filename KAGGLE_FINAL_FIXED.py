# ========================================================================
# PS-03 VISUAL SEARCH - Team AIGR-S47377 (FULLY FIXED)
# GitHub: https://github.com/meethp1884/dpiit_ps03
# ========================================================================

# STEP 1: Install packages (WITHOUT -q to see errors)
print("="*70)
print("INSTALLING PACKAGES...")
print("="*70)

import sys
import subprocess

packages = [
    'rasterio',
    'faiss-gpu', 
    'opencv-python-headless',
    'scikit-image',
    'pyyaml',
    'omegaconf'
]

for pkg in packages:
    print(f"Installing {pkg}...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])

print("\n✓ All packages installed!")

# Verify critical imports
print("\nVerifying imports...")
try:
    import rasterio
    import faiss
    import cv2
    import yaml
    print("✓ All imports successful!")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    print("Please restart notebook and try again")
    raise

# STEP 2: Clone repository
print("\n" + "="*70)
print("CLONING REPOSITORY...")
print("="*70)
import os
os.chdir('/kaggle/working')
!git clone https://github.com/meethp1884/dpiit_ps03.git
os.chdir('dpiit_ps03')
print("✓ Repository cloned")

# STEP 3: Setup data directories
print("\n" + "="*70)
print("LINKING DATASETS...")
print("="*70)
!mkdir -p data
!ln -s /kaggle/input/ps03-sample-set data/sample_set
!ln -s /kaggle/input/ps03-training-set data/training_set
!ln -s /kaggle/input/ps03-testing-set data/testing_set

# Verify data exists
print("\nVerifying datasets...")
!echo "Sample set:"; ls data/sample_set/ 2>/dev/null | head -5 || echo "ERROR: sample_set not found!"
!echo "\nTraining set:"; ls data/training_set/*.tif 2>/dev/null | wc -l || echo "ERROR: training_set not found!"
!echo "Testing set:"; ls data/testing_set/*.tif 2>/dev/null | wc -l || echo "ERROR: testing_set not found!"

# STEP 4: Extract chips
print("\n" + "="*70)
print("EXTRACTING QUERY CHIPS...")
print("="*70)
!python scripts/batch_extract_chips.py \
    --sample-dir data/sample_set \
    --out-dir chips \
    --max-chips 5

# Verify chips extracted
!echo "\nChips extracted:"; ls chips/

# STEP 5: Build FAISS index
print("\n" + "="*70)
print("BUILDING FAISS INDEX...")
print("="*70)
!python scripts/build_index.py \
    --targets data/testing_set \
    --out cache/indexes \
    --device cuda \
    --config configs/default.yaml

# STEP 6: Run search for all 8 classes
print("\n" + "="*70)
print("SEARCHING FOR ALL 8 CLASSES...")
print("="*70)

import glob
from datetime import datetime

# Class names with 'and' (for folder names)
classes_folders = [
    "Solar Panel",
    "Brick Kiln",
    "Pond-1 and Pond-2",
    "Pond-1,Pond-2 and Playground",
    "Pond-2,STP and Sheds",
    "MetroShed,STP and Sheds",
    "Playground",
    "Sheds"
]

# Original names with '&' for submission
original_names = {
    "Pond-1 and Pond-2": "Pond-1 & Pond-2",
    "Pond-1,Pond-2 and Playground": "Pond-1,Pond-2 & Playground",
    "Pond-2,STP and Sheds": "Pond-2,STP & Sheds",
    "MetroShed,STP and Sheds": "MetroShed,STP & Sheds"
}

os.makedirs("outputs", exist_ok=True)

for i, folder_name in enumerate(classes_folders, 1):
    print(f"\n[{i}/8] Searching: {folder_name}...")
    
    # Get original name for submission
    submission_name = original_names.get(folder_name, folder_name)
    
    # Find chips
    safe_name = folder_name.replace(" ", "_").replace(",", "")
    chip_dir = f"chips/{folder_name}"
    chips = glob.glob(f"{chip_dir}/*.tif")[:5]
    
    if not chips:
        print(f"  ✗ No chips found in {chip_dir}")
        continue
    
    print(f"  Found {len(chips)} chips")
    
    # Build command
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
    
    if result == 0:
        # Check if file has content
        if os.path.exists(output_file):
            with open(output_file) as f:
                count = len(f.readlines())
            print(f"  ✓ {submission_name}: {count} detections")
        else:
            print(f"  ✗ {submission_name}: Output file not created")
    else:
        print(f"  ✗ {submission_name}: Search failed (exit code {result})")

# STEP 7: Combine all results
print("\n" + "="*70)
print("COMBINING RESULTS...")
print("="*70)

date_str = datetime.now().strftime("%d-%b-%Y")
submission_file = f"outputs/GC_PS03_{date_str}_AIGR-S47377.txt"

# Combine all temp files
temp_files = sorted(glob.glob("outputs/temp_*.txt"))
print(f"Found {len(temp_files)} temp files to combine")

with open(submission_file, 'w') as outfile:
    for temp_file in temp_files:
        print(f"  Adding {temp_file}...")
        with open(temp_file, 'r') as infile:
            content = infile.read()
            outfile.write(content)

# STEP 8: Show summary
print("\n" + "="*70)
print("SUBMISSION READY!")
print("="*70)

with open(submission_file, 'r') as f:
    lines = f.readlines()

print(f"\nTotal Detections: {len(lines)}")

if len(lines) == 0:
    print("\n✗ WARNING: No detections found!")
    print("Possible issues:")
    print("  1. Check if chips were extracted correctly")
    print("  2. Check if index was built correctly")
    print("  3. Check if search ran without errors")
else:
    print(f"\nDetections by Class:")
    for folder_name in classes_folders:
        display_name = original_names.get(folder_name, folder_name)
        count = sum(1 for line in lines if display_name in line)
        print(f"  {display_name:35s}: {count:4d}")
    
    print(f"\nFirst 10 detections:")
    print("-" * 100)
    for i, line in enumerate(lines[:10], 1):
        print(f"{i:2d}. {line.strip()}")

# STEP 9: Copy to output for download
from shutil import copy
copy(submission_file, '/kaggle/working/')

print(f"\n{'='*70}")
print(f"✓ File: {os.path.basename(submission_file)}")
print(f"✓ Location: /kaggle/working/")
print(f"✓ Click 'Output' tab to download")
print(f"{'='*70}")
print("Team AIGR-S47377 - Submission Complete! 🏆")
print("="*70)
