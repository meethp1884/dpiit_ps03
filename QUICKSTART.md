# PS-03 Quick Start Guide

This guide will help you get up and running in 5 minutes.

## Prerequisites

- Python 3.8+
- CUDA (optional, for GPU)
- At least one sample TIFF image

## Step 1: Install Dependencies (2 min)

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

## Step 2: Prepare Data (1 min)

Create folders and place your data:

```
data/
├── testing_set/
│   └── *.tif      # Your target images
└── sample_set/
    └── *.tif      # Sample images (optional)

chips/
└── MyClass/
    └── chip_01.tif  # Your query chip
```

## Step 3: Build Index (1 min)

```bash
# Windows
python scripts\build_index.py --targets data\testing_set --out cache\indexes

# Linux/Mac
python scripts/build_index.py --targets data/testing_set --out cache/indexes
```

## Step 4: Run Search (1 min)

```bash
# Windows
python scripts\run_search.py ^
  --chips chips\MyClass\chip_01.tif ^
  --index cache\indexes ^
  --name MyClass ^
  --out outputs\results.txt

# Linux/Mac
python scripts/run_search.py \
  --chips chips/MyClass/chip_01.tif \
  --index cache/indexes \
  --name MyClass \
  --out outputs/results.txt
```

## Step 5: View Results

Results are saved to `outputs/results.txt` in PS-03 format:

```
x_min y_min x_max y_max class_name target_filename score
100 200 500 600 MyClass image001 0.923456
...
```

---

## Web UI (Optional)

### Start Backend:
```bash
python api/main.py
```

### Start Frontend (separate terminal):
```bash
cd ui
npm install
npm start
```

Open `http://localhost:3000` in your browser.

---

## Troubleshooting

**"No module named 'rasterio'"**
- Run: `pip install -r requirements.txt`

**"CUDA out of memory"**
- Add `--device cpu` to commands

**"No images found"**
- Check file paths use correct separators (`\` on Windows)
- Verify TIFF files are in correct directories

---

## Next Steps

- **Train embedder:** See `README.md` training section
- **Customize config:** Edit `configs/default.yaml`
- **Multiple classes:** Run search multiple times with different chips
- **Evaluation:** Use `eval_local_map.py` if you have ground truth

For full documentation, see `README.md`.
