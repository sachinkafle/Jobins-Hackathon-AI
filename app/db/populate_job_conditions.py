import argparse
import asyncio
from sqlalchemy import and_, or_, select
from app.db.database import AsyncSessionLocal
from app.models.db_models import Job
from app.services.job_condition_generator import generate_conditions


async def populate_job_conditions(job_id: int | None = None, apply: bool = False) -> None:
    async with AsyncSessionLocal() as session:
        filters = [Job.job_description.is_not(None), Job.job_description != ""]
        if job_id is not None:
            filters.append(Job.job_id == job_id)
        else:
            filters.append(
                or_(
                    Job.application_condition.is_(None),
                    Job.application_condition == "",
                    Job.welcome_condition.is_(None),
                    Job.welcome_condition == "",
                )
            )

        query = select(Job).where(and_(*filters)).limit(500)
        res = await session.execute(query)
        jobs = res.scalars().all()

        if not jobs:
            print("No jobs found for condition generation.")
            return

        updates = 0
        for job in jobs:
            generated_application, generated_welcome = generate_conditions(job.job_description or "")

            next_application = job.application_condition or generated_application
            next_welcome = job.welcome_condition or generated_welcome

            changed = (job.application_condition != next_application) or (job.welcome_condition != next_welcome)
            if not changed:
                continue

            updates += 1
            print(f"job_id={job.job_id}")
            print("  application_condition ->")
            print(f"{next_application}\n")
            print("  welcome_condition ->")
            print(f"{next_welcome}\n")

            if apply:
                job.application_condition = next_application
                job.welcome_condition = next_welcome

        if apply:
            await session.commit()
            print(f"Applied updates: {updates}")
        else:
            print(f"Dry-run complete. Potential updates: {updates}")
            print("Re-run with --apply to persist changes.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Populate application_condition and welcome_condition from job_description.")
    parser.add_argument("--job-id", type=int, default=None, help="Process a single job_id")
    parser.add_argument("--apply", action="store_true", help="Persist generated conditions")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(populate_job_conditions(job_id=args.job_id, apply=args.apply))

