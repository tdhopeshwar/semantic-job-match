from pydantic import BaseModel, Field
from typing import Optional


class JobMatch(BaseModel):
    """A single matched job posting."""
    job_id: str
    title: str
    company: str
    location: Optional[str] = None
    description_snippet: str = Field(..., description="First 300 chars of cleaned description")
    score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score")
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)


class MatchResponse(BaseModel):
    """Response from the /match endpoint."""
    resume_text_preview: str = Field(..., description="First 200 chars extracted from PDF")
    resume_skills: list[str]
    matches: list[JobMatch]
    total_jobs_searched: int


class EmbedResponse(BaseModel):
    """Debug endpoint: returns embedding vector."""
    text_preview: str
    embedding_dim: int
    embedding: list[float]


class HealthResponse(BaseModel):
    status: str
    index_loaded: bool
    index_size: int
    model_loaded: bool
