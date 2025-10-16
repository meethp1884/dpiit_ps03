"""
Zero-mean Normalized Cross-Correlation (ZNCC) scorer
Baseline verification method for multispectral imagery
"""

import numpy as np
import cv2
from typing import Tuple, List
from .candidate import Detection


class ZNCC:
    """
    Zero-mean Normalized Cross-Correlation scorer
    Computes similarity between chip and image region across multiple bands
    """
    
    def __init__(self, method: str = 'opencv'):
        """
        Args:
            method: 'opencv' (fast) or 'numpy' (explicit)
        """
        self.method = method
    
    def compute(
        self,
        chip: np.ndarray,
        image: np.ndarray,
        x: int,
        y: int
    ) -> float:
        """
        Compute ZNCC score between chip and image region
        
        Args:
            chip: Query chip of shape (C, H, W)
            image: Target image of shape (C, H', W')
            x: Top-left x coordinate in image
            y: Top-left y coordinate in image
            
        Returns:
            ZNCC score (higher is better, range approximately [-1, 1])
        """
        if chip.ndim == 2:
            chip = chip[np.newaxis, :, :]
        if image.ndim == 2:
            image = image[np.newaxis, :, :]
        
        C, H, W = chip.shape
        _, img_h, img_w = image.shape
        
        # Extract region from image
        y_end = min(y + H, img_h)
        x_end = min(x + W, img_w)
        region = image[:, y:y_end, x:x_end]
        
        # Ensure same size
        if region.shape[1] != H or region.shape[2] != W:
            # Pad or crop
            region = self._match_size(region, (C, H, W))
        
        # Compute ZNCC per band and average
        scores = []
        for c in range(C):
            score = self._zncc_single_band(chip[c], region[c])
            scores.append(score)
        
        # Average across bands
        mean_score = np.mean(scores)
        
        return float(mean_score)
    
    def _zncc_single_band(self, template: np.ndarray, image: np.ndarray) -> float:
        """
        Compute ZNCC for single band
        
        Args:
            template: Template array (H, W)
            image: Image array (H, W)
            
        Returns:
            ZNCC score
        """
        if self.method == 'opencv':
            # Use OpenCV's matchTemplate
            result = cv2.matchTemplate(
                image.astype(np.float32),
                template.astype(np.float32),
                cv2.TM_CCOEFF_NORMED
            )
            return float(result.max())
        
        else:
            # Numpy implementation
            template = template.astype(np.float64)
            image = image.astype(np.float64)
            
            # Zero-mean
            template_zm = template - template.mean()
            image_zm = image - image.mean()
            
            # Normalize
            template_norm = np.sqrt(np.sum(template_zm ** 2))
            image_norm = np.sqrt(np.sum(image_zm ** 2))
            
            if template_norm == 0 or image_norm == 0:
                return 0.0
            
            # Cross-correlation
            score = np.sum(template_zm * image_zm) / (template_norm * image_norm)
            
            return float(score)
    
    def _match_size(self, region: np.ndarray, target_shape: Tuple[int, int, int]) -> np.ndarray:
        """Resize region to match target shape"""
        C, H, W = target_shape
        c, h, w = region.shape
        
        if h < H or w < W:
            # Pad
            pad_h = max(0, H - h)
            pad_w = max(0, W - w)
            region = np.pad(region, ((0, 0), (0, pad_h), (0, pad_w)), mode='reflect')
        
        if h > H or w > W:
            # Crop
            region = region[:, :H, :W]
        
        return region
    
    def score_detections(
        self,
        detections: List[Detection],
        chip: np.ndarray,
        image: np.ndarray
    ) -> List[Detection]:
        """
        Add ZNCC scores to detections
        
        Args:
            detections: List of Detection objects
            chip: Query chip (C, H, W)
            image: Target image (C, H, W)
            
        Returns:
            Detections with updated scores (stored in metadata)
        """
        for det in detections:
            zncc_score = self.compute(chip, image, det.x_min, det.y_min)
            
            # Store in metadata
            if det.metadata is None:
                det.metadata = {}
            det.metadata['zncc_score'] = zncc_score
        
        return detections
    
    def combine_scores(
        self,
        detections: List[Detection],
        embedder_weight: float = 0.7,
        zncc_weight: float = 0.3
    ) -> List[Detection]:
        """
        Combine embedder and ZNCC scores
        
        Args:
            detections: Detections with embedder scores and zncc_score in metadata
            embedder_weight: Weight for embedder score
            zncc_weight: Weight for ZNCC score
            
        Returns:
            Detections with combined scores
        """
        for det in detections:
            embedder_score = det.score
            zncc_score = det.metadata.get('zncc_score', 0.0) if det.metadata else 0.0
            
            # Normalize ZNCC to [0, 1] (from [-1, 1])
            zncc_norm = (zncc_score + 1) / 2
            
            # Combine
            combined = embedder_weight * embedder_score + zncc_weight * zncc_norm
            det.score = combined
            
            # Store original scores
            if det.metadata is None:
                det.metadata = {}
            det.metadata['embedder_score'] = embedder_score
            det.metadata['zncc_score_normalized'] = zncc_norm
        
        return detections


def sliding_window_zncc(
    chip: np.ndarray,
    image: np.ndarray,
    stride: int = 32,
    threshold: float = 0.7
) -> List[Tuple[int, int, float]]:
    """
    Sliding window ZNCC search (fallback method without embeddings)
    
    Args:
        chip: Query chip (C, H, W)
        image: Target image (C, H, W)
        stride: Stride for sliding window
        threshold: Minimum ZNCC score
        
    Returns:
        List of (x, y, score) tuples
    """
    zncc = ZNCC()
    
    if chip.ndim == 2:
        chip = chip[np.newaxis, :, :]
    if image.ndim == 2:
        image = image[np.newaxis, :, :]
    
    C, chip_h, chip_w = chip.shape
    _, img_h, img_w = image.shape
    
    matches = []
    
    for y in range(0, img_h - chip_h + 1, stride):
        for x in range(0, img_w - chip_w + 1, stride):
            score = zncc.compute(chip, image, x, y)
            
            if score >= threshold:
                matches.append((x, y, score))
    
    return matches
