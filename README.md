# PS-03 Visual Search, Retrieval & Detection for Satellite Imagery

**Stage-1 MVP: Production-Quality Prototype**

A complete visual search system for multispectral satellite imagery (4-band: B,G,R,NIR) that enables query-by-example detection using CNN embeddings, FAISS indexing, and optional ZNCC verification.

---

## 🎯 Overview

This system accepts 1-5 sample image chips (uploaded or drawn as bounding boxes) and searches a target folder of multispectral TIFFs to output bounding box detections with similarity scores in the PS-03 submission format.

**Key Features:**
- 🔍 CNN-based embedder (ResNet18/34 or custom) for 4-band imagery
- ⚡ FAISS indexing for fast similarity search
- 🎨 React web UI for chip upload/drawing and result visualization
- 🐍 FastAPI backend with REST endpoints
- 📊 Training pipeline with triplet loss and batch-hard mining
- 🔧 CLI tools for building indexes, running searches, and evaluation
- 📦 PS-03 compliant submission file generator

---

## 📁 Project Structure

```
ps03/
├── ui/                      # React frontend
│   ├── src/
│   │   ├── App.js          # Main UI component
│   │   └── index.css       # Styles
│   └── package.json
├── api/                     # FastAPI backend
│   └── main.py             # API endpoints
├── engine/                  # Core search engine
│   ├── io_tiff.py          # TIFF I/O and normalization
│   ├── tiler.py            # Sliding window tiler
│   ├── embedder.py         # CNN embedder models
│   ├── index_faiss.py      # FAISS index wrapper
│   ├── candidate.py        # Candidate retrieval
│   ├── verify_ncc.py       # ZNCC scorer
│   ├── nms.py              # Non-maximum suppression
│   ├── writer.py           # Submission file writer
│   └── train.py            # Training pipeline
├── scripts/                 # CLI tools
│   ├── build_index.py      # Build FAISS index
│   ├── run_search.py       # Run visual search
│   ├── train_embedder.py   # Train embedder
│   └── eval_local_map.py   # Evaluate mAP
├── configs/
│   └── default.yaml        # Default configuration
├── data/                    # Dataset folder (create this)
│   ├── training_set/       # 150 training TIFFs
│   ├── testing_set/        # 40 testing TIFFs
│   ├── sample_set/         # 9 sample TIFFs + JSONs
│   └── short_listing_set/  # 40 shortlist TIFFs
├── chips/                   # Query chips (per class)
│   └── <ClassName>/
├── cache/                   # Precomputed indexes
├── outputs/                 # Results and submissions
│   └── runs/
├── models/                  # Model checkpoints
│   └── checkpoints/
└── requirements.txt
```

---

## 🚀 Quick Start

### 1. Installation

**Prerequisites:**
- Python 3.8+
- Node.js 16+ (for UI)
- CUDA (optional, for GPU acceleration)

**Install Python dependencies:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Install UI dependencies:**
```bash
cd ui
npm install
cd ..
```

### 2. Dataset Setup

Place your datasets in the `data/` folder following this structure:

```
data/
├── training_set/*.tif       # 150 training images
├── testing_set/*.tif        # 40 testing images (for submission)
├── sample_set/*.tif         # 9 sample images
└── sample_set/*.json        # Ground truth annotations
```

**Example:**
```
data/training_set/GC01PS03D0001.tif
data/training_set/GC01PS03D0002.tif
...
data/testing_set/GC01PS03T0001.tif
...
```

### 3. Prepare Query Chips

Create query chips from sample images or your own annotations:

```bash
# Option A: Place pre-extracted chips
chips/Solar_Panel/chip_01.tif
chips/Solar_Panel/chip_02.tif

# Option B: Use the UI to draw bounding boxes (see Web UI section)
```

### 4. Build FAISS Index

Build an index from your target images (testing_set):

**Windows:**
```cmd
python scripts\build_index.py --targets data\testing_set --out cache\indexes --config configs\default.yaml
```

**Linux/Mac:**
```bash
python scripts/build_index.py --targets data/testing_set --out cache/indexes --config configs/default.yaml
```

This will:
- Tile each image into overlapping patches
- Extract embeddings using the CNN
- Build a FAISS index for fast search
- Save to `cache/indexes/`

### 5. Run Visual Search

Search for objects using your query chips:

