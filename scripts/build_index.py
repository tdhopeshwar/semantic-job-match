"""
Build FAISS index from job postings CSV.

Usage:
    python scripts/build_index.py --input data/raw/jobs.csv --limit 2000

This script:
1. Loads job postings from CSV
2. Cleans and prepares text for embedding
3. Embeds all job descriptions using SBERT (batched)
4. Builds a FAISS IndexFlatIP and saves it to disk
5. Saves job metadata (title, company, etc.) as JSON

Run this once. The index file is ~6MB per 2000 jobs.
The backend loads it at startup and searches it in <1ms.

Dataset options (free, no scraping needed):
  - https://www.kaggle.com/datasets/arshkon/linkedin-job-postings
  - https://www.kaggle.com/datasets/jobspikr/10000-data-analyst-jobs
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import faiss

# Add backend to path so we can import services
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.embedding_service import embedder
from core.config import settings


REQUIRED_COLUMNS = {"title", "company", "description"}
TEXT_CONCAT_TEMPLATE = "{title} at {company}. {description}"


def load_jobs(csv_path: Path, limit: int) -> pd.DataFrame:
    df = pd.read_csv(csv_path, nrows=limit)
    print(f"Loaded {len(df)} rows from {csv_path}")

    # Normalize column names to lowercase
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {missing}\n"
            f"Available columns: {list(df.columns)}"
        )

    # Drop rows with missing critical fields
    df = df.dropna(subset=["title", "company", "description"])
    df = df.reset_index(drop=True)
    print(f"After cleaning: {len(df)} valid job postings")
    return df


def prepare_texts(df: pd.DataFrame) -> list[str]:
    """
    Concatenate title + company + description for embedding.
    
    Why concatenate? The embedding should capture the full
    context of the job, not just the description.
    """
    texts = []
    for _, row in df.iterrows():
        # Truncate description to 512 tokens (model max)
        desc = str(row["description"])[:2000]
        text = TEXT_CONCAT_TEMPLATE.format(
            title=row["title"],
            company=row["company"],
            description=desc,
        )
        texts.append(text)
    return texts


def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    """
    Build IndexFlatIP (exact inner product search).
    Vectors must be L2-normalized for IP == cosine similarity.
    """
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print(f"FAISS index built: {index.ntotal} vectors, dim={dim}")
    return index


def save_metadata(df: pd.DataFrame, path: Path) -> None:
    """Save job metadata as JSON list (parallel to FAISS index order)."""
    meta_cols = ["title", "company", "description"]
    optional_cols = ["location", "salary", "job_type", "url"]
    cols_to_save = meta_cols + [c for c in optional_cols if c in df.columns]

    records = []
    for i, row in df[cols_to_save].iterrows():
        record = row.to_dict()
        record["job_id"] = str(i)
        records.append(record)

    with open(path, "w") as f:
        json.dump(records, f, indent=2)
    print(f"Saved metadata for {len(records)} jobs → {path}")


def main():
    parser = argparse.ArgumentParser(description="Build FAISS index from job postings")
    parser.add_argument("--input", type=Path, default=Path("data/raw/jobs.csv"))
    parser.add_argument("--limit", type=int, default=2000, help="Max jobs to index")
    args = parser.parse_args()

    # Ensure output directory exists
    settings.index_path.parent.mkdir(parents=True, exist_ok=True)

    # Load data
    df = load_jobs(args.input, args.limit)

    # Prepare text
    texts = prepare_texts(df)

    # Embed (this takes ~1-2 min for 2000 jobs on CPU)
    print(f"\nEmbedding {len(texts)} job descriptions...")
    embedder.load()
    embeddings = embedder.embed_batch(texts, batch_size=64)

    # Verify normalization (should already be normalized by embed_batch)
    norms = np.linalg.norm(embeddings, axis=1)
    print(f"Embedding norms: min={norms.min():.4f}, max={norms.max():.4f} (should be ~1.0)")

    # Build and save FAISS index
    index = build_faiss_index(embeddings)
    faiss.write_index(index, str(settings.index_path))
    print(f"FAISS index saved → {settings.index_path}")

    # Save metadata
    save_metadata(df, settings.metadata_path)

    print("\nDone! Start the backend with: uvicorn api.main:app --reload --port 8000")


if __name__ == "__main__":
    main()
