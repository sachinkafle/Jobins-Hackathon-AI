import asyncio
from sqlalchemy import select, update
from app.db.database import engine, AsyncSessionLocal
from app.models.db_models import Job, CandidatePool
from app.services.ai_matcher import AIMatcherService

async def populate_job_embeddings(session, matcher):
    # Fetch all jobs that don't have embeddings yet
    query = select(Job).where(Job.embedding == None)
    result = await session.execute(query)
    jobs = result.scalars().all()
    
    if not jobs:
        print("All jobs already have embeddings!")
        return

    print(f"Generating embeddings for {len(jobs)} jobs...")
    
    for i, job in enumerate(jobs):
        job_text = matcher.build_job_text(job)
        try:
            embedding = await matcher.get_embedding(job_text)
            await session.execute(
                update(Job)
                .where(Job.job_id == job.job_id)
                .values(embedding=embedding)
            )
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(jobs)} jobs...")
                await session.commit()
        except Exception as e:
            print(f"Error processing Job {job.job_id}: {e}")
    
    await session.commit()
    print("Done populating job embeddings!")

async def populate_candidate_embeddings(session, matcher):
    # Fetch all candidates that don't have embeddings yet
    query = select(CandidatePool).where(CandidatePool.embedding == None)
    result = await session.execute(query)
    candidates = result.scalars().all()
    
    if not candidates:
        print("All candidates already have embeddings!")
        return

    print(f"Generating embeddings for {len(candidates)} candidates...")
    
    for i, candidate in enumerate(candidates):
        candidate_text = matcher.build_candidate_text(candidate)
        try:
            embedding = await matcher.get_embedding(candidate_text)
            await session.execute(
                update(CandidatePool)
                .where(CandidatePool.id == candidate.id)
                .values(embedding=embedding)
            )
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(candidates)} candidates...")
                await session.commit()
        except Exception as e:
            print(f"Error processing Candidate {candidate.id}: {e}")
    
    await session.commit()
    print("Done populating candidate embeddings!")

async def main():
    matcher = AIMatcherService()
    async with AsyncSessionLocal() as session:
        print("--- Starting Job Embeddings ---")
        await populate_job_embeddings(session, matcher)
        print("\n--- Starting Candidate Embeddings ---")
        await populate_candidate_embeddings(session, matcher)
        print("\nAll embeddings populated!")

if __name__ == "__main__":
    asyncio.run(main())
