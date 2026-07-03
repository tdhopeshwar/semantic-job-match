from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from models.schemas import MatchResponse, JobMatch, EmbedResponse, HealthResponse
from services.embedding_service import embedder
from services.search_service import searcher
from services.pdf_service import extract_text, extract_skills, validate_pdf_size
from services.gap_service import analyze_gap
from core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        index_loaded=searcher.is_loaded,
        index_size=searcher.index_size,
        model_loaded=embedder.is_loaded,
    )


@router.post("/match", response_model=MatchResponse)
async def match_resume(
    file: UploadFile = File(..., description="PDF resume, max 5MB"),
    top_k: int = Form(default=10, ge=1, le=25),
):
    """
    Main endpoint. Upload a resume PDF and receive ranked job matches.
    
    - Extracts text from PDF
    - Embeds resume text using SBERT
    - Searches FAISS index
    - Returns ranked matches with skill gap analysis
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted.")

    pdf_bytes = await file.read()

    try:
        validate_pdf_size(pdf_bytes, max_mb=settings.max_pdf_size_mb)
    except ValueError as e:
        raise HTTPException(413, str(e))

    # Extract text + skills from resume
    resume_text = extract_text(pdf_bytes, max_pages=settings.max_pages)
    if len(resume_text.strip()) < 100:
        raise HTTPException(422, "Could not extract enough text from the PDF. Is it a scanned image?")

    resume_skills = extract_skills(resume_text)

    # Embed and search
    resume_vec = embedder.embed(resume_text)
    raw_matches = searcher.search(resume_vec, top_k=top_k)

    # Build response with gap analysis
    job_matches = []
    for job in raw_matches:
        matched, missing = analyze_gap(resume_skills, job.get("description", ""))
        job_matches.append(JobMatch(
            job_id=job["job_id"],
            title=job["title"],
            company=job.get("company") or job.get("company_name", ""),
            location=job.get("location"),
            description_snippet=job.get("description", "")[:300],
            score=job["score"],
            matched_skills=matched,
            missing_skills=missing,
        ))

    return MatchResponse(
        resume_text_preview=resume_text[:200],
        resume_skills=resume_skills,
        matches=job_matches,
        total_jobs_searched=searcher.index_size,
    )


@router.post("/embed", response_model=EmbedResponse)
async def embed_text(text: str = Form(...)):
    """
    Debug endpoint: embed any text string and see the vector.
    Useful for testing the embedding service in isolation.
    """
    vec = embedder.embed(text)
    return EmbedResponse(
        text_preview=text[:100],
        embedding_dim=len(vec),
        embedding=vec.tolist(),
    )
