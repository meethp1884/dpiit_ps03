"""
Extract chips from GeoJSON annotations (sample-set format)
Handles MultiPolygon geometries and converts to bounding boxes
"""

import argparse
import json
import numpy as np
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import read_tiff, write_tiff, normalize_bands


def polygon_to_bbox(coordinates):
    """
    Convert polygon coordinates to bounding box
    
    Args:
        coordinates: List of [x, y] coordinates
    
    Returns:
        [x_min, y_min, x_max, y_max]
    """
    coords_array = np.array(coordinates)
    x_coords = coords_array[:, 0]
    y_coords = coords_array[:, 1]
    
    return [
        int(np.min(x_coords)),
        int(np.min(y_coords)),
        int(np.max(x_coords)),
        int(np.max(y_coords))
    ]


def extract_chip_from_bbox(image_path: str, bbox: list, output_path: str, padding: int = 0):
    """
    Extract chip from image using bounding box
    
    Args:
        image_path: Path to source image
        bbox: [x_min, y_min, x_max, y_max]
        output_path: Path to save chip
        padding: Extra pixels to add around bbox
    """
    # Read image
    image, metadata = read_tiff(image_path)
    
    # Parse bbox
    x_min, y_min, x_max, y_max = bbox
    
    # Add padding
    x_min = max(0, x_min - padding)
    y_min = max(0, y_min - padding)
    x_max = min(image.shape[2], x_max + padding)
    y_max = min(image.shape[1], y_max + padding)
    
    # Extract region
    chip = image[:, y_min:y_max, x_min:x_max]
    
    # Save chip
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    write_tiff(output_path, chip, metadata)
    
    return chip.shape


def main():
    parser = argparse.ArgumentParser(description='Extract chips from GeoJSON annotations')
    parser.add_argument('--json', type=str, required=True,
                       help='Path to GeoJSON file')
    parser.add_argument('--image', type=str, default=None,
                       help='Path to image (if not same directory as JSON)')
    parser.add_argument('--out-dir', type=str, required=True,
                       help='Output directory for chips')
    parser.add_argument('--max-chips', type=int, default=5,
                       help='Maximum chips per class (default: 5)')
    parser.add_argument('--padding', type=int, default=10,
                       help='Padding around bounding box (pixels)')
    
    args = parser.parse_args()
    
    # Load GeoJSON
    with open(args.json, 'r') as f:
        data = json.load(f)
    
    # Extract image path
    if args.image:
        image_path = args.image
    else:
        # Use same directory as JSON, replace extension
        json_path = Path(args.json)
        image_name = data.get('name', json_path.stem)
        image_path = str(json_path.parent / f"{image_name}.tif")
    
    if not Path(image_path).exists():
        print(f"ERROR: Image not found: {image_path}")
        return
    
    print(f"Processing: {image_path}")
    print(f"Annotations: {args.json}")
    
    # Extract features
    features = data.get('features', [])
    if not features:
        print("ERROR: No features found in GeoJSON")
        return
    
    # Group by class
    chips_by_class = {}
    for feature in features:
        # Get class name
        props = feature.get('properties', {})
        class_name = props.get('Class Name', props.get('class', props.get('label', 'unknown')))
        
        # Get geometry
        geometry = feature.get('geometry', {})
        geom_type = geometry.get('type')
        coordinates = geometry.get('coordinates', [])
        
        if geom_type == 'MultiPolygon':
            # MultiPolygon: coordinates[i][0] is the outer ring
            for polygon in coordinates:
                bbox = polygon_to_bbox(polygon[0])
                
                if class_name not in chips_by_class:
                    chips_by_class[class_name] = []
                chips_by_class[class_name].append(bbox)
        
        elif geom_type == 'Polygon':
            # Polygon: coordinates[0] is the outer ring
            bbox = polygon_to_bbox(coordinates[0])
            
            if class_name not in chips_by_class:
                chips_by_class[class_name] = []
            chips_by_class[class_name].append(bbox)
    
    # Extract chips
    total_extracted = 0
    for class_name, bboxes in chips_by_class.items():
        print(f"\nClass: {class_name} ({len(bboxes)} annotations)")
        
        # Limit to max_chips
        bboxes = bboxes[:args.max_chips]
        
        for i, bbox in enumerate(bboxes, 1):
            # Create output path
            out_path = Path(args.out_dir) / class_name / f"chip_{i:02d}.tif"
            
            # Extract chip
            try:
                shape = extract_chip_from_bbox(image_path, bbox, str(out_path), args.padding)
                print(f"  ✓ Extracted chip {i}: {shape} -> {out_path}")
                total_extracted += 1
            except Exception as e:
                print(f"  ✗ Failed chip {i}: {e}")
    
    print(f"\n✓ Total chips extracted: {total_extracted}")
    print(f"✓ Output directory: {args.out_dir}")


if __name__ == '__main__':
    main()