**Windows:**
```cmd
python scripts\run_search.py ^
  --chips chips\Solar_Panel\chip_01.tif chips\Solar_Panel\chip_02.tif ^
  --index cache\indexes ^
  --name Solar_Panel ^
  --out outputs\runs\GC_PS03_16-Oct-2025_TeamName\results.txt ^
  --team TeamName
```

**Linux/Mac:**
```bash
python scripts/run_search.py \
  --chips chips/Solar_Panel/chip_01.tif chips/Solar_Panel/chip_02.tif \
  --index cache/indexes \
  --name Solar_Panel \
  --out outputs/runs/GC_PS03_16-Oct-2025_TeamName/results.txt \
  --team TeamName
```

**Output:** `results.txt` in PS-03 format:
```
x_min y_min x_max y_max class_name target_filename score
100 200 500 600 Solar_Panel GC01PS03T0001 0.923456
...
```

---

## 🌐 Web UI

### Start the Backend API

```bash
# Windows
python api\main.py

# Linux/Mac
python api/main.py
```

Backend runs at `http://localhost:8000`

### Start the React Frontend

```bash
cd ui
npm start
```

UI opens at `http://localhost:3000`

### Using the UI

1. **Upload Chips Tab:**
   - Click "Upload TIFF chips" to upload query chips
   - Enter index path (e.g., `cache/indexes`)
   - Click "Load Index"

2. **Search Tab:**
   - Enter class name (e.g., `Solar_Panel`)
   - Click "Run Search"

3. **Results Tab:**
   - View detections with bounding boxes and scores
   - Click "Export Submission" to download results file

---

## 🎓 Training the Embedder

Train on your training set to improve retrieval performance:

**Windows:**
```cmd
python scripts\train_embedder.py ^
  --data data\training_set ^
  --config configs\default.yaml ^
  --epochs 50 ^
  --device cuda
```

**Linux/Mac:**
```bash
python scripts/train_embedder.py \
  --data data/training_set \
  --config configs/default.yaml \
  --epochs 50 \
  --device cuda
```

**What it does:**
- Extracts random tiles from training images
- Trains CNN with triplet loss (batch-hard mining)
- Saves checkpoints to `models/checkpoints/`
- Uses data augmentation (flips, rotations, brightness)

**Training config (in `configs/default.yaml`):**
```yaml
training:
  batch_size: 32
  num_epochs: 50
  learning_rate: 0.001
  loss: "triplet"
  margin: 0.5
  mining: "batch_hard"
```

**Use trained checkpoint:**
```bash
# Update config with checkpoint path
embedder:
  checkpoint: "models/checkpoints/best.pth"

# Or specify via CLI
python scripts/run_search.py --checkpoint models/checkpoints/best.pth ...
```

---

## 📊 Evaluation

Evaluate your submission against ground truth (for validation):

```bash
python scripts/eval_local_map.py \
  --submission outputs/runs/GC_PS03_16-Oct-2025_TeamName/results.txt \
  --ground-truth data/sample_set \
  --iou-thresholds 0.5 0.75 0.9
```

**Output:**
```
Evaluating at IoU threshold: 0.5
  mAP: 0.7543
  Precision: 0.8123
  Recall: 0.7234

IoU 0.5: mAP=0.7543, P=0.8123, R=0.7234
IoU 0.75: mAP=0.6234, P=0.7456, R=0.6543
```

---

## ⚙️ Configuration

Edit `configs/default.yaml` to customize:

**Key settings:**
```yaml
# Tiling
tiler:
  tile_size: 384      # Tile size in pixels
  stride: 192         # 50% overlap
  scales: [1.0, 0.75, 1.33]  # Multi-scale search

# Embedder
embedder:
  architecture: "resnet18"  # resnet18, resnet34, custom_cnn
  embedding_dim: 256
  checkpoint: null    # Path to trained model

# Search
retrieval:
  top_k_per_chip: 500
  similarity_threshold: 0.7

# NMS
nms:
  iou_threshold: 0.5
  method: "soft"      # soft or hard
  score_threshold: 0.3
```

---

## 🛠️ CLI Reference

### build_index.py

Build FAISS index from target images.

```bash
python scripts/build_index.py \
  --targets <path_to_images> \
  --out <output_dir> \
  --config configs/default.yaml \
  --checkpoint <embedder_checkpoint> \
  --device cuda
```

**Arguments:**
- `--targets`: Directory containing target TIFF images
- `--out`: Output directory for index files
- `--config`: Path to config file
- `--checkpoint`: Embedder checkpoint (optional)
- `--device`: Device (cuda/cpu)

