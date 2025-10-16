"""
Training pipeline for embedder with triplet/contrastive loss
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from tqdm import tqdm
import random

from .embedder import Embedder
from .io_tiff import read_tiff, normalize_bands


class TileDataset(Dataset):
    """
    Dataset for training embedder on tiles
    """
    
    def __init__(
        self,
        image_paths: List[str],
        tile_size: int = 384,
        tiles_per_image: int = 10,
        augment: bool = True,
        normalize_method: str = 'percentile'
    ):
        """
        Args:
            image_paths: List of paths to TIFF files
            tile_size: Size of tiles to extract
            tiles_per_image: Number of random tiles per image
            augment: Whether to apply augmentation
            normalize_method: Normalization method
        """
        self.image_paths = image_paths
        self.tile_size = tile_size
        self.tiles_per_image = tiles_per_image
        self.augment = augment
        self.normalize_method = normalize_method
        
        # Create list of (image_idx, tile_idx) pairs
        self.samples = []
        for img_idx in range(len(image_paths)):
            for tile_idx in range(tiles_per_image):
                self.samples.append((img_idx, tile_idx))
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_idx, tile_idx = self.samples[idx]
        
        # Read image
        image, _ = read_tiff(self.image_paths[img_idx])
        image = normalize_bands(image, method=self.normalize_method)
        
        C, H, W = image.shape
        
        # Extract random tile
        if H > self.tile_size and W > self.tile_size:
            y = random.randint(0, H - self.tile_size)
            x = random.randint(0, W - self.tile_size)
            tile = image[:, y:y+self.tile_size, x:x+self.tile_size]
        else:
            # Pad if image is smaller
            tile = self._pad_tile(image, self.tile_size)
        
        # Augment
        if self.augment:
            tile = self._augment(tile)
        
        return torch.from_numpy(tile).float(), img_idx
    
    def _pad_tile(self, image, target_size):
        """Pad image to target size"""
        C, H, W = image.shape
        pad_h = max(0, target_size - H)
        pad_w = max(0, target_size - W)
        
        if pad_h > 0 or pad_w > 0:
            image = np.pad(image, ((0, 0), (0, pad_h), (0, pad_w)), mode='reflect')
        
        return image[:, :target_size, :target_size]
    
    def _augment(self, tile):
        """Apply data augmentation"""
        # Random horizontal flip
        if random.random() < 0.5:
            tile = np.flip(tile, axis=2).copy()
        
        # Random vertical flip
        if random.random() < 0.5:
            tile = np.flip(tile, axis=1).copy()
        
        # Random 90-degree rotation
        if random.random() < 0.3:
            k = random.randint(1, 3)
            tile = np.rot90(tile, k=k, axes=(1, 2)).copy()
        
        # Random brightness/contrast (per band)
        if random.random() < 0.2:
            factor = np.random.uniform(0.8, 1.2, size=(tile.shape[0], 1, 1))
            tile = tile * factor
            tile = np.clip(tile, 0, 1)
        
        return tile


class TripletLoss(nn.Module):
    """
    Triplet loss with online mining
    """
    
    def __init__(self, margin: float = 0.5, mining: str = 'batch_hard'):
        """
        Args:
            margin: Triplet margin
            mining: 'batch_hard', 'batch_all', or 'online'
        """
        super().__init__()
        self.margin = margin
        self.mining = mining
    
    def forward(self, embeddings, labels):
        """
        Args:
            embeddings: Tensor of shape (B, D)
            labels: Tensor of shape (B,)
            
        Returns:
            Loss scalar
        """
        if self.mining == 'batch_hard':
            return self._batch_hard_triplet_loss(embeddings, labels)
        elif self.mining == 'batch_all':
            return self._batch_all_triplet_loss(embeddings, labels)
        else:
            raise ValueError(f"Unknown mining strategy: {self.mining}")
    
    def _batch_hard_triplet_loss(self, embeddings, labels):
        """Batch hard triplet loss"""
        # Compute pairwise distances
        pdist = torch.cdist(embeddings, embeddings, p=2)
        
        # For each anchor, find hardest positive and negative
        mask_pos = labels.unsqueeze(0) == labels.unsqueeze(1)
        mask_neg = labels.unsqueeze(0) != labels.unsqueeze(1)
        
        # Hardest positive: furthest same-class sample
        pdist_pos = pdist.clone()
        pdist_pos[~mask_pos] = 0
        hardest_pos = pdist_pos.max(dim=1)[0]
        
        # Hardest negative: closest different-class sample
        pdist_neg = pdist.clone()
        pdist_neg[~mask_neg] = float('inf')
        hardest_neg = pdist_neg.min(dim=1)[0]
        
        # Triplet loss
        loss = F.relu(hardest_pos - hardest_neg + self.margin)
        return loss.mean()
    
    def _batch_all_triplet_loss(self, embeddings, labels):
        """Batch all triplet loss"""
        pdist = torch.cdist(embeddings, embeddings, p=2)
        
        mask_pos = labels.unsqueeze(0) == labels.unsqueeze(1)
        mask_neg = labels.unsqueeze(0) != labels.unsqueeze(1)
        
        # All valid triplets
        losses = []
        for i in range(len(embeddings)):
            pos_dists = pdist[i][mask_pos[i]]
            neg_dists = pdist[i][mask_neg[i]]
            
            if len(pos_dists) > 0 and len(neg_dists) > 0:
                # All combinations
                triplet_loss = pos_dists.unsqueeze(1) - neg_dists.unsqueeze(0) + self.margin
                triplet_loss = F.relu(triplet_loss)
                losses.append(triplet_loss.mean())
        
        if losses:
            return torch.stack(losses).mean()
        else:
            return torch.tensor(0.0, device=embeddings.device)


class Trainer:
    """
    Training manager for embedder
    """
    
    def __init__(
        self,
        model: Embedder,
        train_loader: DataLoader,
        val_loader: Optional[DataLoader] = None,
        loss_fn: nn.Module = None,
        optimizer: torch.optim.Optimizer = None,
        scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
        device: str = 'cuda',
        checkpoint_dir: str = 'models/checkpoints'
    ):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.loss_fn = loss_fn or TripletLoss()
        self.optimizer = optimizer or torch.optim.Adam(model.parameters(), lr=0.001)
        self.scheduler = scheduler
        self.device = device
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        self.best_loss = float('inf')
        self.history = {'train_loss': [], 'val_loss': []}
    
    def train_epoch(self) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        
        pbar = tqdm(self.train_loader, desc='Training')
        for batch_idx, (images, labels) in enumerate(pbar):
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            # Forward
            embeddings = self.model(images)
            loss = self.loss_fn(embeddings, labels)
            
            # Backward
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            pbar.set_postfix({'loss': loss.item()})
        
        avg_loss = total_loss / len(self.train_loader)
        return avg_loss
    
    def validate(self) -> float:
        """Validate on validation set"""
        if self.val_loader is None:
            return 0.0
        
        self.model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for images, labels in tqdm(self.val_loader, desc='Validation'):
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                embeddings = self.model(images)
                loss = self.loss_fn(embeddings, labels)
                
                total_loss += loss.item()
        
        avg_loss = total_loss / len(self.val_loader)
        return avg_loss
    
    def train(self, num_epochs: int, save_every: int = 5):
        """
        Train for multiple epochs
        
        Args:
            num_epochs: Number of epochs
            save_every: Save checkpoint every N epochs
        """
        print(f"Training for {num_epochs} epochs on {self.device}")
        
        for epoch in range(1, num_epochs + 1):
            print(f"\nEpoch {epoch}/{num_epochs}")
            
            # Train
            train_loss = self.train_epoch()
            self.history['train_loss'].append(train_loss)
            print(f"Train loss: {train_loss:.4f}")
            
            # Validate
            if self.val_loader:
                val_loss = self.validate()
                self.history['val_loss'].append(val_loss)
                print(f"Val loss: {val_loss:.4f}")
            else:
                val_loss = train_loss
            
            # Scheduler step
            if self.scheduler:
                self.scheduler.step()
            
            # Save checkpoint
            if epoch % save_every == 0:
                self.save_checkpoint(f'epoch_{epoch}.pth')
            
            # Save best model
            if val_loss < self.best_loss:
                self.best_loss = val_loss
                self.save_checkpoint('best.pth')
                print(f"✓ Saved best model (loss: {val_loss:.4f})")
        
        print("\nTraining complete!")
        print(f"Best validation loss: {self.best_loss:.4f}")
    
    def save_checkpoint(self, filename: str):
        """Save model checkpoint"""
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'best_loss': self.best_loss,
            'history': self.history
        }
        
        if self.scheduler:
            checkpoint['scheduler_state_dict'] = self.scheduler.state_dict()
        
        path = self.checkpoint_dir / filename
        torch.save(checkpoint, path)
    
    def load_checkpoint(self, filename: str):
        """Load model checkpoint"""
        path = self.checkpoint_dir / filename
        checkpoint = torch.load(path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.best_loss = checkpoint.get('best_loss', float('inf'))
        self.history = checkpoint.get('history', {'train_loss': [], 'val_loss': []})
        
        if self.scheduler and 'scheduler_state_dict' in checkpoint:
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        print(f"Loaded checkpoint from {path}")


def train_embedder_from_config(config: Dict, image_paths: List[str]):
    """
    Convenience function to train embedder from config dict
    
    Args:
        config: Configuration dict
        image_paths: List of training image paths
    """
    # Split train/val
    val_split = config['training'].get('val_split', 0.2)
    n_val = int(len(image_paths) * val_split)
    random.shuffle(image_paths)
    train_paths = image_paths[n_val:]
    val_paths = image_paths[:n_val]
    
    # Create datasets
    train_dataset = TileDataset(
        train_paths,
        tile_size=config['tiler']['tile_size'],
        tiles_per_image=10,
        augment=True
    )
    
    val_dataset = TileDataset(
        val_paths,
        tile_size=config['tiler']['tile_size'],
        tiles_per_image=5,
        augment=False
    )
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=config['training']['batch_size'],
        shuffle=True,
        num_workers=config['system'].get('num_workers', 4),
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config['training']['batch_size'],
        shuffle=False,
        num_workers=config['system'].get('num_workers', 4),
        pin_memory=True
    )
    
    # Create model
    model = Embedder(
        architecture=config['embedder']['architecture'],
        in_channels=config['embedder']['input_channels'],
        embedding_dim=config['embedder']['embedding_dim'],
        normalize=config['embedder']['normalize_embeddings']
    )
    
    # Create optimizer
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=config['training']['learning_rate'],
        weight_decay=config['training']['weight_decay']
    )
    
    # Create scheduler
    scheduler = None
    if config['training']['scheduler'] == 'cosine':
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=config['training']['num_epochs']
        )
    elif config['training']['scheduler'] == 'step':
        scheduler = torch.optim.lr_scheduler.StepLR(
            optimizer,
            step_size=10,
            gamma=0.5
        )
    
    # Create loss
    loss_fn = TripletLoss(
        margin=config['training']['margin'],
        mining=config['training']['mining']
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        loss_fn=loss_fn,
        optimizer=optimizer,
        scheduler=scheduler,
        device=config['system']['device'],
        checkpoint_dir=config['training']['checkpoint_dir']
    )
    
    # Train
    trainer.train(
        num_epochs=config['training']['num_epochs'],
        save_every=config['training']['save_every']
    )
    
    return trainer
