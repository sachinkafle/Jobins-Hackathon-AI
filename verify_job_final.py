import asyncio
from sqlalchemy import select, or_
from app.db.database import AsyncSessionLocal
from app.models.db_models import Job, CandidatePool


async def verify():
    async with AsyncSessionLocal() as s:

        # 1. Accountant / Senior / Finance jobs
        jobs = (await s.execute(
            select(Job.job_id, Job.job_title, Job.organization_id, Job.job_status,
                   Job.application_condition, Job.embedding)
            .where(or_(
                Job.job_title.ilike('%account%'),
                Job.job_title.ilike('%finance%'),
                Job.job_title.ilike('%senior%'),
            ))
            .limit(10)
        )).all()

        print("\n=== JOBS ===")
        if jobs:
            for r in jobs:
                emb_flag = "has_emb=YES" if r[5] else "has_emb=NO"
                print(f"  job_id={r[0]}  org={r[2]}  status={r[3]}  {emb_flag}")
                print(f"    title: {r[1]}")
                if r[4]:
                    print(f"    app_condition: {r[4][:100]}")
        else:
            print("  No matching jobs found")

        # 2. David Wilson candidate
        cands = (await s.execute(
            select(CandidatePool.id, CandidatePool.first_name, CandidatePool.last_name,
                   CandidatePool.company_id, CandidatePool.experience, CandidatePool.self_promotion)
            .where(or_(
                CandidatePool.first_name.ilike('%david%'),
                CandidatePool.last_name.ilike('%wilson%'),
            ))
        )).all()

        print("\n=== CANDIDATE: David Wilson ===")
        if cands:
            for c in cands:
                promo = (c[5] or '')[:120]
                print(f"  id={c[0]}  name={c[1]} {c[2]}  company_id={c[3]}  experience={c[4]} yrs")
                print(f"    self_promotion: {promo}")
        else:
            print("  NOT IN DB YET - must be added manually via your system")

        # 3. Cross-company eligibility
        if jobs and cands:
            print("\n=== CROSS-COMPANY FILTER CHECK ===")
            for r in jobs:
                for c in cands:
                    ok = c[3] != r[2]
                    status = "ELIGIBLE" if ok else "BLOCKED (same company)"
                    print(f"  job_id={r[0]} (org={r[2]}) + candidate_id={c[0]} (company={c[3]}) -> {status}")
        else:
            print("\n=== NOTE ===")
            print("  Once you save the Senior Accountant job AND David Wilson candidate via your UI,")
            print("  re-run this script to confirm cross-company eligibility.")


asyncio.run(verify())

