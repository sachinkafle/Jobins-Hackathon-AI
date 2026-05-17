import asyncio
import json
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.db_models import CandidatePool, Job, SelectionHistory
from app.services.ai_matcher import AIMatcherService

async def insert_test_data():
    """Insert test data for job_ids 5, 499, 500 and some candidates"""

    async with AsyncSessionLocal() as session:
        try:
            # Job configurations
            jobs_config = {
                5: {
                    "title": "Senior Python Developer",
                    "description": """
We are looking for an experienced Senior Python Developer to join our growing team.
Requirements:
- 5+ years of Python development experience
- Strong knowledge of FastAPI or Django
- Experience with async programming and SQLAlchemy ORM
- Proficient in RESTful API design
- Experience with machine learning libraries (numpy, pandas, scikit-learn)
- Excellent problem-solving skills
- Previous experience with AI/ML projects is a plus

Responsibilities:
- Design and develop scalable Python applications
- Work with AI and machine learning models
- Collaborate with team members on complex features
- Review code and maintain code quality standards
- Optimize application performance
                    """,
                    "skills": "Python, FastAPI, SQLAlchemy, Async Programming, REST APIs, Machine Learning, NumPy, Pandas",
                    "qualification": "Bachelor's degree in Computer Science or related field, or equivalent experience"
                },
                499: {
                    "title": "Full Stack Web Developer",
                    "description": """
Join our team as a Full Stack Web Developer!
Requirements:
- 3+ years of web development experience
- Proficiency in React.js or Vue.js for frontend
- Strong backend skills with Node.js, Python, or Java
- Experience with relational databases (PostgreSQL, MySQL)
- Understanding of RESTful APIs and microservices
- Familiarity with Docker and containerization
- Git version control expertise

Responsibilities:
- Develop and maintain both frontend and backend components
- Build responsive and user-friendly web applications
- Implement API integrations and database operations
- Participate in code reviews and team collaboration
- Troubleshoot and optimize application performance
                    """,
                    "skills": "React, Node.js, JavaScript, PostgreSQL, REST APIs, Docker, Git, HTML/CSS",
                    "qualification": "Bachelor's degree in Computer Science or equivalent practical experience"
                },
                500: {
                    "title": "Data Science Engineer",
                    "description": """
We are seeking a talented Data Science Engineer to drive insights and innovation.
Requirements:
- 4+ years of data science and machine learning experience
- Strong proficiency in Python and SQL
- Experience with scikit-learn, TensorFlow, or PyTorch
- Knowledge of statistical analysis and data visualization
- Experience with big data tools (Spark, Hadoop)
- Strong problem-solving and communication skills
- Experience with cloud platforms (AWS, GCP, Azure)

Responsibilities:
- Develop and deploy machine learning models
- Perform data analysis and create data visualizations
- Optimize model performance and accuracy
- Collaborate with product and engineering teams
- Document models and maintain code quality
- Stay updated with latest ML techniques and tools
                    """,
                    "skills": "Python, Machine Learning, TensorFlow, Scikit-learn, SQL, Spark, Data Visualization, AWS",
                    "qualification": "Master's degree in Data Science, Statistics, or Computer Science, or equivalent experience"
                }
            }

            # Process each job
            for job_id, config in jobs_config.items():
                job_query = select(Job).where(Job.job_id == job_id)
                existing_job = await session.execute(job_query)
                job_exists = existing_job.scalar_one_or_none()

                if job_exists:
                    print(f"Job ID {job_id} already exists. Updating with proper data...")
                    job_exists.job_title = config["title"]
                    job_exists.job_description = config["description"]
                    job_exists.required_skills_text = config["skills"]
                    job_exists.required_qualification = config["qualification"]
                    job_exists.job_status = "Open"
                    job_exists.organization_id = 1
                else:
                    print(f"Creating Job ID {job_id}...")
                    job = Job(
                        job_id=job_id,
                        organization_id=1,
                        job_title=config["title"],
                        job_description=config["description"],
                        required_skills_text=config["skills"],
                        required_qualification=config["qualification"],
                        job_status="Open"
                    )
                    session.add(job)

            # Check for candidates
            candidates_query = select(CandidatePool).where(CandidatePool.company_id == 1)
            existing_candidates = await session.execute(candidates_query)
            candidates = existing_candidates.scalars().all()

            if len(candidates) < 2:
                print(f"Found {len(candidates)} candidates. Inserting more test candidates...")

                # Candidate 1: Good match
                candidate1 = CandidatePool(
                    company_id=1,
                    first_name="John",
                    last_name="Developer",
                    self_promotion="Experienced Python developer with 6 years of expertise in building scalable web applications. Passionate about FastAPI and async programming.",
                    skill=["Python", "FastAPI", "SQLAlchemy", "REST APIs", "Async Programming", "NumPy", "Pandas", "PostgreSQL"],
                    academic_background="Bachelor's in Computer Science",
                    experience=6,
                    document_parsed_cv={
                        "experience_years": 6,
                        "technical_skills": ["Python", "FastAPI", "SQLAlchemy", "Async", "REST APIs", "NumPy", "Pandas"],
                        "education": "BS Computer Science",
                        "achievements": ["Led AI integration project", "Architected microservices"]
                    }
                )
                session.add(candidate1)

                # Candidate 2: Moderate match
                candidate2 = CandidatePool(
                    company_id=1,
                    first_name="Jane",
                    last_name="Coder",
                    self_promotion="Full-stack developer with 4 years of experience. Recently started learning Python and async patterns.",
                    skill=["JavaScript", "Python", "Django", "SQL", "REST APIs"],
                    academic_background="Bachelor's in Information Technology",
                    experience=4,
                    document_parsed_cv={
                        "experience_years": 4,
                        "technical_skills": ["JavaScript", "Python", "Django", "SQL", "REST"],
                        "education": "BS Information Technology",
                        "achievements": ["Built e-commerce platform", "Team lead experience"]
                    }
                )
                session.add(candidate2)

                # Candidate 3: Another good match
                candidate3 = CandidatePool(
                    company_id=1,
                    first_name="Alex",
                    last_name="Engineer",
                    self_promotion="Python specialist with 7 years of backend development. Expert in FastAPI, SQLAlchemy, and machine learning libraries.",
                    skill=["Python", "FastAPI", "SQLAlchemy", "Scikit-learn", "NumPy", "Pandas", "PostgreSQL", "Docker"],
                    academic_background="Master's in Computer Science",
                    experience=7,
                    document_parsed_cv={
                        "experience_years": 7,
                        "technical_skills": ["Python", "FastAPI", "SQLAlchemy", "Scikit-learn", "NumPy", "Pandas", "Docker"],
                        "education": "MS Computer Science",
                        "achievements": ["Implemented ML pipelines", "Optimized API performance by 40%"]
                    }
                )
                session.add(candidate3)

                # Candidate 4: Poor match
                candidate4 = CandidatePool(
                    company_id=1,
                    first_name="Bob",
                    last_name="Designer",
                    self_promotion="UI/UX designer with 5 years of experience. Familiar with frontend technologies.",
                    skill=["Figma", "CSS", "HTML", "JavaScript", "UI Design"],
                    academic_background="Bachelor's in Graphic Design",
                    experience=5,
                    document_parsed_cv={
                        "experience_years": 5,
                        "technical_skills": ["Figma", "CSS", "HTML", "JavaScript"],
                        "education": "BS Graphic Design",
                        "achievements": ["Award-winning UI designs", "Led design team"]
                    }
                )
                session.add(candidate4)

                print("Test candidates added.")

            await session.commit()
            print("✅ Test data inserted successfully!")

            # Now generate embeddings if not present
            print("\nGenerating embeddings for job...")
            job_query = select(Job).where(Job.job_id == 5)
            job_result = await session.execute(job_query)
            job = job_result.scalar_one_or_none()

            if job and not job.embedding:
                matcher = AIMatcherService()
                job_text = f"Title: {job.job_title}\nDescription: {job.job_description}\nSkills: {job.required_skills_text}"
                embedding = await matcher.get_embedding(job_text)
                job.embedding = embedding
                await session.commit()
                print("✅ Job embedding generated!")
            else:
                print("✅ Job embedding already exists or job not found.")

        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(insert_test_data())

