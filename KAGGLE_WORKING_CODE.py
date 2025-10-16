# ========================================================================
# PS-03 - Team AIGR-S47377 (WORKING VERSION - All Import Issues Fixed)
# ========================================================================

# STEP 1: Install packages with proper error handling
print("="*70)
print("INSTALLING PACKAGES...")
print("="*70)

import sys
import subprocess

# Install each package individually
packages = [
    'rasterio',
    'faiss-gpu',
    'opencv-python-headless', 
    'scikit-image',
    'pyyaml',
    'omegaconf'
]

for pkg in packages:
    print(f"\nInstalling {pkg}...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', pkg])
        print(f"✓ {pkg} installed")
    except:
        print(f"✗ {pkg} failed")

# CRITICAL: Restart kernel message
print("\n" + "="*70)
print("⚠️  IMPORTANT: After packages install, you MUST:")
print("   1. Click 'Restart Session' button (top right)")
print("   2. Then run the REST of the code below")
print("="*70)

# ========================================================================
# RUN THIS AFTER RESTARTING KERNEL
# ========================================================================

# Verify imports work
print("\nVerifying imports...")
try:
    import rasterio
    print("✓ rasterio")
except ImportError as e:
    print(f"✗ rasterio: {e}")

try:
    import faiss
    print("✓ faiss")
except ImportError as e:
    print(f"✗ faiss: {e}")
    print("  Note: On Kaggle CPU, faiss-cpu might be needed instead")

try:
    import cv2
    print("✓ opencv")
except ImportError as e:
    print(f"✗ opencv: {e}")

try:
    import yaml
    print("✓ pyyaml")
except ImportError as e:
    print(f"✗ pyyaml: {e}")

print("\n✓ Import verification complete!")

# Clone repo
import os
print("\n" + "="*70)
print("CLONING REPOSITORY...")
print("="*70)
os.chdir('/kaggle/working')
!git clone https://github.com/meethp1884/dpiit_ps03.git
os.chdir('dpiit_ps03')
print("✓ Repository ready")

# Link datasets
print("\n" + "="*70)
print("LINKING DATASETS...")
print("="*70)
!mkdir -p data
!ln -s /kaggle/input/ps03-sample-set data/sample_set
!ln -s /kaggle/input/ps03-training-set data/training_set
!ln -s /kaggle/input/ps03-testing-set data/testing_set

# Verify data
!echo "Sample set:"; ls data/sample_set/ | head -3
!echo "\nTesting set:"; ls data/testing_set/*.tif 2>/dev/null | wc -l || echo "0"

# Extract chips
print("\n" + "="*70)
print("EXTRACTING CHIPS...")
print("="*70)
!python scripts/batch_extract_chips.py --sample-dir data/sample_set --out-dir chips --max-chips 5
!echo "Chips extracted:"; ls chips/

# Build index
print("\n" + "="*70)
print("BUILDING INDEX...")
print("="*70)
!python scripts/build_index.py --targets data/testing_set --out cache/indexes --device cuda --config configs/default.yaml

# Search all classes
print("\n" + "="*70)
print("SEARCHING ALL CLASSES...")
print("="*70)

import glob
from datetime import datetime

classes_folders = [
    "Solar Panel", "Brick Kiln",
    "Pond-1 and Pond-2", "Pond-1,Pond-2 and Playground",
    "Pond-2,STP and Sheds", "MetroShed,STP and Sheds",
    "Playground", "Sheds"
]

original_names = {
    "Pond-1 and Pond-2": "Pond-1 & Pond-2",
    "Pond-1,Pond-2 and Playground": "Pond-1,Pond-2 & Playground",
    "Pond-2,STP and Sheds": "Pond-2,STP & Sheds",
    "MetroShed,STP and Sheds": "MetroShed,STP & Sheds"
}

os.makedirs("outputs", exist_ok=True)

for i, folder in enumerate(classes_folders, 1):
    submission_name = original_names.get(folder, folder)
    safe = folder.replace(" ", "_").replace(",", "")
    chips = glob.glob(f"chips/{folder}/*.tif")[:5]
    
    if chips:
        print(f"[{i}/8] {folder}: {len(chips)} chips")
        chip_str = " ".join([f'"{c}"' for c in chips])
        result = os.system(f'python scripts/run_search.py --chips {chip_str} --index cache/indexes --name "{submission_name}" --out outputs/temp_{safe}.txt --team AIGR-S47377 --config configs/default.yaml --device cuda')
        if result != 0:
            print(f"  ✗ Search failed with code {result}")
    else:
        print(f"[{i}/8] {folder}: NO CHIPS")

# Combine results
print("\n" + "="*70)
print("COMBINING RESULTS...")
print("="*70)

submission = f"outputs/GC_PS03_{datetime.now().strftime('%d-%b-%Y')}_AIGR-S47377.txt"
temp_files = glob.glob("outputs/temp_*.txt")
print(f"Found {len(temp_files)} temp files")

with open(submission, 'w') as out:
    for f in sorted(temp_files):
        with open(f) as inf:
            out.write(inf.read())

# Summary
lines = open(submission).readlines()
print(f"\nTotal: {len(lines)} detections")

if len(lines) > 0:
    for folder in classes_folders:
        orig = original_names.get(folder, folder)
        count = sum(1 for l in lines if orig in l)
        print(f"{orig:35s}: {count:4d}")
    
    print("\nFirst 10:")
    for i, l in enumerate(lines[:10], 1):
        print(f"{i}. {l.strip()}")
else:
    print("✗ NO DETECTIONS FOUND!")
    print("Check errors above")

# Download
from shutil import copy
copy(submission, '/kaggle/working/')
print(f"\n✓ Download: {os.path.basename(submission)}")
