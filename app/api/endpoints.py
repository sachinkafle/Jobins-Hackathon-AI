import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.schemas import (
    CandidateMatchRequest, 
    JobMatchRequest, 
    JobMatchResponse, 
    CandidateMatchResponse, 
    ErrorResponse, 
    ResumeParseRequest, 
    ResumeParseResponse, 
    ResumeData
)
from app.services.ai_matcher import AIMatcherService
from app.services.resume_parser import ResumeParserService
from app.core.cache import ai_cache

logger = logging.getLogger(__name__)

router = APIRouter()
matcher_service = AIMatcherService()
resume_service = ResumeParserService()

@router.post("/candidate-to-jobs", response_model=JobMatchResponse, responses={500: {"model": ErrorResponse}})
async def match_candidate_to_jobs(payload: CandidateMatchRequest, db: AsyncSession = Depends(get_db)):
    cache_key = f"candidate_to_jobs:{payload.candidate_id}"
    cached = ai_cache.get(cache_key)
    if cached is not None:
        logger.info(f"CACHE HIT for candidate {payload.candidate_id}")
        return cached
    try:
        results = await matcher_service.match_candidate_to_jobs(db, payload.candidate_id)
        response = JobMatchResponse(results=results)
        ai_cache.set(cache_key, response, ttl_seconds=300)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/job-to-candidates", response_model=CandidateMatchResponse, responses={500: {"model": ErrorResponse}})
async def match_job_to_candidates(payload: JobMatchRequest, db: AsyncSession = Depends(get_db)):
    cache_key = f"job_to_candidates:{payload.job_id}"
    cached = ai_cache.get(cache_key)
    if cached is not None:
        logger.info(f"CACHE HIT for job {payload.job_id}")
        return cached
    try:
        results = await matcher_service.match_job_to_candidates(db, payload.job_id)
        response = CandidateMatchResponse(results=results)
        ai_cache.set(cache_key, response, ttl_seconds=300)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse-resume", response_model=ResumeParseResponse, responses={500: {"model": ErrorResponse}})
async def parse_resume(payload: ResumeParseRequest):
    cache_key = f"parse_resume:{payload.file_path}"
    cached = ai_cache.get(cache_key)
    if cached is not None:
        logger.info(f"CACHE HIT for resume {payload.file_path}")
        return cached
    try:
        data = await resume_service.parse_resume(
            file_path=payload.file_path, 
            file_name=payload.file_name, 
            upload_name=payload.upload_name
        )
        response = ResumeParseResponse(
            success=True,
            message="Resume parsed successfully",
            data=ResumeData(**data)
        )
        ai_cache.set(cache_key, response, ttl_seconds=600)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
