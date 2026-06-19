# Milestone 1 checklist — Environment + Data Pipeline

Goal: By end of M1, you can run `build_index.py` and see a FAISS index on disk.
No frontend. No API. Just the data and embedding pipeline working end to end.

## Setup tasks

- [ ] Create GitHub repo and push initial commit
- [ ] Create virtual environment and install requirements
  ```bash
  cd backend
  python -m venv venv
  source venv/bin/activate    # Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```
- [ ] Verify PyMuPDF works
  ```python
  import fitz; print(fitz.__version__)
  ```
- [ ] Verify FAISS works
  ```python
  import faiss; print(faiss.__version__)
  ```
- [ ] Verify sentence-transformers works
  ```python
  from sentence_transformers import SentenceTransformer
  m = SentenceTransformer("all-MiniLM-L6-v2")  # downloads ~80MB first time
  print(m.encode("test").shape)  # should print (384,)
  ```

## Data tasks

**Option A — Quick start (synthetic data, no download needed)**
```bash
cd semantic-job-match
python scripts/generate_sample_data.py
# → creates data/raw/jobs.csv with 200 jobs
```

**Option B — Real data (better for the actual product)**
1. Go to https://www.kaggle.com/datasets/arshkon/linkedin-job-postings
2. Download `job_postings.csv`
3. Place it at `data/raw/jobs.csv`
4. Inspect the columns: `python -c "import pandas as pd; print(pd.read_csv('data/raw/jobs.csv').columns.tolist())"`
5. If columns have different names, update `REQUIRED_COLUMNS` in `scripts/build_index.py`

## Index build

```bash
# From project root
python scripts/build_index.py --input data/raw/jobs.csv --limit 500

# Expected output:
# Loaded 500 rows from data/raw/jobs.csv
# After cleaning: 487 valid job postings
# Embedding 487 job descriptions...
# [progress bar]
# Embedding norms: min=1.0000, max=1.0000 (should be ~1.0)
# FAISS index built: 487 vectors, dim=384
# FAISS index saved → data/index/jobs.index
# Saved metadata for 487 jobs → data/index/metadata.json
```

## Verify it worked

```python
# Quick sanity check
import faiss, json, numpy as np
from sentence_transformers import SentenceTransformer

index = faiss.read_index("data/index/jobs.index")
meta = json.load(open("data/index/metadata.json"))

model = SentenceTransformer("all-MiniLM-L6-v2")
query = "Python machine learning engineer with PyTorch and FastAPI experience"
vec = model.encode(query, normalize_embeddings=True).reshape(1, -1)

scores, indices = index.search(vec, k=3)
for score, idx in zip(scores[0], indices[0]):
    job = meta[idx]
    print(f"{score:.3f}  {job['title']} @ {job['company']}")
```

## Run the tests

```bash
cd backend
pytest tests/test_services.py -v -k "not normalized_vector"
# Should see: 10 passed
```

## Git commit for M1

```bash
git add .
git commit -m "feat: M1 - data pipeline and FAISS index builder"
git push origin main
```

## What's next → Milestone 2

- FastAPI server with /health and /match endpoints
- PDF upload and text extraction
- Wire embedding + FAISS into the API
- Test with curl / Postman
