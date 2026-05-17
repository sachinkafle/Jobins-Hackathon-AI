import asyncio
from sqlalchemy import select, text
from app.db.database import AsyncSessionLocal
from app.models.db_models import Job


ACCOUNTANT_JOB_DESCRIPTION = """We are looking for an experienced Senior Accountant to join our finance team.

Requirements:
- 4+ years of accounting or finance experience
- Strong knowledge of accounting principles (GAAP)
- Proficiency in QuickBooks or similar accounting software
- Expert-level Microsoft Excel skills
- Experience with tax preparation and filing
- Knowledge of accounts payable and accounts receivable
- Experience with payroll processing
- Ability to prepare financial statements and reports
- Auditing experience is a plus
- CPA certification preferred"""

ACCOUNTANT_RESPONSIBILITIES = """- Prepare and maintain accurate financial records
- Manage accounts payable and receivable
- Process monthly, quarterly, and annual financial reports
- Handle tax preparation and compliance
- Perform bank reconciliations
- Assist in budgeting and forecasting
- Conduct internal audits
- Ensure compliance with financial regulations
- Support external audits
- Collaborate with management on financial decisions"""

ACCOUNTANT_SKILLS = "Accounting, Bookkeeping, Financial Reporting, Tax Preparation, Accounts Payable, Accounts Receivable, QuickBooks, Excel, Payroll, Auditing, GAAP, Balance Sheet, Bank Reconciliation"

ACCOUNTANT_QUALIFICATION = "Bachelor's degree in Accounting, Finance, or related field. CPA certification preferred."

APPLICATION_CONDITION = """- 4+ years of accounting or finance experience
- Strong knowledge of accounting principles (GAAP)
- Proficiency in QuickBooks or similar accounting software
- Expert-level Microsoft Excel skills
- Experience with tax preparation and filing
- Knowledge of accounts payable and accounts receivable
- Experience with payroll processing
- Ability to prepare financial statements and reports"""

WELCOME_CONDITION = """- Auditing experience is a plus
- CPA certification preferred
- Experience with ERP or financial management systems is welcome"""


async def main():
    async with AsyncSessionLocal() as s:
        job = (await s.execute(select(Job).where(Job.job_id == 1013))).scalar_one_or_none()

        if not job:
            print("job_id 1013 not found. Exiting.")
            return

        print(f"Before: description={repr((job.job_description or '')[:60])}")
        print(f"Before: skills={repr(job.required_skills_text)}")

        job.job_description = ACCOUNTANT_JOB_DESCRIPTION
        job.job_responsibilities = ACCOUNTANT_RESPONSIBILITIES
        job.required_skills_text = ACCOUNTANT_SKILLS
        job.required_qualification = ACCOUNTANT_QUALIFICATION
        job.application_condition = APPLICATION_CONDITION
        job.welcome_condition = WELCOME_CONDITION
        job.embedding = None  # force regeneration on next API call

        await s.commit()
        print(f"\nAfter: description={repr(job.job_description[:60])}")
        print(f"After: skills={repr(job.required_skills_text[:60])}")
        print("\n✅ job_id 1013 fully populated. Embedding will auto-generate on next API call.")


asyncio.run(main())

