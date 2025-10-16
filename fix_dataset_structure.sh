#!/bin/bash
# Automated script to fix dataset folder structure

echo "================================================"
echo "PS-03 Dataset Structure Fix"
echo "================================================"
echo ""

cd "$(dirname "$0")"

echo "Step 1: Rename mock_set to testing_set"
echo "----------------------------------------"
if [ -d "data/mock_set" ]; then
    if [ -d "data/testing_set" ]; then
        echo "WARNING: testing_set already exists!"
        echo "Skipping rename..."
    else
        echo "Renaming mock_set to testing_set..."
        mv "data/mock_set" "data/testing_set"
        echo "✓ Renamed to testing_set"
    fi
else
    echo "✓ mock_set not found (already renamed or doesn't exist)"
fi
echo ""

echo "Step 2: Flatten sample-set nested structure"
echo "----------------------------------------"
if [ -d "data/sample-set/sample-set" ]; then
    echo "Found nested sample-set folder"
    
    # Create temp folder
    mkdir -p "data/sample_set_temp"
    
    # Move all class folders to temp
    echo "Moving class folders..."
    cp -r "data/sample-set/sample-set/"* "data/sample_set_temp/"
    
    # Remove old nested structure
    echo "Removing old structure..."
    rm -rf "data/sample-set"
    
    # Rename temp to sample_set
    echo "Renaming to sample_set..."
    mv "data/sample_set_temp" "data/sample_set"
    
    echo "✓ Flattened sample-set structure"
elif [ -d "data/sample-set" ]; then
    echo "Renaming sample-set to sample_set..."
    if [ -d "data/sample_set" ]; then
        echo "WARNING: sample_set already exists!"
    else
        mv "data/sample-set" "data/sample_set"
        echo "✓ Renamed to sample_set"
    fi
else
    echo "✓ sample-set already processed or doesn't exist"
fi
echo ""

echo "Step 3: Verify structure"
echo "----------------------------------------"
echo "Current data folder contents:"
ls -1 data/
echo ""

echo "================================================"
echo "Structure Fix Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Extract chips: python scripts/batch_extract_chips.py --sample-dir data/sample_set --out-dir chips"
echo "2. Build index:   python scripts/build_index.py --targets data/testing_set --out cache/indexes"
echo "3. Run search:    python scripts/run_search.py --chips 'chips/Solar Panel/chip_01.tif' --index cache/indexes --name 'Solar Panel' --out outputs/results.txt"
echo ""
