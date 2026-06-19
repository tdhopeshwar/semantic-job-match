"""
FAISS search service.

Index type: IndexFlatIP (Inner Product)
When vectors are L2-normalized, inner product == cosine similarity.
This gives exact nearest-neighbor search with no approximation.

For >100K jobs, swap to IndexIVFFlat or IndexHNSWFlat for speed.
"""
import json
import numpy as np
import faiss
from pathlib import Path
from core.config import settings


class SearchService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._index = None
            cls._instance._metadata = []
        return cls._instance

    def load(self) -> None:
        """Load FAISS index and job metadata. Call once at startup."""
        if self._index is not None:
            return

        index_path = settings.index_path
        metadata_path = settings.metadata_path

        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found at {index_path}. "
                "Run: python scripts/build_index.py"
            )

        print(f"Loading FAISS index from {index_path}")
        self._index = faiss.read_index(str(index_path))

        print(f"Loading job metadata from {metadata_path}")
        with open(metadata_path, "r") as f:
            self._metadata = json.load(f)

        print(f"Index loaded: {self._index.ntotal} jobs indexed.")

    @property
    def is_loaded(self) -> bool:
        return self._index is not None

    @property
    def index_size(self) -> int:
        return self._index.ntotal if self._index else 0

    def search(
        self,
        query_vec: np.ndarray,
        top_k: int = None,
    ) -> list[dict]:
        """
        Search FAISS index for most similar jobs.
        
        Args:
            query_vec: Shape (384,), L2-normalized float32
            top_k: Number of results (defaults to settings.top_k)
        
        Returns:
            List of dicts with job metadata + 'score' key (cosine similarity)
        """
        if not self.is_loaded:
            raise RuntimeError("Index not loaded. Call .load() first.")

        k = top_k or settings.top_k

        # FAISS expects shape (1, dim) for single query
        query_matrix = query_vec.reshape(1, -1)
        scores, indices = self._index.search(query_matrix, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for not found
                continue
            if score < settings.min_score_threshold:
                continue

            job = self._metadata[idx].copy()
            job["score"] = float(round(score, 4))
            results.append(job)

        return results


# Module-level singleton
searcher = SearchService()
