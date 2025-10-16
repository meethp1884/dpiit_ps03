"""
Train embedder on training set
"""

import argparse
import yaml
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.train import train_embedder_from_config


def main():
    parser = argparse.ArgumentParser(description='Train embedder model')
    parser.add_argument('--data', type=str, required=True,
                       help='Path to training images directory')
    parser.add_argument('--config', type=str, default='configs/default.yaml',
                       help='Path to config file')
    parser.add_argument('--checkpoint-dir', type=str, default=None,
                       help='Directory to save checkpoints (overrides config)')
    parser.add_argument('--epochs', type=int, default=None,
                       help='Number of epochs (overrides config)')
    parser.add_argument('--device', type=str, default=None,
                       help='Device (cuda/cpu), overrides config')
    parser.add_argument('--pattern', type=str, default='*.tif',
                       help='File pattern for images')
    
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Override config with CLI args
    if args.checkpoint_dir:
        config['training']['checkpoint_dir'] = args.checkpoint_dir
    if args.epochs:
        config['training']['num_epochs'] = args.epochs
    if args.device:
        config['system']['device'] = args.device
    
    # Get image paths
    data_dir = Path(args.data)
    if not data_dir.exists():
        print(f"ERROR: Data directory not found: {data_dir}")
        return
    
    image_paths = sorted(data_dir.glob(args.pattern))
    image_paths = [str(p) for p in image_paths]
    
    if not image_paths:
        print(f"ERROR: No images found in {data_dir} with pattern {args.pattern}")
        return
    
    print(f"Found {len(image_paths)} training images")
    print(f"Config: {args.config}")
    print(f"Device: {config['system']['device']}")
    print(f"Epochs: {config['training']['num_epochs']}")
    print(f"Checkpoint dir: {config['training']['checkpoint_dir']}")
    
    # Train
    print("\nStarting training...")
    trainer = train_embedder_from_config(config, image_paths)
    
    print("\n✓ Training complete!")
    print(f"  Best loss: {trainer.best_loss:.4f}")
    print(f"  Checkpoints saved to: {config['training']['checkpoint_dir']}")


if __name__ == '__main__':
    main()
