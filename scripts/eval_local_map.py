"""
Evaluate local mAP on validation/sample set
Computes retrieval metrics for embedder evaluation
"""

import argparse
import yaml
import numpy as np
from pathlib import Path
from collections import defaultdict
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import read_submission_file, compute_iou


def compute_ap(recalls, precisions):
    """Compute Average Precision from precision-recall curve"""
    # Ensure arrays
    recalls = np.array(recalls)
    precisions = np.array(precisions)
    
    # Sort by recall
    idx = np.argsort(recalls)
    recalls = recalls[idx]
    precisions = precisions[idx]
    
    # Interpolated AP
    ap = 0
    for i in range(len(recalls)):
        if i == 0:
            r_diff = recalls[i]
        else:
            r_diff = recalls[i] - recalls[i-1]
        ap += r_diff * precisions[i]
    
    return ap


def compute_precision_recall(
    predictions: list,
    ground_truth: list,
    iou_threshold: float = 0.5
):
    """
    Compute precision-recall for detection task
    
    Args:
        predictions: List of (x_min, y_min, x_max, y_max, score) tuples
        ground_truth: List of (x_min, y_min, x_max, y_max) tuples
        iou_threshold: IoU threshold for TP
        
    Returns:
        Tuple of (precision, recall, ap)
    """
    if not predictions:
        return 0.0, 0.0, 0.0
    
    if not ground_truth:
        return 0.0, 0.0, 0.0
    
    # Sort predictions by score
    predictions = sorted(predictions, key=lambda x: x[4], reverse=True)
    
    n_gt = len(ground_truth)
    matched_gt = set()
    
    precisions = []
    recalls = []
    
    tp = 0
    fp = 0
    
    for pred in predictions:
        pred_box = pred[:4]
        
        # Find best matching GT
        best_iou = 0
        best_gt_idx = -1
        
        for gt_idx, gt_box in enumerate(ground_truth):
            if gt_idx in matched_gt:
                continue
            
            iou = compute_iou(pred_box, gt_box)
            if iou > best_iou:
                best_iou = iou
                best_gt_idx = gt_idx
        
        # Check if TP
        if best_iou >= iou_threshold and best_gt_idx >= 0:
            tp += 1
            matched_gt.add(best_gt_idx)
        else:
            fp += 1
        
        # Compute precision and recall at this point
        precision = tp / (tp + fp)
        recall = tp / n_gt
        
        precisions.append(precision)
        recalls.append(recall)
    
    # Compute AP
    ap = compute_ap(recalls, precisions)
    
    # Final precision and recall
    final_precision = tp / len(predictions)
    final_recall = tp / n_gt
    
    return final_precision, final_recall, ap


def load_ground_truth_from_json(json_path: str):
    """
    Load ground truth bounding boxes from JSON file
    Expected format: list of dicts with 'bbox' keys
    """
    import json
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    boxes = []
    
    # Handle different JSON formats
    if isinstance(data, list):
        for item in data:
            if 'bbox' in item:
                bbox = item['bbox']
                if len(bbox) == 4:
                    boxes.append(tuple(bbox))
    elif isinstance(data, dict):
        if 'annotations' in data:
            for ann in data['annotations']:
                if 'bbox' in ann:
                    bbox = ann['bbox']
                    if len(bbox) == 4:
                        boxes.append(tuple(bbox))
        elif 'objects' in data:
            for obj in data['objects']:
                if 'bbox' in obj:
                    bbox = obj['bbox']
                    if len(bbox) == 4:
                        boxes.append(tuple(bbox))
    
    return boxes


def evaluate_submission(
    submission_path: str,
    ground_truth_dir: str,
    iou_thresholds: list = [0.5, 0.75, 0.9]
):
    """
    Evaluate submission file against ground truth
    
    Args:
        submission_path: Path to submission file
        ground_truth_dir: Directory containing JSON ground truth files
        iou_thresholds: List of IoU thresholds to evaluate
    """
    # Load predictions
    detections = read_submission_file(submission_path)
    
    # Group by image
    predictions_by_image = defaultdict(list)
    for det in detections:
        pred = (det.x_min, det.y_min, det.x_max, det.y_max, det.score)
        predictions_by_image[det.target_filename].append(pred)
    
    # Load ground truth
    gt_dir = Path(ground_truth_dir)
    ground_truth_by_image = {}
    
    for json_file in gt_dir.glob('*.json'):
        image_name = json_file.stem
        boxes = load_ground_truth_from_json(str(json_file))
        if boxes:
            ground_truth_by_image[image_name] = boxes
    
    print(f"Loaded predictions for {len(predictions_by_image)} images")
    print(f"Loaded ground truth for {len(ground_truth_by_image)} images")
    
    # Evaluate at each IoU threshold
    results = {}
    
    for iou_thresh in iou_thresholds:
        print(f"\n{'='*60}")
        print(f"Evaluating at IoU threshold: {iou_thresh}")
        print(f"{'='*60}")
        
        all_precisions = []
        all_recalls = []
        all_aps = []
        
        for image_name, gt_boxes in ground_truth_by_image.items():
            preds = predictions_by_image.get(image_name, [])
            
            precision, recall, ap = compute_precision_recall(
                preds, gt_boxes, iou_thresh
            )
            
            all_precisions.append(precision)
            all_recalls.append(recall)
            all_aps.append(ap)
            
            if len(all_aps) <= 5:  # Print first few
                print(f"  {image_name}: P={precision:.3f}, R={recall:.3f}, AP={ap:.3f}")
        
        # Compute mean metrics
        mean_precision = np.mean(all_precisions)
        mean_recall = np.mean(all_recalls)
        mean_ap = np.mean(all_aps)
        
        results[iou_thresh] = {
            'mAP': mean_ap,
            'precision': mean_precision,
            'recall': mean_recall
        }
        
        print(f"\nSummary @ IoU={iou_thresh}:")
        print(f"  mAP: {mean_ap:.4f}")
        print(f"  Precision: {mean_precision:.4f}")
        print(f"  Recall: {mean_recall:.4f}")
    
    # Overall summary
    print(f"\n{'='*60}")
    print("OVERALL RESULTS")
    print(f"{'='*60}")
    
    for iou_thresh, metrics in results.items():
        print(f"IoU {iou_thresh}: mAP={metrics['mAP']:.4f}, "
              f"P={metrics['precision']:.4f}, R={metrics['recall']:.4f}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Evaluate local mAP')
    parser.add_argument('--submission', type=str, required=True,
                       help='Path to submission file')
    parser.add_argument('--ground-truth', type=str, required=True,
                       help='Path to ground truth directory (JSON files)')
    parser.add_argument('--iou-thresholds', type=float, nargs='+',
                       default=[0.5, 0.75, 0.9],
                       help='IoU thresholds for evaluation')
    parser.add_argument('--output', type=str, default=None,
                       help='Path to save evaluation results (JSON)')
    
    args = parser.parse_args()
    
    # Validate paths
    if not Path(args.submission).exists():
        print(f"ERROR: Submission file not found: {args.submission}")
        return
    
    if not Path(args.ground_truth).exists():
        print(f"ERROR: Ground truth directory not found: {args.ground_truth}")
        return
    
    # Evaluate
    results = evaluate_submission(
        args.submission,
        args.ground_truth,
        args.iou_thresholds
    )
    
    # Save results if requested
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to {args.output}")


if __name__ == '__main__':
    main()
