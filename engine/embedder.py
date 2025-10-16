"""
CNN-based embedder for 4-band multispectral imagery
Produces normalized 256-D descriptors for tile retrieval
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import resnet18, resnet34
from typing import Optional, Literal
import numpy as np


class CustomCNN(nn.Module):
    """Lightweight custom CNN for 4-channel input"""
    
    def __init__(self, in_channels: int = 4, embedding_dim: int = 256):
        super().__init__()
        
        # Encoder
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels, 64, kernel_size=7, stride=2, padding=3, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        )
        
        self.conv2 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True)
        )
        
        self.conv3 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True)
        )
        
        self.conv4 = nn.Sequential(
            nn.Conv2d(256, 512, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True)
        )
        
        # Global pooling and projection
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512, embedding_dim)
    
    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x


class ResNetBackbone(nn.Module):
    """ResNet backbone adapted for 4-channel input"""
    
    def __init__(
        self,
        architecture: Literal['resnet18', 'resnet34'] = 'resnet18',
        in_channels: int = 4,
        embedding_dim: int = 256,
        pretrained: bool = False
    ):
        super().__init__()
        
        # Load ResNet
        if architecture == 'resnet18':
            resnet = resnet18(pretrained=False)
            feature_dim = 512
        elif architecture == 'resnet34':
            resnet = resnet34(pretrained=False)
            feature_dim = 512
        else:
            raise ValueError(f"Unknown architecture: {architecture}")
        
        # Modify first conv layer for 4 channels
        original_conv1 = resnet.conv1
        self.conv1 = nn.Conv2d(
            in_channels,
            original_conv1.out_channels,
            kernel_size=original_conv1.kernel_size,
            stride=original_conv1.stride,
            padding=original_conv1.padding,
            bias=False
        )
        
        # Initialize new conv1 weights
        if pretrained and in_channels == 3:
            # Use pretrained weights for RGB channels
            self.conv1.weight.data = original_conv1.weight.data
        elif in_channels == 4:
            # Average RGB weights for NIR channel or random init
            with torch.no_grad():
                if pretrained:
                    # Copy RGB weights and duplicate for NIR
                    self.conv1.weight.data[:, :3, :, :] = original_conv1.weight.data
                    self.conv1.weight.data[:, 3:4, :, :] = original_conv1.weight.data.mean(dim=1, keepdim=True)
                else:
                    # Kaiming initialization
                    nn.init.kaiming_normal_(self.conv1.weight, mode='fan_out', nonlinearity='relu')
        
        # Copy remaining layers
        self.bn1 = resnet.bn1
        self.relu = resnet.relu
        self.maxpool = resnet.maxpool
        self.layer1 = resnet.layer1
        self.layer2 = resnet.layer2
        self.layer3 = resnet.layer3
        self.layer4 = resnet.layer4
        self.avgpool = resnet.avgpool
        
        # Replace final FC layer
        self.fc = nn.Linear(feature_dim, embedding_dim)
    
    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        
        return x


class Embedder(nn.Module):
    """
    Main embedder class with L2 normalization
    """
    
    def __init__(
        self,
        architecture: str = 'resnet18',
        in_channels: int = 4,
        embedding_dim: int = 256,
        normalize: bool = True,
        pretrained: bool = False
    ):
        super().__init__()
        
        self.normalize = normalize
        
        # Build backbone
        if architecture == 'custom_cnn':
            self.backbone = CustomCNN(in_channels, embedding_dim)
        elif architecture in ['resnet18', 'resnet34']:
            self.backbone = ResNetBackbone(architecture, in_channels, embedding_dim, pretrained)
        else:
            raise ValueError(f"Unknown architecture: {architecture}")
    
    def forward(self, x):
        """
        Args:
            x: Tensor of shape (B, C, H, W)
            
        Returns:
            Embeddings of shape (B, D), L2-normalized if self.normalize=True
        """
        embeddings = self.backbone(x)
        
        if self.normalize:
            embeddings = F.normalize(embeddings, p=2, dim=1)
        
        return embeddings
    
    def embed_batch(self, images: torch.Tensor) -> torch.Tensor:
        """Convenience method for embedding a batch"""
        with torch.no_grad():
            return self.forward(images)
    
    def save(self, path: str):
        """Save model checkpoint"""
        torch.save({
            'state_dict': self.state_dict(),
            'architecture': self.backbone.__class__.__name__,
        }, path)
    
    def load(self, path: str, device: str = 'cpu'):
        """Load model checkpoint"""
        checkpoint = torch.load(path, map_location=device)
        self.load_state_dict(checkpoint['state_dict'])


def get_embedder(
    architecture: str = 'resnet18',
    in_channels: int = 4,
    embedding_dim: int = 256,
    normalize: bool = True,
    checkpoint: Optional[str] = None,
    device: str = 'cpu'
) -> Embedder:
    """
    Factory function to create embedder
    
    Args:
        architecture: 'resnet18', 'resnet34', or 'custom_cnn'
        in_channels: Number of input channels
        embedding_dim: Dimension of output embeddings
        normalize: Whether to L2-normalize embeddings
        checkpoint: Path to checkpoint file (optional)
        device: Device to load model on
        
    Returns:
        Embedder instance
    """
    model = Embedder(
        architecture=architecture,
        in_channels=in_channels,
        embedding_dim=embedding_dim,
        normalize=normalize
    )
    
    if checkpoint:
        model.load(checkpoint, device)
    
    model = model.to(device)
    model.eval()
    
    return model


def extract_embeddings(
    embedder: Embedder,
    images: np.ndarray,
    batch_size: int = 32,
    device: str = 'cpu'
) -> np.ndarray:
    """
    Extract embeddings from a batch of images
    
    Args:
        embedder: Embedder model
        images: Array of shape (N, C, H, W)
        batch_size: Batch size for processing
        device: Device to use
        
    Returns:
        Embeddings array of shape (N, D)
    """
    embedder.eval()
    embeddings_list = []
    
    with torch.no_grad():
        for i in range(0, len(images), batch_size):
            batch = images[i:i + batch_size]
            
            # Convert to tensor
            if isinstance(batch, np.ndarray):
                batch = torch.from_numpy(batch).float()
            
            batch = batch.to(device)
            
            # Extract embeddings
            emb = embedder(batch)
            embeddings_list.append(emb.cpu().numpy())
    
    embeddings = np.vstack(embeddings_list)
    return embeddings
