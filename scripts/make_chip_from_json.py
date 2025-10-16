"""
Extract chips from images using JSON annotations
"""

import argparse
import json
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import read_tiff, write_tiff, normalize_bands


def extract_chip_from_bbox(image_path: str, bbox: list, output_path: str):
    """
    Extract chip from image using bounding box
    
    Args:
        image_path: Path to source image
        bbox: [x_min, y_min, x_max, y_max] or [x, y, width, height]
        output_path: Path to save chip
    """
    # Read image
    image, metadata = read_tiff(image_path)
    
    # Parse bbox
    if len(bbox) == 4:
        # Could be [x_min, y_min, x_max, y_max] or [x, y, width, height]
        # Assume [x_min, y_min, x_max, y_max] if values look like corners
        if bbox[2] > bbox[0] and bbox[3] > bbox[1]:
            x_min, y_min, x_max, y_max = bbox
        else:
            # Assume [x, y, width, height]
            x_min, y_min = bbox[0], bbox[1]
            x_max, y_max = bbox[0] + bbox[2], bbox[1] + bbox[3]
    else:
        raise ValueError(f"Invalid bbox format: {bbox}")
    
    # Extract region
    C, H, W = image.shape
    x_min = max(0, int(x_min))
    y_min = max(0, int(y_min))
    x_max = min(W, int(x_max))
    y_max = min(H, int(y_max))
    
    chip = image[:, y_min:y_max, x_min:x_max]
    
    # Save chip
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    write_tiff(output_path, chip, metadata)
    
    print(f"✓ Extracted chip: {chip.shape} -> {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Extract chip from image using JSON annotation')
    parser.add_argument('--json', type=str, required=True,
                       help='Path to JSON annotation file')
    parser.add_argument('--image', type=str, default=None,
                       help='Path to image (if not in JSON)')
    parser.add_argument('--out', type=str, required=True,
                       help='Output path for chip')
    parser.add_argument('--index', type=int, default=0,
                       help='Object index in JSON (if multiple)')
    
    args = parser.parse_args()
    
    # Load JSON
    with open(args.json, 'r') as f:
        data = json.load(f)
    
    # Extract image path
    image_path = args.image
    if not image_path:
        # Try to find image path in JSON
        if 'image_path' in data:
            image_path = data['image_path']
        elif 'filename' in data:
            image_path = str(Path(args.json).parent / data['filename'])
        else:
            # Use same name as JSON but with .tif extension
            image_path = str(Path(args.json).with_suffix('.tif'))
    
    if not Path(image_path).exists():
        print(f"ERROR: Image not found: {image_path}")
        return
    
    # Extract bbox
    bbox = None
    
    # Try different JSON structures
    if 'annotations' in data:
        if len(data['annotations']) > args.index:
            ann = data['annotations'][args.index]
            if 'bbox' in ann:
                bbox = ann['bbox']
    elif 'objects' in data:
        if len(data['objects']) > args.index:
            obj = data['objects'][args.index]
            if 'bbox' in obj:
                bbox = obj['bbox']
    elif 'bbox' in data:
        bbox = data['bbox']
    
    if bbox is None:
        print("ERROR: Could not find bbox in JSON")
        print("Supported formats: {'bbox': [...]}, {'annotations': [{'bbox': [...]}]}, {'objects': [{'bbox': [...]}]}")
        return
    
    # Extract chip
    extract_chip_from_bbox(image_path, bbox, args.out)


if __name__ == '__main__':
    main()