### run_search.py

Run visual search with query chips.

```bash
python scripts/run_search.py \
  --chips <chip1.tif> <chip2.tif> ... \
  --index <index_dir> \
  --name <class_name> \
  --out <output_file.txt> \
  --config configs/default.yaml \
  --team <team_name>
```

**Arguments:**
- `--chips`: Paths to query chip TIFFs (1-5 chips)
- `--index`: Directory containing FAISS index
- `--name`: Class name for detections
- `--out`: Output submission file path
- `--team`: Team name for submission filename
- `--no-zncc`: Disable ZNCC verification

### train_embedder.py

Train CNN embedder on training set.

```bash
python scripts/train_embedder.py \
  --data <training_dir> \
  --config configs/default.yaml \
  --epochs 50 \
  --device cuda
```

### eval_local_map.py

Evaluate submission against ground truth.

```bash
python scripts/eval_local_map.py \
  --submission <results.txt> \
  --ground-truth <json_dir> \
  --iou-thresholds 0.5 0.75
```

---

## 📝 Submission Format

PS-03 requires this exact format:

**Filename:** `GC_PS03_<DD-MMM-YYYY>_<Team>.txt`

**Example:** `GC_PS03_16-Oct-2025_TeamXYZ.txt`

**Content (space-delimited):**
```
x_min y_min x_max y_max class_name target_filename score
100 200 500 600 Solar_Panel GC01PS03T0001 0.923456
150 300 450 700 Solar_Panel GC01PS03T0001 0.887234
...
```

**Fields:**
- `x_min, y_min, x_max, y_max`: Bounding box coordinates (integers)
- `class_name`: Object class (no spaces)
- `target_filename`: Target image filename (without .tif)
- `score`: Confidence score (float, or -1 if N/A)

---

## 🧪 Testing

Run unit tests:

```bash
pytest tests/
```

Test modules:
- `test_io_tiff.py`: TIFF reading/writing
- `test_tiler.py`: Tile generation
- `test_embedder.py`: Embedder forward pass
- `test_index.py`: FAISS indexing

---

## 🐛 Troubleshooting

### "CUDA out of memory"
- Reduce `batch_size` in config
- Use `--device cpu`
- Reduce `tile_size` or image count

### "No tiles generated"
- Check image size > tile_size
- Verify TIFF files are valid 4-band images

### "Index not found"
- Run `build_index.py` first
- Verify `--index` path is correct

### "FileNotFoundError: chip not found"
- Check chip paths use correct separators (`\` on Windows, `/` on Linux)
- Use absolute paths or run from repo root

### UI not loading
- Check API is running: `http://localhost:8000/`
- Check CORS settings in `api/main.py`
- Verify React is running: `http://localhost:3000`

---

## 📚 Architecture Details

### CNN Embedder

**ResNet18 (default):**
- Modified first conv layer for 4 channels (B,G,R,NIR)
- Output: 256-D L2-normalized embeddings
- ~11M parameters

**Custom CNN (lightweight):**
- 4 conv blocks with downsampling
- Output: 256-D embeddings
- ~3M parameters

### FAISS Index

**Flat (exact search):**
- Inner product (cosine similarity)
- Exact nearest neighbors
- Best for <1M vectors

**IVF (approximate):**
- Inverted file index
- Faster for large datasets
- Configurable `nlist` and `nprobe`

### Training Loss

**Triplet Loss:**
- Batch-hard mining: selects hardest positive/negative per anchor
- Margin: 0.5 (configurable)
- Encourages similar images to have close embeddings

---

## 🎯 Performance Tips

1. **Use GPU for training:** 10-20x faster than CPU
2. **Pre-build indexes:** Avoid rebuilding for every search
3. **Multi-scale tiles:** Improves detection at different scales
4. **Tune NMS threshold:** Balance precision/recall
5. **Train on domain data:** Fine-tune on your specific imagery

---

## 📄 License

This project is for PS-03 challenge use.

---

## 🙏 Acknowledgments

Built using:
- PyTorch & torchvision
- FAISS (Facebook AI Similarity Search)
- FastAPI
- React & Lucide icons
- Rasterio for TIFF I/O

---

## 📞 Support

For issues or questions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Review config in `configs/default.yaml`
3. Check logs in terminal output

---

**Good luck with PS-03! 🚀**
"# dpiit_ps03" 
