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

router = APIRouter()
matcher_service = AIMatcherService()
resume_service = ResumeParserService()

@router.post("/candidate-to-jobs", response_model=JobMatchResponse, responses={500: {"model": ErrorResponse}})
async def match_candidate_to_jobs(request: CandidateMatchRequest, db: AsyncSession = Depends(get_db)):
    try:
        results = await matcher_service.match_candidate_to_jobs(db, request.candidate_id)
        return JobMatchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/job-to-candidates", response_model=CandidateMatchResponse, responses={500: {"model": ErrorResponse}})
async def match_job_to_candidates(request: JobMatchRequest, db: AsyncSession = Depends(get_db)):
    try:
        results = await matcher_service.match_job_to_candidates(db, request.job_id)
        return CandidateMatchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse-resume", response_model=ResumeParseResponse, responses={500: {"model": ErrorResponse}})
async def parse_resume(request: ResumeParseRequest):
    try:
        data = await resume_service.parse_resume(
            file_path=request.file_path, 
            file_name=request.file_name, 
            upload_name=request.upload_name
        )
        return ResumeParseResponse(
            data=ResumeData(**data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
