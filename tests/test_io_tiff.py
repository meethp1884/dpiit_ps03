"""
Unit tests for TIFF I/O operations
"""

import pytest
import numpy as np
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.io_tiff import (
    read_tiff, write_tiff, normalize_bands, 
    get_rgb_preview, histogram_match_bands
)


def test_normalize_bands_percentile():
    """Test percentile normalization"""
    # Create test data
    data = np.random.rand(4, 100, 100).astype(np.float32) * 1000
    
    normalized = normalize_bands(data, method='percentile', percentiles=(2, 98))
    
    # Check output shape
    assert normalized.shape == data.shape
    
    # Check range is approximately [0, 1]
    assert normalized.min() >= -0.1
    assert normalized.max() <= 1.1


def test_normalize_bands_minmax():
    """Test min-max normalization"""
    data = np.random.rand(4, 100, 100).astype(np.float32) * 1000
    
    normalized = normalize_bands(data, method='minmax')
    
    assert normalized.shape == data.shape
    assert normalized.min() >= 0
    assert normalized.max() <= 1


def test_normalize_bands_standard():
    """Test standard normalization"""
    data = np.random.rand(4, 100, 100).astype(np.float32) * 1000
    
    normalized = normalize_bands(data, method='standard')
    
    assert normalized.shape == data.shape
    # Standard normalization should have mean ~0 and std ~1
    assert abs(normalized.mean()) < 1.0
    assert abs(normalized.std() - 1.0) < 0.5


def test_get_rgb_preview():
    """Test RGB preview extraction"""
    # 4-band image (B, G, R, NIR)
    data = np.random.rand(4, 200, 200).astype(np.float32) * 1000
    
    rgb = get_rgb_preview(data, bands=(2, 1, 0))  # R, G, B
    
    # Check output
    assert rgb.shape == (200, 200, 3)
    assert rgb.dtype == np.uint8
    assert rgb.min() >= 0
    assert rgb.max() <= 255


def test_get_rgb_preview_single_band():
    """Test RGB preview from single band"""
    data = np.random.rand(100, 100).astype(np.float32) * 1000
    
    rgb = get_rgb_preview(data)
    
    assert rgb.shape == (100, 100, 3)
    assert rgb.dtype == np.uint8


def test_write_read_tiff():
    """Test writing and reading TIFF"""
    # Create test data
    data = np.random.rand(4, 100, 100).astype(np.float32)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "test.tif"
        
        # Write
        write_tiff(str(filepath), data)
        
        # Read
        read_data, metadata = read_tiff(str(filepath))
        
        # Check
        assert read_data.shape == data.shape
        assert metadata['width'] == 100
        assert metadata['height'] == 100
        assert metadata['count'] == 4


def test_histogram_match():
    """Test histogram matching"""
    source = np.random.rand(4, 100, 100).astype(np.float32)
    reference = np.random.rand(4, 100, 100).astype(np.float32) * 2
    
    matched = histogram_match_bands(source, reference)
    
    assert matched.shape == source.shape
    # Matched histogram should be closer to reference
    # (exact test would require more sophisticated comparison)
