"""
Unit tests for tiling operations
"""

import pytest
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.tiler import TileGenerator, tile_image, reconstruct_from_tiles


def test_tile_generator_basic():
    """Test basic tile generation"""
    image = np.random.rand(4, 1000, 1000).astype(np.float32)
    
    tiler = TileGenerator(tile_size=256, stride=128, scales=[1.0])
    tiles = tiler.tile_image(image, image_id="test")
    
    # Check tiles were generated
    assert len(tiles) > 0
    
    # Check tile properties
    for tile in tiles:
        assert tile.data.shape[0] == 4  # 4 channels
        assert tile.data.shape[1] == 256  # Height
        assert tile.data.shape[2] == 256  # Width
        assert tile.image_id == "test"
        assert tile.scale == 1.0


def test_tile_generator_multiscale():
    """Test multi-scale tiling"""
    image = np.random.rand(4, 800, 800).astype(np.float32)
    
    tiler = TileGenerator(tile_size=256, stride=128, scales=[1.0, 0.5, 1.5])
    tiles = tiler.tile_image(image)
    
    # Should have tiles at multiple scales
    scales = set(tile.scale for tile in tiles)
    assert len(scales) == 3
    assert 1.0 in scales
    assert 0.5 in scales
    assert 1.5 in scales


def test_tile_generator_small_image():
    """Test tiling of small image (padding required)"""
    image = np.random.rand(4, 100, 100).astype(np.float32)
    
    tiler = TileGenerator(tile_size=256, stride=128, scales=[1.0])
    tiles = tiler.tile_image(image)
    
    # Should generate at least one padded tile
    assert len(tiles) >= 1
    assert tiles[0].data.shape[1] == 256
    assert tiles[0].data.shape[2] == 256


def test_tile_image_convenience():
    """Test convenience function"""
    image = np.random.rand(4, 500, 500).astype(np.float32)
    
    tiles = tile_image(image, tile_size=200, stride=100)
    
    assert len(tiles) > 0
    assert tiles[0].data.shape[1] == 200


def test_tile_coordinates():
    """Test tile coordinate mapping"""
    image = np.random.rand(4, 400, 400).astype(np.float32)
    
    tiler = TileGenerator(tile_size=200, stride=200, scales=[1.0])
    tiles = tiler.tile_image(image)
    
    # Check coordinates
    for tile in tiles:
        assert tile.x >= 0
        assert tile.y >= 0
        assert tile.x + tile.width <= 400
        assert tile.y + tile.height <= 400


def test_reconstruct_from_tiles():
    """Test reconstruction from overlapping tiles"""
    image = np.random.rand(4, 400, 400).astype(np.float32)
    
    tiler = TileGenerator(tile_size=200, stride=100, scales=[1.0])
    tiles = tiler.tile_image(image)
    
    # Reconstruct
    reconstructed = reconstruct_from_tiles(tiles, image.shape, aggregation='mean')
    
    assert reconstructed.shape == image.shape


def test_iterator():
    """Test tile iterator"""
    image = np.random.rand(4, 500, 500).astype(np.float32)
    
    tiler = TileGenerator(tile_size=200, stride=100)
    
    count = 0
    for tile in tiler.iter_tiles(image):
        assert tile.data.shape[0] == 4
        assert tile.data.shape[1] == 200
        assert tile.data.shape[2] == 200
        count += 1
    
    assert count > 0
