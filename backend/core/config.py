from pydantic_settings import BaseSettings
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    # Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # FAISS index paths
    index_path: Path = ROOT_DIR / "data" / "index" / "jobs.index"
    metadata_path: Path = ROOT_DIR / "data" / "index" / "metadata.json"

    # Search
    top_k: int = 10
    min_score_threshold: float = 0.3  # cosine similarity floor

    # PDF
    max_pdf_size_mb: int = 5
    max_pages: int = 3               # most resumes are 1-2 pages

    # API
    api_prefix: str = "/api"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
