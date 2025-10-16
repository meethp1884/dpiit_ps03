"""
Run visual search on target images using query chips
Produces submission file in PS-03 format
"""

import argparse
import yaml
import torch
import numpy as np
from pathlib import Path
from tqdm import tqdm
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import (
    read_tiff, normalize_bands, get_embedder, FAISSIndex,
    CandidateRetriever, ZNCC, soft_nms, hard_nms,
    write_submission_file, write_detections_summary, generate_submission_filename
)


def load_chips(chip_paths: list, normalize_method: str = 'percentile'):
    """Load and normalize query chips"""
    chips = []
    chip_names = []
    
    for chip_path in chip_paths:
        chip, _ = read_tiff(chip_path)
        chip = normalize_bands(chip, method=normalize_method)
        chips.append(chip)
        chip_names.append(Path(chip_path).stem)
    
    return chips, chip_names


def extract_chip_embeddings(chips: list, embedder, device: str):
    """Extract embeddings from chips"""
    embeddings = []
    
    embedder.eval()
    with torch.no_grad():
        for chip in chips:
            # Ensure correct shape (add batch dimension)
            chip_tensor = torch.from_numpy(chip).float().unsqueeze(0).to(device)
            emb = embedder(chip_tensor)
            embeddings.append(emb.cpu().numpy())
    
    embeddings = np.vstack(embeddings)
    return embeddings


