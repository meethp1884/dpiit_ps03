"""
Build FAISS index from target images
Tiles images and extracts embeddings
"""

import argparse
import yaml
import torch
import numpy as np
from pathlib import Path
from tqdm import tqdm
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import read_tiff, normalize_bands, TileGenerator, get_embedder, FAISSIndex


def build_index_from_images(
    image_paths: list,
    embedder,
    tiler: TileGenerator,
    device: str = 'cpu',
    normalize_method: str = 'percentile'
):
    """
    Build FAISS index from list of images
    
    Args:
        image_paths: List of image paths
        embedder: Embedder model
        tiler: TileGenerator instance
        device: Device for embeddings
        normalize_method: Normalization method
        
    Returns:
        Tuple of (embeddings, metadata, image_ids)
    """
    all_embeddings = []
    all_metadata = []
    
    embedder.eval()
    
    for img_path in tqdm(image_paths, desc='Processing images'):
        img_name = Path(img_path).stem
        
        # Read and normalize
        image, _ = read_tiff(img_path)
        image = normalize_bands(image, method=normalize_method)
        
        # Generate tiles
        tiles = tiler.tile_image(image, image_id=img_name)
        
        if not tiles:
            print(f"Warning: No tiles generated for {img_name}")
            continue
        
        # Extract embeddings in batches
        batch_size = 32
        tile_data = np.stack([t.data for t in tiles])
        
        embeddings = []
        with torch.no_grad():
            for i in range(0, len(tile_data), batch_size):
                batch = tile_data[i:i+batch_size]
                batch_tensor = torch.from_numpy(batch).float().to(device)
                emb = embedder(batch_tensor)
                embeddings.append(emb.cpu().numpy())
        
        embeddings = np.vstack(embeddings)
        
        # Store metadata
        for i, tile in enumerate(tiles):
            metadata = {
                'image_id': img_name,
                'x': tile.x,
                'y': tile.y,
                'width': tile.width,
                'height': tile.height,
                'scale': tile.scale
            }
            all_metadata.append(metadata)
        
        all_embeddings.append(embeddings)
    
    # Concatenate all embeddings
    all_embeddings = np.vstack(all_embeddings)
    
    return all_embeddings, all_metadata


def main():
    parser = argparse.ArgumentParser(description='Build FAISS index from target images')
    parser.add_argument('--targets', type=str, required=True,
                       help='Path to target images directory')
    parser.add_argument('--out', type=str, required=True,
                       help='Output directory for index')
    parser.add_argument('--config', type=str, default='configs/default.yaml',
                       help='Path to config file')
    parser.add_argument('--checkpoint', type=str, default=None,
                       help='Path to embedder checkpoint')
    parser.add_argument('--name', type=str, default='faiss_index',
                       help='Name for index files')
    parser.add_argument('--device', type=str, default=None,
                       help='Device (cuda/cpu), overrides config')
    parser.add_argument('--pattern', type=str, default='*.tif',
                       help='File pattern for images')
    
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Determine device
    device = args.device or config['system']['device']
    if device == 'cuda' and not torch.cuda.is_available():
        print("CUDA not available, using CPU")
        device = 'cpu'
    
    print(f"Building index on {device}")
    
    # Get image paths
    target_dir = Path(args.targets)
    if not target_dir.exists():
        print(f"ERROR: Target directory not found: {target_dir}")
        return
    
    image_paths = sorted(target_dir.glob(args.pattern))
    image_paths = [str(p) for p in image_paths]
    
    if not image_paths:
        print(f"ERROR: No images found in {target_dir} with pattern {args.pattern}")
        return
    
    print(f"Found {len(image_paths)} images")
    
    # Create embedder
    checkpoint = args.checkpoint or config['embedder'].get('checkpoint')
    embedder = get_embedder(
        architecture=config['embedder']['architecture'],
        in_channels=config['embedder']['input_channels'],
        embedding_dim=config['embedder']['embedding_dim'],
        normalize=config['embedder']['normalize_embeddings'],
        checkpoint=checkpoint,
        device=device
    )
    
    print(f"Loaded embedder: {config['embedder']['architecture']}")
    
    # Create tiler
    tiler = TileGenerator(
        tile_size=config['tiler']['tile_size'],
        stride=config['tiler']['stride'],
        scales=config['tiler']['scales']
    )
    
    # Build embeddings
    print("Extracting embeddings...")
    embeddings, metadata = build_index_from_images(
        image_paths,
        embedder,
        tiler,
        device=device,
        normalize_method=config['preprocessing']['normalization']
    )
    
    print(f"Extracted {len(embeddings)} tile embeddings")
    
    # Create FAISS index
    print("Building FAISS index...")
    faiss_index = FAISSIndex(
        embedding_dim=config['embedder']['embedding_dim'],
        index_type=config['faiss']['index_type'],
        metric=config['faiss']['metric'],
        nlist=config['faiss']['nlist'],
        nprobe=config['faiss']['nprobe']
    )
    
    faiss_index.add(embeddings, metadata)
    
    # Save index
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)
    faiss_index.save(str(output_dir), args.name)
    
    print(f"\n✓ Index saved to {output_dir}/{args.name}")
    print(f"  Total vectors: {faiss_index.ntotal}")
    print(f"  Unique images: {len(set(m['image_id'] for m in metadata))}")


if __name__ == '__main__':
    main()
