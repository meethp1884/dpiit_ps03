"""
Non-Maximum Suppression (NMS) for post-processing detections
Supports both hard and soft NMS
"""

import numpy as np
from typing import List
from .candidate import Detection, compute_iou


def hard_nms(
    detections: List[Detection],
    iou_threshold: float = 0.5,
    score_threshold: float = 0.3
) -> List[Detection]:
    """
    Hard NMS: suppress detections with IoU > threshold
    
    Args:
        detections: List of Detection objects
        iou_threshold: IoU threshold for suppression
        score_threshold: Minimum score to keep
        
    Returns:
        Filtered list of detections
    """
    if not detections:
        return []
    
    # Filter by score
    detections = [d for d in detections if d.score >= score_threshold]
    
    if not detections:
        return []
    
    # Sort by score descending
    sorted_dets = sorted(detections, key=lambda d: d.score, reverse=True)
    
    keep = []
    suppress = set()
    
    for i, det in enumerate(sorted_dets):
        if i in suppress:
            continue
        
        keep.append(det)
        box1 = (det.x_min, det.y_min, det.x_max, det.y_max)
        
        # Suppress overlapping boxes
        for j in range(i + 1, len(sorted_dets)):
            if j in suppress:
                continue
            
            other = sorted_dets[j]
            box2 = (other.x_min, other.y_min, other.x_max, other.y_max)
            
            if compute_iou(box1, box2) > iou_threshold:
                suppress.add(j)
    
    return keep


def soft_nms(
    detections: List[Detection],
    iou_threshold: float = 0.5,
    score_threshold: float = 0.3,
    sigma: float = 0.5,
    method: str = 'gaussian'
) -> List[Detection]:
    """
    Soft NMS: decay scores of overlapping detections
    
    Args:
        detections: List of Detection objects
        iou_threshold: IoU threshold
        score_threshold: Minimum score to keep
        sigma: Gaussian sigma for soft decay
        method: 'gaussian' or 'linear'
        
    Returns:
        List of detections with updated scores
    """
    if not detections:
        return []
    
    # Create mutable copy
    detections = [Detection(
        x_min=d.x_min,
        y_min=d.y_min,
        x_max=d.x_max,
        y_max=d.y_max,
        score=d.score,
        class_name=d.class_name,
        target_filename=d.target_filename,
        metadata=d.metadata
    ) for d in detections]
    
    # Sort by score descending
    detections = sorted(detections, key=lambda d: d.score, reverse=True)
    
    keep = []
    
    for i in range(len(detections)):
        det = detections[i]
        
        if det.score < score_threshold:
            continue
        
        keep.append(det)
        box1 = (det.x_min, det.y_min, det.x_max, det.y_max)
        
        # Decay scores of remaining detections
        for j in range(i + 1, len(detections)):
            other = detections[j]
            box2 = (other.x_min, other.y_min, other.x_max, other.y_max)
            
            iou = compute_iou(box1, box2)
            
            if iou > 0:
                if method == 'gaussian':
                    # Gaussian decay
                    weight = np.exp(-(iou ** 2) / sigma)
                elif method == 'linear':
                    # Linear decay
                    if iou > iou_threshold:
                        weight = 1 - iou
                    else:
                        weight = 1
                else:
                    weight = 1
                
                other.score *= weight
    
    # Final filter
    keep = [d for d in keep if d.score >= score_threshold]
    
    return keep


def merge_detections(
    detections: List[Detection],
    iou_threshold: float = 0.5
) -> List[Detection]:
    """
    Merge overlapping detections by averaging coordinates
    
    Args:
        detections: List of Detection objects
        iou_threshold: IoU threshold for merging
        
    Returns:
        List of merged detections
    """
    from .candidate import cluster_detections, merge_cluster
    
    if not detections:
        return []
    
    # Cluster overlapping detections
    clusters = cluster_detections(detections, iou_threshold)
    
    # Merge each cluster
    merged = [merge_cluster(cluster) for cluster in clusters]
    
    return merged


def apply_nms_per_image(
    grouped_detections: dict,
    method: str = 'soft',
    iou_threshold: float = 0.5,
    score_threshold: float = 0.3,
    sigma: float = 0.5
) -> dict:
    """
    Apply NMS to detections grouped by image
    
    Args:
        grouped_detections: Dict mapping image_id -> List[Detection]
        method: 'soft' or 'hard'
        iou_threshold: IoU threshold
        score_threshold: Score threshold
        sigma: Sigma for soft NMS
        
    Returns:
        Dict with NMS applied per image
    """
    result = {}
    
    for image_id, detections in grouped_detections.items():
        if method == 'soft':
            filtered = soft_nms(
                detections,
                iou_threshold=iou_threshold,
                score_threshold=score_threshold,
                sigma=sigma
            )
        elif method == 'hard':
            filtered = hard_nms(
                detections,
                iou_threshold=iou_threshold,
                score_threshold=score_threshold
            )
        else:
            raise ValueError(f"Unknown NMS method: {method}")
        
        result[image_id] = filtered
    
    return result


def filter_by_confidence(
    detections: List[Detection],
    threshold: float
) -> List[Detection]:
    """
    Filter detections by confidence threshold
    
    Args:
        detections: List of Detection objects
        threshold: Minimum confidence score
        
    Returns:
        Filtered list
    """
    return [d for d in detections if d.score >= threshold]


def filter_by_area(
    detections: List[Detection],
    min_area: int = 100,
    max_area: int = None
) -> List[Detection]:
    """
    Filter detections by bounding box area
    
    Args:
        detections: List of Detection objects
        min_area: Minimum area in pixels
        max_area: Maximum area in pixels (None = no limit)
        
    Returns:
        Filtered list
    """
    filtered = []
    
    for det in detections:
        area = (det.x_max - det.x_min) * (det.y_max - det.y_min)
        
        if area < min_area:
            continue
        
        if max_area is not None and area > max_area:
            continue
        
        filtered.append(det)
    
    return filtered
