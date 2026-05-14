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

    def build_job_text(self, job: Job) -> str:
        def to_text(value):
            if value is None:
                return ""
            if isinstance(value, (list, dict)):
                return json.dumps(value, ensure_ascii=True)
            return str(value)

        fields = [
            ("Job Title", job.job_title),
            ("Job Description", job.job_description),
            ("Job Responsibilities", job.job_responsibilities),
            ("Required Skills", job.required_skills_text),
            ("Required Qualification", job.required_qualification),
            ("Application Condition", job.application_condition),
            ("Welcome Condition", job.welcome_condition),
            ("Role Scope", job.job_change_possibility_description),
            ("Minimum Education", job.minimum_education_level),
            ("Academic Level", job.academic_level),
            ("Experience", job.experience),
            ("Minimum Job Experience", job.minimum_job_experience),
            ("Minimum Industry Experience", job.minimum_industry_experience),
            ("Employment Status", job.employment_status),
            ("Employment Category", job.job_employment_category),
            ("Preferred Nationality", job.pref_nationality),
            ("Preferred Gender", job.gender),
            ("Age Range", f"{to_text(job.age_min)}-{to_text(job.age_max)}" if job.age_min or job.age_max else ""),
            ("Year Salary", f"{to_text(job.min_year_salary)}-{to_text(job.max_year_salary)}" if job.min_year_salary or job.max_year_salary else ""),
            ("Month Salary", f"{to_text(job.min_month_salary)}-{to_text(job.max_month_salary)}" if job.min_month_salary or job.max_month_salary else ""),
            ("Location", job.location_desc),
            ("Working Hours", job.working_hours),
            ("Holidays", job.holidays),
            ("Benefits", job.benefits),
            ("Allowances", job.allowances),
            ("Selection Flow", job.selection_flow),
            ("Organization Description", job.organization_description),
            ("Recruitment Status", job.recruitment_status),
        ]
        return "\n".join(f"{label}: {to_text(value)}" for label, value in fields if to_text(value).strip())

    def build_candidate_text(self, c: CandidatePool) -> str:
        def t(v):
            if v is None:
                return ""
            if isinstance(v, (list, dict)):
                return json.dumps(v, ensure_ascii=False)
            return str(v)

        parts = [
            ("Name", f"{t(c.first_name)} {t(c.last_name)}".strip()),
            ("Gender", c.gender),
            ("Nationality", c.nationality),
            ("Education", c.academic_background),
            ("Education Details", c.educational_background_details),
            ("Qualification", c.qualification),
            ("Experience (years)", c.experience),
            ("Industry Experience (years)", c.years_of_industry_experience),
            ("Companies Changed", c.no_of_company_change),
            ("Current Status", c.current_employment_status),
            ("Current Type", c.current_employment_type),
            ("Current Position", c.current_position),
            ("Current Salary (year)", c.current_year_salary),
            ("Most Recent Workplace", c.most_recent_workplace),
            ("Skills", c.skill),
            ("Japanese Skills", c.japanese_skills),
            ("English Skills", c.english_skills),
            ("Chinese Skills", c.chinese_skills),
            ("Other Languages", c.other_languages),
            ("TOEIC", c.toeic),
            ("TOEFL", c.toefl),
            ("Self Promotion", c.self_promotion),
            ("Work History", c.employment_histories),
            ("Desired Job Timing", c.desired_job_change_timing),
            ("Desired Motivation", c.desired_job_change_motivation),
            ("Desired Employment Type", c.desired_employment_type),
            ("Desired Position", c.desired_position),
            ("Min Desired Salary", c.min_desire_salary),
            ("Relocation OK", c.relocation),
            ("Desired Locations", c.specified_desired_locations),
            ("Desired Occupations", c.specified_desired_occupations),
            ("Desired Sub-industries", c.specified_desired_sub_industries),
            ("Personality", c.candidate_personality),
            ("Job Change Axis", c.job_change_axis),
            ("CV Data", c.document_parsed_cv),
        ]
        return "\n".join(f"{label}: {t(value)}" for label, value in parts if t(value).strip())

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
        candidate_text = self.build_candidate_text(candidate)

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
            texts = [self.build_job_text(j) for j in jobs_needing_embedding]
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
        tasks = [self.score_match(candidate_text, self.build_job_text(j)) for j in top_jobs]
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
        logger.info(f"--- Starting Match for Job {job_id} ---")

        # 1. Fetch Job
        query = select(Job).where(Job.job_id == job_id)
        res = await session.execute(query)
        job = res.scalar_one_or_none()
        if not job:
            logger.warning(f"Job {job_id} not found.")
            return []

        logger.info(f"Job: {job.job_title}, Org: {job.organization_id}")
        job_text = self.build_job_text(job)

        # 2. Build company filter – source candidates from other companies
        if company_id is None:
            company_filter = CandidatePool.company_id != job.organization_id
        else:
            company_filter = and_(
                CandidatePool.company_id == company_id,
                CandidatePool.company_id != job.organization_id
            )

        # 3. Fetch pool of candidates with actual profile data (self_promotion OR skill)
        pool_query = (
            select(CandidatePool)
            .where(
                and_(
                    company_filter,
                    CandidatePool.self_promotion.isnot(None),
                    CandidatePool.self_promotion != "",
                )
            )
        )
        pool_res = await session.execute(pool_query)
        all_candidates = pool_res.scalars().all()

        # Fallback: include candidates without self_promotion
        if not all_candidates:
            pool_res2 = await session.execute(select(CandidatePool).where(company_filter))
            all_candidates = pool_res2.scalars().all()

        logger.info(f"Candidate pool size: {len(all_candidates)}")
        if not all_candidates:
            return []

        # 4. Embed all candidates in batch for semantic search
        logger.info(f"Generating embeddings for {len(all_candidates)} candidates (batch)...")
        cand_texts = [self.build_candidate_text(c) for c in all_candidates]
        cand_embeddings = await self.get_embeddings_batch(cand_texts)

        # 5. Semantic search – embed job and rank candidates
        job_embedding = await self.get_embedding(job_text)
        cand_similarities = []
        for cand, emb in zip(all_candidates, cand_embeddings):
            sim = self.cosine_similarity(job_embedding, emb)
            cand_similarities.append((cand, sim))

        cand_similarities.sort(key=lambda x: x[1], reverse=True)
        top_candidates = [item[0] for item in cand_similarities[:10]]
        logger.info(f"Semantic search done. Top candidate: {top_candidates[0].first_name if top_candidates else 'None'}")

        # 6. AI Reranking
        tasks = [self.score_match(self.build_candidate_text(c), job_text) for c in top_candidates]
        scores = await asyncio.gather(*tasks)
        
        # 7. Format results
        results = []
        for cand, sd in zip(top_candidates, scores):
            results.append(
                CandidateMatchResult(
                    candidate_id=cand.id,
                    candidate_company_id=cand.company_id,
                    score=sd.get("score", 0),
                    reasoning=sd.get("reasoning", "")
                )
            )

        await session.commit()
        logger.info("Job-to-candidate match complete!")
        results.sort(key=lambda x: x.score, reverse=True)
        return results
