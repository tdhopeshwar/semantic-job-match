"""
FastAPI application entry point.

Endpoints:
  GET  /api/health     — liveness + index stats
  POST /api/match      — main endpoint: PDF → ranked jobs
  POST /api/embed      — debug: see the embedding vector for any text
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from api.routes import router
from services.embedding_service import embedder
from services.search_service import searcher


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load model and index once
    embedder.load()
    try:
        searcher.load()
    except FileNotFoundError as e:
        print(f"WARNING: {e}")
        print("The /match endpoint will fail until the index is built.")
    yield
    # Shutdown: nothing to clean up for FAISS/SBERT


app = FastAPI(
    title="Semantic Job Match Engine",
    description="Upload a resume PDF, get ranked job matches with skill gap analysis.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.api_prefix)
