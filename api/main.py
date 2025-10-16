"""
FastAPI backend for PS-03 visual search
Provides endpoints for chip upload, search, and result visualization
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
import yaml
import torch
import numpy as np
from pathlib import Path
import tempfile
import shutil
import uuid
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import (
    read_tiff, write_tiff, normalize_bands, get_rgb_preview,
    get_embedder, FAISSIndex, CandidateRetriever,
    soft_nms, write_submission_file
)

# Initialize FastAPI app
app = FastAPI(title="PS-03 Visual Search API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
CONFIG = None
EMBEDDER = None
FAISS_INDEX = None
TEMP_DIR = Path(tempfile.gettempdir()) / "ps03_api"
TEMP_DIR.mkdir(exist_ok=True)


# Pydantic models
class SearchRequest(BaseModel):
    chip_ids: List[str]
    class_name: str
    top_k: Optional[int] = 100
    similarity_threshold: Optional[float] = 0.7
    nms_threshold: Optional[float] = 0.5


class DetectionResponse(BaseModel):
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    score: float
    class_name: str
    target_filename: str


class SearchResponse(BaseModel):
    detections: List[DetectionResponse]
    total_count: int
    images_count: int


@app.on_event("startup")
async def startup_event():
    """Load configuration and models on startup"""
    global CONFIG, EMBEDDER, FAISS_INDEX
    
    # Load config
    config_path = Path("configs/default.yaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            CONFIG = yaml.safe_load(f)
        print("✓ Configuration loaded")
    else:
        print("Warning: Config file not found, using defaults")
        CONFIG = {
            'embedder': {
                'architecture': 'resnet18',
                'input_channels': 4,
                'embedding_dim': 256,
                'normalize_embeddings': True,
                'checkpoint': None
            },
            'system': {'device': 'cpu'},
            'preprocessing': {'normalization': 'percentile'}
        }
    
    # Determine device
    device = CONFIG['system']['device']
    if device == 'cuda' and not torch.cuda.is_available():
        device = 'cpu'
    
    # Load embedder
    try:
        EMBEDDER = get_embedder(
            architecture=CONFIG['embedder']['architecture'],
            in_channels=CONFIG['embedder']['input_channels'],
            embedding_dim=CONFIG['embedder']['embedding_dim'],
            normalize=CONFIG['embedder']['normalize_embeddings'],
            checkpoint=CONFIG['embedder'].get('checkpoint'),
            device=device
        )
        print(f"✓ Embedder loaded on {device}")
    except Exception as e:
        print(f"Warning: Could not load embedder: {e}")
    
    print("✓ API ready")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PS-03 Visual Search API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/upload_chip")
async def upload_chip(file: UploadFile = File(...)):
    """
    Upload a query chip image
    Returns chip_id for use in search
    """
    try:
        # Generate unique ID
        chip_id = str(uuid.uuid4())
        
        # Save file
        chip_path = TEMP_DIR / f"chip_{chip_id}.tif"
        with open(chip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read and validate
        image, metadata = read_tiff(str(chip_path))
        
        # Generate preview
        preview = get_rgb_preview(image)
        preview_path = TEMP_DIR / f"chip_{chip_id}_preview.png"
        
        import cv2
        cv2.imwrite(str(preview_path), cv2.cvtColor(preview, cv2.COLOR_RGB2BGR))
        
        return {
            "chip_id": chip_id,
            "filename": file.filename,
            "shape": list(image.shape),
            "preview_url": f"/preview/{chip_id}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to upload chip: {str(e)}")


@app.get("/preview/{chip_id}")
async def get_preview(chip_id: str):
    """Get RGB preview of chip"""
    preview_path = TEMP_DIR / f"chip_{chip_id}_preview.png"
    
    if not preview_path.exists():
        raise HTTPException(status_code=404, detail="Preview not found")
    
    return FileResponse(preview_path)


@app.post("/load_index")
async def load_index(index_dir: str = Form(...)):
    """Load FAISS index from directory"""
    global FAISS_INDEX
    
    try:
        index_path = Path(index_dir)
        if not index_path.exists():
            raise HTTPException(status_code=404, detail="Index directory not found")
        
        FAISS_INDEX = FAISSIndex.load(str(index_path), 'faiss_index')
        
        return {
            "message": "Index loaded successfully",
            "total_vectors": FAISS_INDEX.ntotal,
            "unique_images": len(set(m['image_id'] for m in FAISS_INDEX.tile_metadata))
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load index: {str(e)}")


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Run visual search with uploaded chips
    """
    global EMBEDDER, FAISS_INDEX, CONFIG
    
    if EMBEDDER is None:
        raise HTTPException(status_code=503, detail="Embedder not loaded")
    
    if FAISS_INDEX is None:
        raise HTTPException(status_code=503, detail="Index not loaded. Call /load_index first")
    
    try:
        # Load chips
        chips = []
        chip_names = []
        
        for chip_id in request.chip_ids:
            chip_path = TEMP_DIR / f"chip_{chip_id}.tif"
            if not chip_path.exists():
                raise HTTPException(status_code=404, detail=f"Chip not found: {chip_id}")
            
            image, _ = read_tiff(str(chip_path))
            image = normalize_bands(image, method=CONFIG['preprocessing']['normalization'])
            chips.append(image)
            chip_names.append(chip_id)
        
        # Extract embeddings
        device = CONFIG['system']['device']
        if device == 'cuda' and not torch.cuda.is_available():
            device = 'cpu'
        
        embeddings = []
        EMBEDDER.eval()
        with torch.no_grad():
            for chip in chips:
                chip_tensor = torch.from_numpy(chip).float().unsqueeze(0).to(device)
                emb = EMBEDDER(chip_tensor)
                embeddings.append(emb.cpu().numpy())
        
        embeddings = np.vstack(embeddings)
        
        # Search
        search_results = FAISS_INDEX.search_with_metadata(embeddings, k=request.top_k)
        
        # Retrieve candidates
        retriever = CandidateRetriever(
            top_k_per_chip=request.top_k,
            top_k_per_image=request.top_k,
            similarity_threshold=request.similarity_threshold
        )
        
        detections, grouped = retriever.process(search_results, request.class_name, chip_names)
        
        # Apply NMS
        from engine.nms import apply_nms_per_image
        grouped = apply_nms_per_image(
            grouped,
            method='soft',
            iou_threshold=request.nms_threshold,
            score_threshold=0.3
        )
        
        # Flatten detections
        final_detections = []
        for dets in grouped.values():
            for det in dets:
                final_detections.append(DetectionResponse(
                    x_min=det.x_min,
                    y_min=det.y_min,
                    x_max=det.x_max,
                    y_max=det.y_max,
                    score=det.score,
                    class_name=det.class_name,
                    target_filename=det.target_filename
                ))
        
        return SearchResponse(
            detections=final_detections,
            total_count=len(final_detections),
            images_count=len(grouped)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/export_submission")
async def export_submission(
    detections: List[DetectionResponse],
    team_name: str = Form("TeamName")
):
    """
    Export detections as PS-03 submission file
    """
    try:
        from engine.candidate import Detection
        from engine.writer import generate_submission_filename
        
        # Convert to Detection objects
        det_objects = []
        for det in detections:
            det_objects.append(Detection(
                x_min=det.x_min,
                y_min=det.y_min,
                x_max=det.x_max,
                y_max=det.y_max,
                score=det.score,
                class_name=det.class_name,
                target_filename=det.target_filename
            ))
        
        # Generate filename
        filename = generate_submission_filename(team_name)
        output_path = TEMP_DIR / filename
        
        # Write file
        write_submission_file(det_objects, str(output_path))
        
        return FileResponse(
            output_path,
            media_type='text/plain',
            filename=filename
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.post("/draw_chip")
async def draw_chip(
    image_path: str = Form(...),
    x: int = Form(...),
    y: int = Form(...),
    width: int = Form(...),
    height: int = Form(...)
):
    """
    Extract chip from image by bounding box coordinates
    """
    try:
        # Read image
        if not Path(image_path).exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        image, metadata = read_tiff(image_path)
        
        # Extract region
        C, H, W = image.shape
        y_end = min(y + height, H)
        x_end = min(x + width, W)
        
        chip = image[:, y:y_end, x:x_end]
        
        # Save chip
        chip_id = str(uuid.uuid4())
        chip_path = TEMP_DIR / f"chip_{chip_id}.tif"
        write_tiff(str(chip_path), chip, metadata)
        
        # Generate preview
        preview = get_rgb_preview(chip)
        preview_path = TEMP_DIR / f"chip_{chip_id}_preview.png"
        
        import cv2
        cv2.imwrite(str(preview_path), cv2.cvtColor(preview, cv2.COLOR_RGB2BGR))
        
        return {
            "chip_id": chip_id,
            "shape": list(chip.shape),
            "preview_url": f"/preview/{chip_id}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract chip: {str(e)}")


@app.get("/status")
async def get_status():
    """Get API status"""
    return {
        "embedder_loaded": EMBEDDER is not None,
        "index_loaded": FAISS_INDEX is not None,
        "index_size": FAISS_INDEX.ntotal if FAISS_INDEX else 0,
        "device": CONFIG['system']['device'] if CONFIG else "unknown"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
