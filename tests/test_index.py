"""
Unit tests for FAISS index
"""

import pytest
import numpy as np
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.index_faiss import FAISSIndex


def test_faiss_index_flat():
    """Test flat FAISS index"""
    index = FAISSIndex(embedding_dim=256, index_type='Flat', metric='cosine')
    
    # Add vectors
    vectors = np.random.randn(100, 256).astype(np.float32)
    metadata = [{'id': i} for i in range(100)]
    
    index.add(vectors, metadata)
    
    assert index.ntotal == 100
    assert len(index.tile_metadata) == 100


def test_faiss_index_search():
    """Test search functionality"""
    index = FAISSIndex(embedding_dim=128, index_type='Flat', metric='cosine')
    
    # Add vectors
    vectors = np.random.randn(100, 128).astype(np.float32)
    # Normalize for cosine
    vectors = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-8)
    
    metadata = [{'id': i, 'value': f'item_{i}'} for i in range(100)]
    index.add(vectors, metadata)
    
    # Search
    query = vectors[:5]  # Use first 5 as queries
    distances, indices = index.search(query, k=10)
    
    assert distances.shape == (5, 10)
    assert indices.shape == (5, 10)
    
    # First result should be the vector itself (distance ~1.0 for cosine)
    assert indices[0, 0] == 0
    assert distances[0, 0] > 0.99


def test_faiss_index_with_metadata():
    """Test search with metadata retrieval"""
    index = FAISSIndex(embedding_dim=64, index_type='Flat', metric='l2')
    
    vectors = np.random.randn(50, 64).astype(np.float32)
    metadata = [{'id': i, 'x': i*10, 'y': i*20} for i in range(50)]
    
    index.add(vectors, metadata)
    
    # Search with metadata
    query = vectors[:3]
    results = index.search_with_metadata(query, k=5)
    
    assert len(results) == 3
    assert len(results[0]) == 5
    
    # Check metadata structure
    result = results[0][0]
    assert 'score' in result
    assert 'metadata' in result
    assert 'id' in result['metadata']
    assert 'x' in result['metadata']


def test_faiss_index_ivf():
    """Test IVF index (approximate search)"""
    index = FAISSIndex(embedding_dim=128, index_type='IVF', metric='cosine', nlist=10)
    
    # Generate enough vectors for clustering
    vectors = np.random.randn(200, 128).astype(np.float32)
    vectors = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-8)
    
    metadata = [{'id': i} for i in range(200)]
    
    # Train and add
    index.train(vectors)
    index.add(vectors, metadata)
    
    assert index.ntotal == 200
    assert index.is_trained


def test_faiss_index_save_load():
    """Test saving and loading index"""
    index = FAISSIndex(embedding_dim=64, index_type='Flat', metric='cosine')
    
    vectors = np.random.randn(50, 64).astype(np.float32)
    metadata = [{'id': i} for i in range(50)]
    
    index.add(vectors, metadata)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save
        index.save(tmpdir, 'test_index')
        
        # Load
        loaded_index = FAISSIndex.load(tmpdir, 'test_index')
        
        assert loaded_index.ntotal == 50
        assert len(loaded_index.tile_metadata) == 50
        
        # Test search on loaded index
        query = vectors[:5]
        distances, indices = loaded_index.search(query, k=5)
        
        assert distances.shape == (5, 5)
        assert indices.shape == (5, 5)


def test_faiss_index_reset():
    """Test index reset"""
    index = FAISSIndex(embedding_dim=128, index_type='Flat')
    
    vectors = np.random.randn(50, 128).astype(np.float32)
    index.add(vectors)
    
    assert index.ntotal == 50
    
    index.reset()
    
    assert index.ntotal == 0
    assert len(index.tile_metadata) == 0


def test_faiss_index_incremental_add():
    """Test adding vectors incrementally"""
    index = FAISSIndex(embedding_dim=64, index_type='Flat')
    
    # Add in batches
    for i in range(5):
        vectors = np.random.randn(20, 64).astype(np.float32)
        metadata = [{'batch': i, 'id': j} for j in range(20)]
        index.add(vectors, metadata)
    
    assert index.ntotal == 100
    assert len(index.tile_metadata) == 100
