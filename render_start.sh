#!/bin/bash
# render_start.sh
# Runs on Render before starting the FastAPI server.
# Builds the FAISS index from seed data if it doesn't exist yet.

set -e

echo "=== Semantic Job Match — Startup ==="

# Build index if missing
INDEX_PATH="data/index/jobs.index"
SEED_PATH="data/seed_jobs.csv"

if [ ! -f "$INDEX_PATH" ]; then
  echo "Index not found. Building from seed data ($SEED_PATH)..."
  mkdir -p data/index
  python scripts/build_index.py --input "$SEED_PATH" --limit 500
  echo "Index built successfully."
else
  echo "Index already exists, skipping build."
fi

# Start FastAPI
echo "Starting FastAPI server..."
cd backend
uvicorn api.main:app --host 0.0.0.0 --port $PORT
