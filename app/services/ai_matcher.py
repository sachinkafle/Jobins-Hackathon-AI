import os
import json
import asyncio
import numpy as np
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, not_, update
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from app.models.db_models import CandidatePool, Job, SelectionHistory
from app.models.schemas import JobMatchResult, CandidateMatchResult
from app.services.prompts import MATCHING_SYSTEM_PROMPT, MATCHING_USER_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIMatcherService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    async def get_embedding(self, text: str) -> List[float]:
        return await self.embeddings.aembed_query(text)

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        return await self.embeddings.aembed_documents(texts)

    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        v1 = np.array(v1)
        v2 = np.array(v2)
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    async def get_recommended_job_ids(self, session: AsyncSession, candidate_id: int) -> List[int]:
        query = select(SelectionHistory.job_id).where(SelectionHistory.candidate_id == candidate_id)
        result = await session.execute(query)
        return [row[0] for row in result.all()]

    async def save_match_result(self, session: AsyncSession, candidate_id: int, job_id: int, score: int, reasoning: str):
        new_history = SelectionHistory(
            candidate_id=candidate_id,
            job_id=job_id,
            match_score=score,
            match_reason=reasoning
        )
        session.add(new_history)
        # We use flush instead of commit to keep the session alive for the next save in the loop
        await session.flush()

    async def score_match(self, candidate_info: str, job_info: str) -> Dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", MATCHING_SYSTEM_PROMPT),
            ("user", MATCHING_USER_PROMPT)
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"candidate": candidate_info, "job": job_info})
        
        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            return json.loads(content)
        except Exception:
            return {"score": 0, "reasoning": "Failed to generate reasoning."}

    async def match_candidate_to_jobs(self, session: AsyncSession, candidate_id: int, company_id: int = None) -> List[JobMatchResult]:
        logger.info(f"--- Starting Match for Candidate {candidate_id} ---")
        
        # 1. Fetch Candidate
        candidate_query = select(CandidatePool).where(CandidatePool.id == candidate_id)
        candidate_res = await session.execute(candidate_query)
        candidate = candidate_res.scalar_one_or_none()
        if not candidate:
            logger.warning(f"Candidate {candidate_id} not found.")
            return []

        if company_id is None:
            company_id = candidate.company_id
        
        logger.info(f"Candidate: {candidate.first_name} {candidate.last_name}, Company: {company_id}")

        # Prepare rich candidate text
        candidate_text = f"Name: {candidate.first_name} {candidate.last_name}\n"
        candidate_text += f"Education: {candidate.academic_background}\n"
        candidate_text += f"Experience: {candidate.experience} years\n"
        candidate_text += f"Skills: {json.dumps(candidate.skill) if candidate.skill else 'N/A'}\n"
        if candidate.document_parsed_cv:
            candidate_text += f"CV: {json.dumps(candidate.document_parsed_cv)}\n"

        # 2. Exclude history
        recommended_job_ids = await self.get_recommended_job_ids(session, candidate_id)
        logger.info(f"Excluding {len(recommended_job_ids)} previously recommended jobs.")

        # 3. Fetch Jobs
        jobs_query = select(Job).where(
            and_(
                Job.organization_id == company_id,
                Job.job_status == 'Open',
                not_(Job.job_id.in_(recommended_job_ids)) if recommended_job_ids else True
            )
        )
        jobs_res = await session.execute(jobs_query)
        all_jobs = jobs_res.scalars().all()
        logger.info(f"Found {len(all_jobs)} potential jobs in company.")

        if not all_jobs:
            return []

        # 4. Handle Missing Embeddings (Batching)
        jobs_needing_embedding = [j for j in all_jobs if not j.embedding]
        if jobs_needing_embedding:
            logger.info(f"Generating embeddings for {len(jobs_needing_embedding)} jobs (Batching)...")
            texts = [f"{j.job_title} {j.job_description}" for j in jobs_needing_embedding]
            new_embeddings = await self.get_embeddings_batch(texts)
            for job, emb in zip(jobs_needing_embedding, new_embeddings):
                job.embedding = emb
            await session.flush()

        # 5. Semantic Search (Fast Filter)
        cand_embedding = await self.get_embedding(candidate_text)
        job_similarities = []
        for job in all_jobs:
            sim = self.cosine_similarity(cand_embedding, job.embedding)
            job_similarities.append((job, sim))

        job_similarities.sort(key=lambda x: x[1], reverse=True)
        top_jobs = [item[0] for item in job_similarities[:10]] # AI Scores top 10
        logger.info(f"Semantic search completed. Top Job: {top_jobs[0].job_title if top_jobs else 'None'}")

        # 6. AI Reranking
        logger.info("Starting AI Match Scoring for top 10 results...")
        tasks = [self.score_match(candidate_text, f"{j.job_title} {j.job_description}") for j in top_jobs]
        scores = await asyncio.gather(*tasks)

        # 7. Format and Persist
        results = []
        for job, score_data in zip(top_jobs, scores):
            res = JobMatchResult(
                job_id=job.job_id,
                score=score_data.get("score", 0),
                reasoning=score_data.get("reasoning", "")
            )
            results.append(res)
            await self.save_match_result(session, candidate_id, job.job_id, res.score, res.reasoning)
        
        await session.commit()
        logger.info("Match results saved to history. Done!")
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results

    async def match_job_to_candidates(self, session: AsyncSession, job_id: int, company_id: int = None) -> List[CandidateMatchResult]:
        # Implementation (Simplified for brevity, similar to above)
        query = select(Job).where(Job.job_id == job_id)
        res = await session.execute(query)
        job = res.scalar_one_or_none()
        if not job: return []
        
        candidates_query = select(CandidatePool).where(CandidatePool.company_id == (company_id or job.organization_id)).limit(20)
        cands_res = await session.execute(candidates_query)
        candidates = cands_res.scalars().all()
        
        tasks = [self.score_match(f"{c.first_name} {c.skill}", f"{job.job_title} {job.job_description}") for c in candidates]
        scores = await asyncio.gather(*tasks)
        
        results = []
        for cand, sd in zip(candidates, scores):
            results.append(CandidateMatchResult(candidate_id=cand.id, score=sd.get("score", 0), reasoning=sd.get("reasoning", "")))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results
