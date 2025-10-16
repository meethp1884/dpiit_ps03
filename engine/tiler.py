"""
Sliding window tiler for multispectral imagery
Generates overlapping tiles at multiple scales
"""

import numpy as np
from typing import List, Tuple, Iterator, Optional
from dataclasses import dataclass


@dataclass
class Tile:
    """Represents a single tile with metadata"""
    data: np.ndarray  # Shape (C, H, W)
    x: int  # Top-left x coordinate in original image
    y: int  # Top-left y coordinate in original image
    width: int
    height: int
    scale: float = 1.0
    image_id: Optional[str] = None


class TileGenerator:
    """
    Generate overlapping tiles from large images using sliding window
    Supports multi-scale tiling
    """
    
    def __init__(
        self,
        tile_size: int = 384,
        stride: int = 192,
        scales: List[float] = [1.0],
        min_tile_coverage: float = 0.5
    ):
        """
        Args:
            tile_size: Base tile size (pixels)
            stride: Sliding window stride (pixels)
            scales: List of scale factors for multi-scale tiling
            min_tile_coverage: Minimum fraction of tile that must be valid
        """
        self.tile_size = tile_size
        self.stride = stride
        self.scales = scales
        self.min_tile_coverage = min_tile_coverage
    
    def tile_image(
        self,
        image: np.ndarray,
        image_id: Optional[str] = None
    ) -> List[Tile]:
        """
        Generate all tiles from an image
        
        Args:
            image: Array of shape (C, H, W) or (H, W)
            image_id: Optional identifier for the image
            
        Returns:
            List of Tile objects
        """
        if image.ndim == 2:
            image = image[np.newaxis, :, :]
        
        C, H, W = image.shape
        tiles = []
        
        for scale in self.scales:
            # Resize image for this scale
            if scale != 1.0:
                import cv2
                new_h, new_w = int(H * scale), int(W * scale)
                scaled_image = np.zeros((C, new_h, new_w), dtype=image.dtype)
                for c in range(C):
                    scaled_image[c] = cv2.resize(
                        image[c],
                        (new_w, new_h),
                        interpolation=cv2.INTER_LINEAR
                    )
            else:
                scaled_image = image
                new_h, new_w = H, W
            
            # Generate tiles at this scale
            scale_tiles = self._tile_at_scale(
                scaled_image, scale, image_id, orig_h=H, orig_w=W
            )
            tiles.extend(scale_tiles)
        
        return tiles
    
    def _tile_at_scale(
        self,
        image: np.ndarray,
        scale: float,
        image_id: Optional[str],
        orig_h: int,
        orig_w: int
    ) -> List[Tile]:
        """Generate tiles at a specific scale"""
        C, H, W = image.shape
        tiles = []
        
        # Calculate number of tiles
        n_rows = max(1, (H - self.tile_size) // self.stride + 1)
        n_cols = max(1, (W - self.tile_size) // self.stride + 1)
        
        for i in range(n_rows):
            for j in range(n_cols):
                # Calculate tile boundaries
                y = i * self.stride
                x = j * self.stride
                
                # Ensure tile doesn't exceed image bounds
                y_end = min(y + self.tile_size, H)
                x_end = min(x + self.tile_size, W)
                
                # Adjust start if near edge
                if y_end - y < self.tile_size:
                    y = max(0, y_end - self.tile_size)
                if x_end - x < self.tile_size:
                    x = max(0, x_end - self.tile_size)
                
                # Extract tile
                tile_data = image[:, y:y_end, x:x_end]
                
                # Check coverage
                coverage = (tile_data.shape[1] * tile_data.shape[2]) / (self.tile_size ** 2)
                if coverage < self.min_tile_coverage:
                    continue
                
                # Pad if necessary
                if tile_data.shape[1] < self.tile_size or tile_data.shape[2] < self.tile_size:
                    tile_data = self._pad_tile(tile_data, self.tile_size)
                
                # Convert coordinates back to original scale
                orig_x = int(x / scale)
                orig_y = int(y / scale)
                orig_w = int(tile_data.shape[2] / scale)
                orig_h = int(tile_data.shape[1] / scale)
                
                tile = Tile(
                    data=tile_data,
                    x=orig_x,
                    y=orig_y,
                    width=orig_w,
                    height=orig_h,
                    scale=scale,
                    image_id=image_id
                )
                tiles.append(tile)
        
        return tiles
    
    def _pad_tile(self, tile: np.ndarray, target_size: int) -> np.ndarray:
        """Pad tile to target size with reflection"""
        C, H, W = tile.shape
        pad_h = target_size - H
        pad_w = target_size - W
        
        if pad_h > 0 or pad_w > 0:
            padded = np.pad(
                tile,
                ((0, 0), (0, pad_h), (0, pad_w)),
                mode='reflect'
            )
            return padded
        return tile
    
    def iter_tiles(
        self,
        image: np.ndarray,
        image_id: Optional[str] = None
    ) -> Iterator[Tile]:
        """
        Memory-efficient iterator over tiles
        
        Args:
            image: Array of shape (C, H, W) or (H, W)
            image_id: Optional identifier
            
        Yields:
            Tile objects
        """
        tiles = self.tile_image(image, image_id)
        for tile in tiles:
            yield tile


def tile_image(
    image: np.ndarray,
    tile_size: int = 384,
    stride: int = 192,
    scales: List[float] = [1.0]
) -> List[Tile]:
    """
    Convenience function to tile an image
    
    Args:
        image: Input array (C, H, W) or (H, W)
        tile_size: Tile size in pixels
        stride: Stride for sliding window
        scales: List of scale factors
        
    Returns:
        List of Tile objects
    """
    tiler = TileGenerator(tile_size=tile_size, stride=stride, scales=scales)
    return tiler.tile_image(image)


def reconstruct_from_tiles(
    tiles: List[Tile],
    image_shape: Tuple[int, int, int],
    aggregation: str = 'mean'
) -> np.ndarray:
    """
    Reconstruct image from overlapping tiles
    
    Args:
        tiles: List of Tile objects
        image_shape: (C, H, W) of target image
        aggregation: 'mean' or 'max' for overlapping regions
        
    Returns:
        Reconstructed image
    """
    C, H, W = image_shape
    reconstructed = np.zeros((C, H, W), dtype=np.float32)
    counts = np.zeros((H, W), dtype=np.float32)
    
    for tile in tiles:
        y1, y2 = tile.y, tile.y + tile.height
        x1, x2 = tile.x, tile.x + tile.width
        
        # Ensure bounds
        y1, y2 = max(0, y1), min(H, y2)
        x1, x2 = max(0, x1), min(W, x2)
        
        h, w = y2 - y1, x2 - x1
        tile_data = tile.data[:, :h, :w]
        
        if aggregation == 'mean':
            reconstructed[:, y1:y2, x1:x2] += tile_data
            counts[y1:y2, x1:x2] += 1
        elif aggregation == 'max':
            reconstructed[:, y1:y2, x1:x2] = np.maximum(
                reconstructed[:, y1:y2, x1:x2],
                tile_data
            )
    
    if aggregation == 'mean':
        counts[counts == 0] = 1  # Avoid division by zero
        reconstructed = reconstructed / counts[np.newaxis, :, :]
    
    return reconstructed