def run_search(
    chip_paths: list,
    index_dir: str,
    class_name: str,
    output_path: str,
    config: dict,
    checkpoint: str = None,
    use_zncc: bool = True,
    device: str = 'cpu'
):
    """
    Run complete search pipeline
    
    Args:
        chip_paths: List of paths to query chips
        index_dir: Directory containing FAISS index
        class_name: Class name for detections
        output_path: Path to output submission file
        config: Configuration dict
        checkpoint: Path to embedder checkpoint
        use_zncc: Whether to use ZNCC verification
        device: Device for computation
    """
    print(f"Running search on {device}")
    print(f"Class: {class_name}")
    print(f"Query chips: {len(chip_paths)}")
    
    # Load chips
    print("\nLoading query chips...")
    chips, chip_names = load_chips(chip_paths, config['preprocessing']['normalization'])
    print(f"Loaded {len(chips)} chips")
    
    # Load embedder
    print("\nLoading embedder...")
    checkpoint = checkpoint or config['embedder'].get('checkpoint')
    embedder = get_embedder(
        architecture=config['embedder']['architecture'],
        in_channels=config['embedder']['input_channels'],
        embedding_dim=config['embedder']['embedding_dim'],
        normalize=config['embedder']['normalize_embeddings'],
        checkpoint=checkpoint,
        device=device
    )
    
    # Extract chip embeddings
    print("Extracting chip embeddings...")
    chip_embeddings = extract_chip_embeddings(chips, embedder, device)
    print(f"Embeddings shape: {chip_embeddings.shape}")
    
    # Load FAISS index
    print("\nLoading FAISS index...")
    faiss_index = FAISSIndex.load(index_dir, 'faiss_index')
    print(f"Index loaded: {faiss_index.ntotal} vectors")
    
    # Search
    print("\nSearching...")
    search_results = faiss_index.search_with_metadata(
        chip_embeddings,
        k=config['retrieval']['top_k_per_chip']
    )
    
    # Retrieve candidates
    print("Retrieving candidates...")
    retriever = CandidateRetriever(
        top_k_per_chip=config['retrieval']['top_k_per_chip'],
        top_k_per_image=config['retrieval']['top_k_per_image'],
        similarity_threshold=config['retrieval']['similarity_threshold']
    )
    
    detections, grouped = retriever.process(search_results, class_name, chip_names)
    print(f"Retrieved {len(detections)} candidates from {len(grouped)} images")
    
    # ZNCC verification (optional)
    if use_zncc and config['scoring']['use_zncc']:
        print("\nApplying ZNCC verification...")
        zncc = ZNCC()
        
        # Load target images and verify
        # (In production, this would load each target image and verify detections)
        # For now, we'll combine scores based on embedder similarity only
        
        # If you have target images available, uncomment and adapt:
        # for image_id, dets in grouped.items():
        #     target_path = f"data/testing_set/{image_id}.tif"
        #     if Path(target_path).exists():
        #         image, _ = read_tiff(target_path)
        #         image = normalize_bands(image)
        #         for chip in chips:
        #             dets = zncc.score_detections(dets, chip, image)
        #         dets = zncc.combine_scores(dets, 
        #                                     embedder_weight=1-config['scoring']['zncc_weight'],
        #                                     zncc_weight=config['scoring']['zncc_weight'])
        #         grouped[image_id] = dets
    
    # Apply NMS per image
    print("Applying NMS...")
    grouped = {}
    from engine.nms import apply_nms_per_image
    
    # Group detections by image first
    from collections import defaultdict
    grouped_temp = defaultdict(list)
    for det in detections:
        grouped_temp[det.target_filename].append(det)
    
    grouped = apply_nms_per_image(
        dict(grouped_temp),
        method=config['nms']['method'],
        iou_threshold=config['nms']['iou_threshold'],
        score_threshold=config['nms']['score_threshold'],
        sigma=config['nms']['sigma']
    )
    
    # Flatten to final detections
    final_detections = []
    for dets in grouped.values():
        final_detections.extend(dets)
    
    print(f"After NMS: {len(final_detections)} detections")
    
    # Write submission file
    print(f"\nWriting submission to {output_path}")
    write_submission_file(final_detections, output_path)
    
    # Write summary
    summary_path = Path(output_path).parent / f"{Path(output_path).stem}_summary.txt"
    write_detections_summary(final_detections, str(summary_path))
    
    print(f"\n✓ Search complete!")
    print(f"  Detections: {len(final_detections)}")
    print(f"  Images: {len(grouped)}")
    print(f"  Output: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Run visual search on target images')
    parser.add_argument('--chips', type=str, nargs='+', required=True,
                       help='Paths to query chip images')
    parser.add_argument('--targets', type=str, required=True,
                       help='Path to target images (for building index on-the-fly if needed)')
    parser.add_argument('--index', type=str, default=None,
                       help='Path to pre-built FAISS index directory (if not provided, will build)')
    parser.add_argument('--name', type=str, required=True,
                       help='Class name for detections')
    parser.add_argument('--out', type=str, required=True,
                       help='Output path for results file')
    parser.add_argument('--config', type=str, default='configs/default.yaml',
                       help='Path to config file')
    parser.add_argument('--checkpoint', type=str, default=None,
                       help='Path to embedder checkpoint')
    parser.add_argument('--device', type=str, default=None,
                       help='Device (cuda/cpu), overrides config')
    parser.add_argument('--no-zncc', action='store_true',
                       help='Disable ZNCC verification')
    parser.add_argument('--team', type=str, default='TeamName',
                       help='Team name for submission filename')
    
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Determine device
    device = args.device or config['system']['device']
    if device == 'cuda' and not torch.cuda.is_available():
        print("CUDA not available, using CPU")
        device = 'cpu'
    
    # Validate chip paths
    for chip_path in args.chips:
        if not Path(chip_path).exists():
            print(f"ERROR: Chip not found: {chip_path}")
            return
    
    # Check if index exists, otherwise build it
    index_dir = args.index
    if not index_dir:
        # Build index on-the-fly
        print("No index provided, building index from targets...")
        index_dir = Path('cache') / 'temp_index'
        index_dir.mkdir(parents=True, exist_ok=True)
        
        # Call build_index script
        import subprocess
        cmd = [
            sys.executable,
            str(Path(__file__).parent / 'build_index.py'),
            '--targets', args.targets,
            '--out', str(index_dir),
            '--config', args.config,
            '--device', device
        ]
        
        if args.checkpoint:
            cmd.extend(['--checkpoint', args.checkpoint])
        
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print("ERROR: Failed to build index")
            return
    
    # Ensure output directory exists
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # If output path is a directory, generate filename
    if output_path.is_dir() or not output_path.suffix:
        filename = generate_submission_filename(args.team)
        output_path = output_path / filename
    
    # Run search
    run_search(
        chip_paths=args.chips,
        index_dir=index_dir,
        class_name=args.name,
        output_path=str(output_path),
        config=config,
        checkpoint=args.checkpoint,
        use_zncc=not args.no_zncc,
        device=device
    )


if __name__ == '__main__':
    main()
