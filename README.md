# Semantic Job Match Engine

> Upload a resume → get ranked job listings with explainable similarity scores, powered by Sentence-BERT + FAISS.

**Live demo:** [your-app.hf.space](https://your-app.hf.space) · **Author:** Tanisha Dhopeshwar

---

## What it does

1. User uploads a PDF resume
2. Backend extracts and chunks the text
3. Text is embedded using `all-MiniLM-L6-v2` (Sentence-BERT)
4. FAISS finds the top-K most similar job postings from a pre-indexed corpus
5. A gap analysis surfaces which skills the resume is missing per job

## Architecture

```
┌─────────────────┐     POST /api/match      ┌───────────────────────────────┐
│   React UI      │ ───────────────────────► │   FastAPI Backend              │
│  (PDF upload)   │ ◄─────────────────────── │   /embed → /search → /explain  │
└─────────────────┘     ranked JSON           └───────────┬───────────────────┘
                                                          │
                              ┌───────────────────────────┼────────────────┐
                              ▼                           ▼                ▼
                       PyMuPDF                     SBERT model        FAISS index
                    (text extract)              (HuggingFace)     (pre-built offline)
```

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Embedding | `sentence-transformers/all-MiniLM-L6-v2` | Fast, 384-dim, great semantic quality |
| Vector search | FAISS (IndexFlatIP) | No infra needed, runs in-process |
| Backend | FastAPI + Uvicorn | Async, auto docs at `/docs` |
| PDF parsing | PyMuPDF (fitz) | Best text extraction quality |
| Frontend | React + Vite | Fast dev, easy deploy |
| Deployment | Hugging Face Spaces (Docker) | Free, ML-native |

## Quick start

```bash
# Clone and setup
git clone https://github.com/tanisha/semantic-job-match
cd semantic-job-match

# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Build the FAISS index (one-time, uses sample data)
python ../scripts/build_index.py

# Start backend
uvicorn api.main:app --reload --port 8000

# Frontend (new terminal)
cd ../frontend
npm install && npm run dev
```

Then open `http://localhost:5173`

## Project structure

```
semantic-job-match/
├── backend/
│   ├── api/           # FastAPI app, routes
│   ├── core/          # Config, logging
│   ├── models/        # Pydantic schemas
│   ├── services/      # Embedding, search, gap analysis
│   └── tests/
├── frontend/
│   └── src/
│       ├── components/ # UploadZone, ResultCard, ScoreBar
│       ├── pages/
│       └── hooks/
├── data/
│   ├── raw/           # Source job posting CSVs
│   ├── processed/     # Cleaned job data JSON
│   └── index/         # FAISS .index + metadata.json
├── scripts/
│   ├── build_index.py # Pre-builds FAISS index
│   └── scrape_jobs.py # (optional) job data collection
├── notebooks/
│   └── 01_exploration.ipynb
└── .github/workflows/
    └── test.yml
```

## Milestones

- [x] **M1** — Folder structure, environment, sample data pipeline
- [ ] **M2** — Embedding service + FAISS index build script
- [ ] **M3** — FastAPI backend (3 endpoints)
- [ ] **M4** — React frontend with PDF upload + results UI
- [ ] **M5** — Gap analysis (skill diff per job)
- [ ] **M6** — Docker + HuggingFace Spaces deployment
