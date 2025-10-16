"""
FAISS index management for fast similarity search
Supports flat (exact) and IVF (approximate) indexes
"""

import numpy as np
import faiss
import pickle
from pathlib import Path
from typing import Tuple, Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class FAISSIndex:
    """
    FAISS index wrapper for embedding search
    """
    
    def __init__(
        self,
        embedding_dim: int,
        index_type: str = 'Flat',
        metric: str = 'cosine',
        nlist: int = 100,
        nprobe: int = 10
    ):
        """
        Args:
            embedding_dim: Dimension of embeddings
            index_type: 'Flat' (exact) or 'IVF' (approximate)
            metric: 'cosine' or 'l2'
            nlist: Number of clusters for IVF (ignored for Flat)
            nprobe: Number of clusters to search (IVF only)
        """
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.metric = metric
        self.nlist = nlist
        self.nprobe = nprobe
        
        # Create index
        self.index = self._create_index()
        
        # Metadata storage
        self.tile_metadata: List[Dict] = []  # Stores tile info for each vector
        self.is_trained = False
    
    def _create_index(self) -> faiss.Index:
        """Create FAISS index based on configuration"""
        
        if self.metric == 'cosine':
            # For cosine similarity, use inner product with normalized vectors
            if self.index_type == 'Flat':
                index = faiss.IndexFlatIP(self.embedding_dim)
            elif self.index_type == 'IVF':
                quantizer = faiss.IndexFlatIP(self.embedding_dim)
                index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, self.nlist)
            else:
                raise ValueError(f"Unknown index type: {self.index_type}")
        
        elif self.metric == 'l2':
            if self.index_type == 'Flat':
                index = faiss.IndexFlatL2(self.embedding_dim)
            elif self.index_type == 'IVF':
                quantizer = faiss.IndexFlatL2(self.embedding_dim)
                index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, self.nlist)
            else:
                raise ValueError(f"Unknown index type: {self.index_type}")
        
        else:
            raise ValueError(f"Unknown metric: {self.metric}")
        
        return index
    
    def train(self, vectors: np.ndarray):
        """
        Train index (required for IVF)
        
        Args:
            vectors: Training vectors of shape (N, D)
        """
        if self.index_type == 'IVF' and not self.is_trained:
            logger.info(f"Training IVF index with {len(vectors)} vectors...")
            vectors = self._prepare_vectors(vectors)
            self.index.train(vectors)
            self.is_trained = True
            logger.info("Index training complete")
    
    def add(
        self,
        vectors: np.ndarray,
        metadata: Optional[List[Dict]] = None
    ):
        """
        Add vectors to index
        
        Args:
            vectors: Embeddings of shape (N, D)
            metadata: List of dicts with tile metadata (image_id, x, y, etc.)
        """
        vectors = self._prepare_vectors(vectors)
        
        # Train if needed
        if self.index_type == 'IVF' and not self.is_trained:
            self.train(vectors)
        
        # Add to index
        self.index.add(vectors)
        
        # Store metadata
        if metadata:
            self.tile_metadata.extend(metadata)
        else:
            # Create default metadata
            start_idx = len(self.tile_metadata)
            for i in range(len(vectors)):
                self.tile_metadata.append({'index': start_idx + i})
        
        logger.info(f"Added {len(vectors)} vectors. Total: {self.index.ntotal}")
    
    def search(
        self,
        query_vectors: np.ndarray,
        k: int = 100
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for nearest neighbors
        
        Args:
            query_vectors: Query embeddings of shape (N, D)
            k: Number of neighbors to retrieve
            
        Returns:
            Tuple of (distances, indices) both of shape (N, k)
        """
        query_vectors = self._prepare_vectors(query_vectors)
        
        # Set nprobe for IVF
        if self.index_type == 'IVF':
            self.index.nprobe = self.nprobe
        
        distances, indices = self.index.search(query_vectors, k)
        
        return distances, indices
    
    def search_with_metadata(
        self,
        query_vectors: np.ndarray,
        k: int = 100
    ) -> List[List[Dict]]:
        """
        Search and return results with metadata
        
        Args:
            query_vectors: Query embeddings of shape (N, D)
            k: Number of neighbors
            
        Returns:
            List of lists of dicts, each containing {'score', 'metadata'}
        """
        distances, indices = self.search(query_vectors, k)
        
        results = []
        for i in range(len(query_vectors)):
            query_results = []
            for j in range(k):
                idx = indices[i, j]
                if idx < 0 or idx >= len(self.tile_metadata):
                    continue
                
                score = float(distances[i, j])
                # Convert distance to similarity if using cosine
                if self.metric == 'cosine':
                    similarity = score  # Already inner product (cosine for normalized)
                else:
                    # L2 distance to similarity
                    similarity = 1.0 / (1.0 + score)
                
                query_results.append({
                    'score': similarity,
                    'distance': score,
                    'metadata': self.tile_metadata[idx]
                })
            results.append(query_results)
        
        return results
    
    def _prepare_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Ensure vectors are in correct format (contiguous float32)"""
        if not vectors.flags['C_CONTIGUOUS']:
            vectors = np.ascontiguousarray(vectors)
        if vectors.dtype != np.float32:
            vectors = vectors.astype(np.float32)
        return vectors
    
    def save(self, directory: str, name: str = 'faiss_index'):
        """
        Save index and metadata
        
        Args:
            directory: Directory to save to
            name: Base name for files
        """
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Save index
        index_path = Path(directory) / f"{name}.index"
        faiss.write_index(self.index, str(index_path))
        
        # Save metadata
        metadata_path = Path(directory) / f"{name}_metadata.pkl"
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'tile_metadata': self.tile_metadata,
                'embedding_dim': self.embedding_dim,
                'index_type': self.index_type,
                'metric': self.metric,
                'nlist': self.nlist,
                'nprobe': self.nprobe,
                'is_trained': self.is_trained
            }, f)
        
        logger.info(f"Saved index to {directory}")
    
    @classmethod
    def load(cls, directory: str, name: str = 'faiss_index') -> 'FAISSIndex':
        """
        Load index from disk
        
        Args:
            directory: Directory containing index files
            name: Base name of files
            
        Returns:
            FAISSIndex instance
        """
        # Load metadata
        metadata_path = Path(directory) / f"{name}_metadata.pkl"
        with open(metadata_path, 'rb') as f:
            data = pickle.load(f)
        
        # Create instance
        instance = cls(
            embedding_dim=data['embedding_dim'],
            index_type=data['index_type'],
            metric=data['metric'],
            nlist=data['nlist'],
            nprobe=data['nprobe']
        )
        
        # Load index
        index_path = Path(directory) / f"{name}.index"
        instance.index = faiss.read_index(str(index_path))
        instance.tile_metadata = data['tile_metadata']
        instance.is_trained = data['is_trained']
        
        logger.info(f"Loaded index from {directory} with {instance.index.ntotal} vectors")
        
        return instance
    
    def reset(self):
        """Reset index (clear all vectors)"""
        self.index = self._create_index()
        self.tile_metadata = []
        self.is_trained = False
    
    @property
    def ntotal(self) -> int:
        """Number of vectors in index"""
        return self.index.ntotal
