"""
TIFF I/O operations for 4-band multispectral imagery
Handles reading, writing, and normalization of B,G,R,NIR bands
"""

import numpy as np
import rasterio
from rasterio.windows import Window
from typing import Tuple, Optional, Union, List
import warnings

warnings.filterwarnings('ignore', category=rasterio.errors.NotGeoreferencedWarning)


def read_tiff(
    filepath: str,
    bands: Optional[List[int]] = None,
    window: Optional[Tuple[int, int, int, int]] = None,
    dtype: str = 'float32'
) -> Tuple[np.ndarray, dict]:
    """
    Read multispectral TIFF file (4 bands: B,G,R,NIR)
    
    Args:
        filepath: Path to TIFF file
        bands: List of band indices to read (1-indexed), None = all bands
        window: (col_off, row_off, width, height) to read subset
        dtype: Output dtype
        
    Returns:
        Tuple of (array, metadata)
        - array: shape (C, H, W) or (H, W) for single band
        - metadata: dict with profile info
    """
    with rasterio.open(filepath) as src:
        # Get metadata
        metadata = {
            'width': src.width,
            'height': src.height,
            'count': src.count,
            'dtype': src.dtypes[0],
            'crs': src.crs,
            'transform': src.transform,
            'bounds': src.bounds,
        }
        
        # Setup window if specified
        rio_window = None
        if window is not None:
            col_off, row_off, width, height = window
            rio_window = Window(col_off, row_off, width, height)
        
        # Read bands
        if bands is None:
            # Read all bands
            data = src.read(window=rio_window)
        else:
            # Read specific bands (rasterio uses 1-indexed bands)
            data = src.read(bands, window=rio_window)
        
        # Convert to desired dtype
        if dtype != str(data.dtype):
            data = data.astype(dtype)
        
        return data, metadata


def write_tiff(
    filepath: str,
    array: np.ndarray,
    metadata: Optional[dict] = None,
    compress: str = 'lzw'
) -> None:
    """
    Write multispectral array to TIFF
    
    Args:
        filepath: Output path
        array: Array of shape (C, H, W) or (H, W)
        metadata: Metadata dict from read_tiff (optional)
        compress: Compression method ('lzw', 'deflate', None)
    """
    # Handle single-band case
    if array.ndim == 2:
        array = array[np.newaxis, :, :]
    
    count, height, width = array.shape
    
    # Setup profile
    profile = {
        'driver': 'GTiff',
        'height': height,
        'width': width,
        'count': count,
        'dtype': array.dtype,
        'compress': compress,
    }
    
    # Add metadata if provided
    if metadata:
        for key in ['crs', 'transform']:
            if key in metadata:
                profile[key] = metadata[key]
    
    # Write
    with rasterio.open(filepath, 'w', **profile) as dst:
        dst.write(array)


def normalize_bands(
    array: np.ndarray,
    method: str = 'percentile',
    percentiles: Tuple[float, float] = (2, 98),
    per_band: bool = True
) -> np.ndarray:
    """
    Normalize multispectral bands
    
    Args:
        array: Shape (C, H, W) or (H, W)
        method: 'percentile', 'minmax', or 'standard'
        percentiles: (lower, upper) percentiles for clipping
        per_band: Normalize each band independently
        
    Returns:
        Normalized array (float32) in range [0, 1] for percentile/minmax
    """
    array = array.astype(np.float32)
    
    if array.ndim == 2:
        array = array[np.newaxis, :, :]
        squeeze = True
    else:
        squeeze = False
    
    C, H, W = array.shape
    result = np.zeros_like(array)
    
    if method == 'percentile':
        if per_band:
            for c in range(C):
                band = array[c]
                p_low, p_high = np.percentile(band, percentiles)
                band_clipped = np.clip(band, p_low, p_high)
                result[c] = (band_clipped - p_low) / (p_high - p_low + 1e-8)
        else:
            p_low, p_high = np.percentile(array, percentiles)
            array_clipped = np.clip(array, p_low, p_high)
            result = (array_clipped - p_low) / (p_high - p_low + 1e-8)
    
    elif method == 'minmax':
        if per_band:
            for c in range(C):
                band = array[c]
                min_val, max_val = band.min(), band.max()
                result[c] = (band - min_val) / (max_val - min_val + 1e-8)
        else:
            min_val, max_val = array.min(), array.max()
            result = (array - min_val) / (max_val - min_val + 1e-8)
    
    elif method == 'standard':
        if per_band:
            for c in range(C):
                band = array[c]
                mean, std = band.mean(), band.std()
                result[c] = (band - mean) / (std + 1e-8)
        else:
            mean, std = array.mean(), array.std()
            result = (array - mean) / (std + 1e-8)
    
    else:
        raise ValueError(f"Unknown normalization method: {method}")
    
    if squeeze:
        result = result.squeeze(0)
    
    return result


def get_rgb_preview(array: np.ndarray, bands: Tuple[int, int, int] = (2, 1, 0)) -> np.ndarray:
    """
    Extract RGB preview from 4-band array (B,G,R,NIR)
    
    Args:
        array: Shape (4, H, W) with bands [B, G, R, NIR]
        bands: Tuple of band indices for (R, G, B) visualization
        
    Returns:
        RGB array shape (H, W, 3) normalized to [0, 255] uint8
    """
    if array.ndim == 2:
        # Single band - return as grayscale RGB
        normalized = normalize_bands(array, method='percentile')
        rgb = np.stack([normalized] * 3, axis=-1)
    else:
        # Multi-band - extract RGB
        r_idx, g_idx, b_idx = bands
        rgb_bands = array[[r_idx, g_idx, b_idx]]  # (3, H, W)
        
        # Normalize
        rgb_normalized = normalize_bands(rgb_bands, method='percentile', per_band=True)
        
        # Transpose to (H, W, 3)
        rgb = np.transpose(rgb_normalized, (1, 2, 0))
    
    # Convert to uint8
    rgb = (rgb * 255).clip(0, 255).astype(np.uint8)
    
    return rgb


def histogram_match_bands(source: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """
    Match histogram of source image to reference image (per band)
    
    Args:
        source: Source array (C, H, W)
        reference: Reference array (C, H, W)
        
    Returns:
        Histogram-matched source array
    """
    from skimage.exposure import match_histograms
    
    if source.ndim == 2:
        source = source[np.newaxis, :]
        reference = reference[np.newaxis, :]
        squeeze = True
    else:
        squeeze = False
    
    # Match per band
    matched = np.zeros_like(source)
    for c in range(source.shape[0]):
        matched[c] = match_histograms(source[c], reference[c])
    
    if squeeze:
        matched = matched.squeeze(0)
    
    return matched
