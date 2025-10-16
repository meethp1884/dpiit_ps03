"""
PS-03 Visual Search Engine
Core modules for satellite imagery retrieval and detection
"""

__version__ = "1.0.0"

from .io_tiff import read_tiff, write_tiff, normalize_bands
from .tiler import TileGenerator, tile_image
from .embedder import Embedder, get_embedder
from .index_faiss import FAISSIndex
from .candidate import CandidateRetriever
from .verify_ncc import ZNCC
from .nms import soft_nms, hard_nms, merge_detections
from .writer import write_submission_file

__all__ = [
    'read_tiff',
    'write_tiff',
    'normalize_bands',
    'TileGenerator',
    'tile_image',
    'Embedder',
    'get_embedder',
    'FAISSIndex',
    'CandidateRetriever',
    'ZNCC',
    'soft_nms',
    'hard_nms',
    'merge_detections',
    'write_submission_file',
]
