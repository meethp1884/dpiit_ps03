"""
Output writer for PS-03 submission format
Writes space-delimited detection results
"""

from pathlib import Path
from typing import List, Optional
from datetime import datetime
from .candidate import Detection


def write_submission_file(
    detections: List[Detection],
    output_path: str,
    default_score: float = -1.0,
    sort_by_image: bool = True
):
    """
    Write detections to PS-03 submission format
    
    Format: x_min y_min x_max y_max class_name target_filename score
    
    Args:
        detections: List of Detection objects
        output_path: Path to output file
        default_score: Default score if score is None
        sort_by_image: Whether to sort by target filename
    """
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Sort if requested
    if sort_by_image:
        detections = sorted(detections, key=lambda d: (d.target_filename, -d.score))
    
    # Write file
    with open(output_path, 'w') as f:
        for det in detections:
            score = det.score if det.score is not None else default_score
            
            line = f"{det.x_min} {det.y_min} {det.x_max} {det.y_max} " \
                   f"{det.class_name} {det.target_filename} {score:.6f}\n"
            f.write(line)
    
    print(f"Wrote {len(detections)} detections to {output_path}")


def generate_submission_filename(
    team_name: str,
    date: Optional[datetime] = None
) -> str:
    """
    Generate PS-03 submission filename
    
    Format: GC_PS03_<DD-MMM-YYYY>_<Team>.txt
    
    Args:
        team_name: Team name
        date: Date (defaults to now)
        
    Returns:
        Filename string
    """
    if date is None:
        date = datetime.now()
    
    date_str = date.strftime("%d-%b-%Y")
    filename = f"GC_PS03_{date_str}_{team_name}.txt"
    
    return filename


def read_submission_file(filepath: str) -> List[Detection]:
    """
    Read detections from submission file
    
    Args:
        filepath: Path to submission file
        
    Returns:
        List of Detection objects
    """
    detections = []
    
    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) < 6:
                print(f"Warning: Line {line_num} has insufficient columns, skipping")
                continue
            
            try:
                x_min = int(parts[0])
                y_min = int(parts[1])
                x_max = int(parts[2])
                y_max = int(parts[3])
                class_name = parts[4]
                target_filename = parts[5]
                score = float(parts[6]) if len(parts) > 6 else -1.0
                
                det = Detection(
                    x_min=x_min,
                    y_min=y_min,
                    x_max=x_max,
                    y_max=y_max,
                    score=score,
                    class_name=class_name,
                    target_filename=target_filename
                )
                detections.append(det)
                
            except (ValueError, IndexError) as e:
                print(f"Warning: Line {line_num} parse error: {e}, skipping")
                continue
    
    return detections


def write_detections_summary(
    detections: List[Detection],
    output_path: str
):
    """
    Write summary statistics of detections
    
    Args:
        detections: List of Detection objects
        output_path: Path to summary file
    """
    from collections import defaultdict
    
    # Compute statistics
    total = len(detections)
    
    by_class = defaultdict(int)
    by_image = defaultdict(int)
    scores = []
    
    for det in detections:
        by_class[det.class_name] += 1
        by_image[det.target_filename] += 1
        if det.score is not None and det.score != -1:
            scores.append(det.score)
    
    # Write summary
    with open(output_path, 'w') as f:
        f.write(f"PS-03 Detection Summary\n")
        f.write(f"=" * 50 + "\n\n")
        
        f.write(f"Total detections: {total}\n")
        f.write(f"Unique images: {len(by_image)}\n")
        f.write(f"Unique classes: {len(by_class)}\n\n")
        
        f.write("Detections by class:\n")
        for cls, count in sorted(by_class.items()):
            f.write(f"  {cls}: {count}\n")
        
        f.write("\nDetections by image:\n")
        for img, count in sorted(by_image.items(), key=lambda x: -x[1])[:10]:
            f.write(f"  {img}: {count}\n")
        if len(by_image) > 10:
            f.write(f"  ... and {len(by_image) - 10} more images\n")
        
        if scores:
            import numpy as np
            f.write(f"\nScore statistics:\n")
            f.write(f"  Mean: {np.mean(scores):.4f}\n")
            f.write(f"  Median: {np.median(scores):.4f}\n")
            f.write(f"  Min: {np.min(scores):.4f}\n")
            f.write(f"  Max: {np.max(scores):.4f}\n")
    
    print(f"Wrote summary to {output_path}")


def validate_submission_format(filepath: str) -> bool:
    """
    Validate submission file format
    
    Args:
        filepath: Path to submission file
        
    Returns:
        True if valid, False otherwise
    """
    try:
        detections = read_submission_file(filepath)
        
        if not detections:
            print("ERROR: No detections found in file")
            return False
        
        # Check basic validity
        for i, det in enumerate(detections):
            # Check coordinates
            if det.x_min < 0 or det.y_min < 0:
                print(f"ERROR: Detection {i} has negative coordinates")
                return False
            
            if det.x_max <= det.x_min or det.y_max <= det.y_min:
                print(f"ERROR: Detection {i} has invalid box dimensions")
                return False
            
            # Check class name
            if not det.class_name or det.class_name.isspace():
                print(f"ERROR: Detection {i} has empty class name")
                return False
            
            # Check filename
            if not det.target_filename or det.target_filename.isspace():
                print(f"ERROR: Detection {i} has empty filename")
                return False
        
        print(f"✓ Submission file is valid ({len(detections)} detections)")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to validate submission: {e}")
        return False
