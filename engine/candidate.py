"""
Candidate retrieval and aggregation
Retrieves top-K tiles per chip and aggregates by target image
"""

import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Detection:
    """Represents a single detection/candidate"""
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    score: float
    class_name: str
    target_filename: str
    metadata: Dict = None


class CandidateRetriever:
    """
    Retrieves and aggregates candidates from FAISS search results
    """
    
    def __init__(
        self,
        top_k_per_chip: int = 500,
        top_k_per_image: int = 100,
        similarity_threshold: float = 0.7
    ):
        """
        Args:
            top_k_per_chip: Maximum candidates per query chip
            top_k_per_image: Maximum candidates per target image
            similarity_threshold: Minimum similarity score
        """
        self.top_k_per_chip = top_k_per_chip
        self.top_k_per_image = top_k_per_image
        self.similarity_threshold = similarity_threshold
    
    def retrieve_candidates(
        self,
        search_results: List[List[Dict]],
        class_name: str,
        chip_names: List[str] = None
    ) -> List[Detection]:
        """
        Process FAISS search results into candidate detections
        
        Args:
            search_results: Results from FAISSIndex.search_with_metadata()
                           List of lists, one per query chip
            class_name: Class name for detections
            chip_names: Optional list of chip identifiers
            
        Returns:
            List of Detection objects
        """
        all_candidates = []
        
        # Process each chip's results
        for chip_idx, chip_results in enumerate(search_results):
            chip_id = chip_names[chip_idx] if chip_names else f"chip_{chip_idx}"
            
            # Take top-K per chip
            chip_results = chip_results[:self.top_k_per_chip]
            
            for result in chip_results:
                score = result['score']
                
                # Filter by threshold
                if score < self.similarity_threshold:
                    continue
                
                metadata = result['metadata']
                
                # Extract bounding box
                x = metadata.get('x', 0)
                y = metadata.get('y', 0)
                width = metadata.get('width', 0)
                height = metadata.get('height', 0)
                image_id = metadata.get('image_id', 'unknown')
                
                detection = Detection(
                    x_min=x,
                    y_min=y,
                    x_max=x + width,
                    y_max=y + height,
                    score=score,
                    class_name=class_name,
                    target_filename=image_id,
                    metadata={
                        'chip_id': chip_id,
                        **metadata
                    }
                )
                
                all_candidates.append(detection)
        
        return all_candidates
    
    def aggregate_by_image(
        self,
        detections: List[Detection]
    ) -> Dict[str, List[Detection]]:
        """
        Group detections by target image
        
        Args:
            detections: List of Detection objects
            
        Returns:
            Dict mapping image_id -> list of detections
        """
        grouped = defaultdict(list)
        
        for det in detections:
            grouped[det.target_filename].append(det)
        
        return dict(grouped)
    
    def filter_top_k_per_image(
        self,
        grouped_detections: Dict[str, List[Detection]]
    ) -> Dict[str, List[Detection]]:
        """
        Keep only top-K detections per image
        
        Args:
            grouped_detections: Dict from aggregate_by_image()
            
        Returns:
            Filtered dict
        """
        filtered = {}
        
        for image_id, detections in grouped_detections.items():
            # Sort by score descending
            sorted_dets = sorted(detections, key=lambda d: d.score, reverse=True)
            # Take top-K
            filtered[image_id] = sorted_dets[:self.top_k_per_image]
        
        return filtered
    
    def process(
        self,
        search_results: List[List[Dict]],
        class_name: str,
        chip_names: List[str] = None
    ) -> Tuple[List[Detection], Dict[str, List[Detection]]]:
        """
        Full pipeline: retrieve candidates, aggregate, and filter
        
        Args:
            search_results: FAISS search results
            class_name: Class name
            chip_names: Optional chip identifiers
            
        Returns:
            Tuple of (all_detections, grouped_detections)
        """
        # Retrieve candidates
        detections = self.retrieve_candidates(search_results, class_name, chip_names)
        
        # Aggregate by image
        grouped = self.aggregate_by_image(detections)
        
        # Filter top-K per image
        grouped_filtered = self.filter_top_k_per_image(grouped)
        
        # Flatten back to list
        all_detections = []
        for dets in grouped_filtered.values():
            all_detections.extend(dets)
        
        return all_detections, grouped_filtered


def compute_iou(box1: Tuple[int, int, int, int], box2: Tuple[int, int, int, int]) -> float:
    """
    Compute IoU between two bounding boxes
    
    Args:
        box1: (x_min, y_min, x_max, y_max)
        box2: (x_min, y_min, x_max, y_max)
        
    Returns:
        IoU score
    """
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2
    
    # Intersection
    xi_min = max(x1_min, x2_min)
    yi_min = max(y1_min, y2_min)
    xi_max = min(x1_max, x2_max)
    yi_max = min(y1_max, y2_max)
    
    if xi_max <= xi_min or yi_max <= yi_min:
        return 0.0
    
    intersection = (xi_max - xi_min) * (yi_max - yi_min)
    
    # Union
    area1 = (x1_max - x1_min) * (y1_max - y1_min)
    area2 = (x2_max - x2_min) * (y2_max - y2_min)
    union = area1 + area2 - intersection
    
    if union == 0:
        return 0.0
    
    return intersection / union


def cluster_detections(
    detections: List[Detection],
    iou_threshold: float = 0.5
) -> List[List[Detection]]:
    """
    Cluster overlapping detections
    
    Args:
        detections: List of Detection objects
        iou_threshold: IoU threshold for clustering
        
    Returns:
        List of clusters (each cluster is a list of detections)
    """
    if not detections:
        return []
    
    # Sort by score descending
    sorted_dets = sorted(detections, key=lambda d: d.score, reverse=True)
    
    clusters = []
    used = set()
    
    for i, det in enumerate(sorted_dets):
        if i in used:
            continue
        
        # Start new cluster
        cluster = [det]
        used.add(i)
        
        box1 = (det.x_min, det.y_min, det.x_max, det.y_max)
        
        # Find overlapping detections
        for j in range(i + 1, len(sorted_dets)):
            if j in used:
                continue
            
            other = sorted_dets[j]
            box2 = (other.x_min, other.y_min, other.x_max, other.y_max)
            
            if compute_iou(box1, box2) >= iou_threshold:
                cluster.append(other)
                used.add(j)
        
        clusters.append(cluster)
    
    return clusters


def merge_cluster(cluster: List[Detection]) -> Detection:
    """
    Merge a cluster of detections into single detection
    Uses weighted average for box coordinates
    
    Args:
        cluster: List of Detection objects
        
    Returns:
        Merged Detection
    """
    if len(cluster) == 1:
        return cluster[0]
    
    # Compute weighted average
    total_score = sum(d.score for d in cluster)
    
    x_min = sum(d.x_min * d.score for d in cluster) / total_score
    y_min = sum(d.y_min * d.score for d in cluster) / total_score
    x_max = sum(d.x_max * d.score for d in cluster) / total_score
    y_max = sum(d.y_max * d.score for d in cluster) / total_score
    
    # Take max score
    max_score = max(d.score for d in cluster)
    
    # Use first detection's metadata
    merged = Detection(
        x_min=int(x_min),
        y_min=int(y_min),
        x_max=int(x_max),
        y_max=int(y_max),
        score=max_score,
        class_name=cluster[0].class_name,
        target_filename=cluster[0].target_filename,
        metadata=cluster[0].metadata
    )
    
    return merged
