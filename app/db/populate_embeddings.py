import asyncio
from sqlalchemy import select, update
from app.db.database import engine, AsyncSessionLocal
from app.models.db_models import Job
from app.services.ai_matcher import AIMatcherService

async def populate_job_embeddings():
    matcher = AIMatcherService()
    async with AsyncSessionLocal() as session:
        # Fetch all jobs that don't have embeddings yet
        query = select(Job).where(Job.embedding == None)
        result = await session.execute(query)
        jobs = result.scalars().all()
        
        if not jobs:
            print("All jobs already have embeddings!")
            return

        print(f"Generating embeddings for {len(jobs)} jobs...")
        
        for i, job in enumerate(jobs):
            # Create a rich text representation for the vector
            job_text = (
                f"Title: {job.job_title}\n"
                f"Description: {job.job_description}\n"
                f"Responsibilities: {job.job_responsibilities}\n"
                f"Skills: {job.required_skills_text}"
            )

            try:
                embedding = await matcher.get_embedding(job_text)
                
                # Update the job record
                await session.execute(
                    update(Job)
                    .where(Job.job_id == job.job_id)
                    .values(embedding=embedding)
                )
                
                if (i + 1) % 10 == 0:
                    print(f"Processed {i + 1}/{len(jobs)} jobs...")
                    await session.commit() # Commit in batches
            except Exception as e:
                print(f"Error processing Job {job.job_id}: {e}")
        
        await session.commit()
        print("Done populating job embeddings!")

if __name__ == "__main__":
    asyncio.run(populate_job_embeddings())
