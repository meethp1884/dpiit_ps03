"""
Batch extract chips from all GeoJSON files in sample-set
"""

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Batch extract chips from sample-set')
    parser.add_argument('--sample-dir', type=str, required=True,
                       help='Path to sample-set directory (with class folders)')
    parser.add_argument('--out-dir', type=str, required=True,
                       help='Output directory for chips')
    parser.add_argument('--max-chips', type=int, default=5,
                       help='Maximum chips per class per file (default: 5)')
    parser.add_argument('--padding', type=int, default=10,
                       help='Padding around bounding box (pixels)')
    
    args = parser.parse_args()
    
    sample_dir = Path(args.sample_dir)
    if not sample_dir.exists():
        print(f"ERROR: Sample directory not found: {sample_dir}")
        return
    
    # Find all class folders
    class_folders = [d for d in sample_dir.iterdir() if d.is_dir()]
    
    if not class_folders:
        print(f"ERROR: No class folders found in {sample_dir}")
        return
    
    print(f"Found {len(class_folders)} class folders:")
    for folder in class_folders:
        print(f"  - {folder.name}")
    
    print()
    
    # Process each class folder
    total_processed = 0
    for class_folder in class_folders:
        class_name = class_folder.name
        print(f"Processing class: {class_name}")
        
        # Find all JSON files
        json_files = list(class_folder.glob("*.json"))
        
        if not json_files:
            print(f"  No JSON files found, skipping...")
            continue
        
        print(f"  Found {len(json_files)} JSON files")
        
        # Process each JSON file
        for json_file in json_files:
            print(f"  Processing: {json_file.name}")
            
            # Find corresponding TIFF
            tiff_file = json_file.with_suffix('.tif')
            if not tiff_file.exists():
                print(f"    ✗ TIFF not found: {tiff_file.name}")
                continue
            
            # Run extraction script
            cmd = [
                sys.executable,
                str(Path(__file__).parent / "extract_chips_from_geojson.py"),
                "--json", str(json_file),
                "--image", str(tiff_file),
                "--out-dir", args.out_dir,
                "--max-chips", str(args.max_chips),
                "--padding", str(args.padding)
            ]
            
            try:
                subprocess.run(cmd, check=True)
                total_processed += 1
            except subprocess.CalledProcessError as e:
                print(f"    ✗ Failed: {e}")
        
        print()
    
    print(f"✓ Processed {total_processed} files")
    print(f"✓ Chips saved to: {args.out_dir}")
    print(f"\nNext step: Build index and run search!")


if __name__ == '__main__':
    main()
