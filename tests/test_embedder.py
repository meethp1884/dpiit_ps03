"""
Unit tests for CNN embedder
"""

import pytest
import torch
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.embedder import Embedder, get_embedder, CustomCNN, ResNetBackbone, extract_embeddings


def test_custom_cnn_forward():
    """Test CustomCNN forward pass"""
    model = CustomCNN(in_channels=4, embedding_dim=256)
    model.eval()
    
    # Create dummy input
    x = torch.randn(2, 4, 384, 384)
    
    # Forward
    output = model(x)
    
    assert output.shape == (2, 256)


def test_resnet_backbone_forward():
    """Test ResNet backbone forward pass"""
    model = ResNetBackbone(architecture='resnet18', in_channels=4, embedding_dim=256)
    model.eval()
    
    x = torch.randn(2, 4, 384, 384)
    output = model(x)
    
    assert output.shape == (2, 256)


def test_embedder_normalization():
    """Test embedder with L2 normalization"""
    embedder = Embedder(architecture='custom_cnn', in_channels=4, embedding_dim=256, normalize=True)
    embedder.eval()
    
    x = torch.randn(2, 4, 384, 384)
    
    with torch.no_grad():
        output = embedder(x)
    
    # Check normalization
    norms = torch.norm(output, p=2, dim=1)
    assert torch.allclose(norms, torch.ones_like(norms), atol=1e-5)


def test_embedder_without_normalization():
    """Test embedder without normalization"""
    embedder = Embedder(architecture='custom_cnn', in_channels=4, embedding_dim=256, normalize=False)
    embedder.eval()
    
    x = torch.randn(2, 4, 384, 384)
    
    with torch.no_grad():
        output = embedder(x)
    
    assert output.shape == (2, 256)
    # Norms should not be 1
    norms = torch.norm(output, p=2, dim=1)
    assert not torch.allclose(norms, torch.ones_like(norms), atol=1e-5)


def test_get_embedder_factory():
    """Test embedder factory function"""
    embedder = get_embedder(
        architecture='resnet18',
        in_channels=4,
        embedding_dim=256,
        device='cpu'
    )
    
    assert isinstance(embedder, Embedder)
    
    # Test forward
    x = torch.randn(1, 4, 384, 384)
    with torch.no_grad():
        output = embedder(x)
    
    assert output.shape == (1, 256)


def test_extract_embeddings_batch():
    """Test batch embedding extraction"""
    embedder = get_embedder(architecture='custom_cnn', device='cpu')
    
    # Create batch of images
    images = np.random.randn(10, 4, 384, 384).astype(np.float32)
    
    embeddings = extract_embeddings(embedder, images, batch_size=4, device='cpu')
    
    assert embeddings.shape == (10, 256)
    assert isinstance(embeddings, np.ndarray)


def test_embedder_different_architectures():
    """Test different embedder architectures"""
    architectures = ['resnet18', 'resnet34', 'custom_cnn']
    
    for arch in architectures:
        embedder = Embedder(architecture=arch, in_channels=4, embedding_dim=256)
        embedder.eval()
        
        x = torch.randn(1, 4, 384, 384)
        
        with torch.no_grad():
            output = embedder(x)
        
        assert output.shape == (1, 256), f"Failed for {arch}"


def test_embedder_variable_input_size():
    """Test embedder with different input sizes"""
    embedder = get_embedder(architecture='resnet18', device='cpu')
    
    sizes = [256, 384, 512]
    
    for size in sizes:
        x = torch.randn(1, 4, size, size)
        
        with torch.no_grad():
            output = embedder(x)
        
        assert output.shape == (1, 256), f"Failed for size {size}"
