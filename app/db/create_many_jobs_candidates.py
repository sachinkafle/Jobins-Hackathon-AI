"""
This script creates multiple jobs and candidates to test the matching system.
It demonstrates how the AI matcher works with various skill combinations.
"""

import asyncio
import json
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.db_models import CandidatePool, Job
from app.services.ai_matcher import AIMatcherService


# ============================================================================
# JOBS CONFIGURATION - Different roles across various industries
# ============================================================================
JOBS_CONFIG = {
    # Cloud/Infrastructure Role
    1001: {
        "title": "Cloud Infrastructure Engineer",
        "description": """
We're looking for an experienced Cloud Infrastructure Engineer to architect and manage our cloud infrastructure.

Requirements:
- 4+ years of cloud infrastructure experience
- Strong expertise in AWS or GCP
- Knowledge of Kubernetes and container orchestration
- Experience with Infrastructure as Code (Terraform, CloudFormation)
- Proficiency in Linux/Unix systems
- Understanding of CI/CD pipelines
- Experience with monitoring and logging tools (Prometheus, ELK)

Responsibilities:
- Design and deploy scalable cloud architectures
- Implement and manage Kubernetes clusters
- Automate infrastructure provisioning
- Monitor system performance and security
- Collaborate with development teams on deployment strategies
- Optimize cloud costs and performance
        """,
        "skills": "AWS, GCP, Kubernetes, Terraform, Docker, CI/CD, Linux, Prometheus, CloudFormation",
        "qualification": "Bachelor's in Computer Science or equivalent experience"
    },

    # Mobile Developer Role
    1002: {
        "title": "Mobile App Developer",
        "description": """
Join our mobile team to build engaging iOS and Android applications.

Requirements:
- 3+ years of mobile app development experience
- Proficiency in React Native or Flutter
- Strong understanding of mobile UI/UX principles
- Experience with REST APIs and mobile databases
- Familiarity with app stores and publishing process
- Knowledge of performance optimization for mobile
- Experience with version control (Git)

Responsibilities:
- Develop and maintain mobile applications
- Implement responsive and intuitive user interfaces
- Integrate with backend APIs
- Test and debug mobile applications
- Optimize app performance and battery usage
- Work with designers to implement UI/UX designs
- Participate in code reviews
        """,
        "skills": "React Native, Flutter, Swift, Kotlin, Mobile UI/UX, REST APIs, SQLite, Firebase",
        "qualification": "Bachelor's in Computer Science or proven mobile dev experience"
    },

    # DevOps Role
    1003: {
        "title": "DevOps Engineer",
        "description": """
We need a DevOps Engineer to streamline our development and deployment processes.

Requirements:
- 3+ years of DevOps experience
- Strong scripting skills (Python, Bash, or Go)
- Expertise in containerization (Docker)
- Knowledge of container orchestration (Kubernetes)
- Experience with infrastructure automation
- Proficiency in version control systems
- Understanding of cloud platforms (AWS/GCP/Azure)
- Experience with monitoring and alerting

Responsibilities:
- Maintain and improve CI/CD pipelines
- Manage containerized applications
- Implement infrastructure as code
- Monitor system performance and uptime
- Troubleshoot deployment issues
- Implement security best practices
- Document infrastructure and processes
        """,
        "skills": "Docker, Kubernetes, Python, Bash, Jenkins, GitLab CI, AWS, Terraform, Monitoring",
        "qualification": "Bachelor's in IT or equivalent hands-on experience"
    },

    # QA Automation Role
    1004: {
        "title": "QA Automation Engineer",
        "description": """
We're seeking a QA Automation Engineer to ensure software quality through automated testing.

Requirements:
- 2+ years of QA automation experience
- Proficiency in automation frameworks (Selenium, Cypress, TestNG)
- Strong programming skills (Java, Python, or JavaScript)
- Experience with API testing tools (Postman, REST Assured)
- Knowledge of CI/CD integration for testing
- Understanding of testing methodologies
- Experience with bug tracking tools (Jira)

Responsibilities:
- Design and implement automated test cases
- Maintain and update test automation frameworks
- Execute automated test suites
- Report and track defects
- Collaborate with developers on test coverage
- Perform exploratory testing
- Document test cases and results
        """,
        "skills": "Selenium, Cypress, Java, Python, REST APIs, Postman, TestNG, Jira, CI/CD",
        "qualification": "Bachelor's in Computer Science or equivalent QA experience"
    },

    # Product Manager Role
    1005: {
        "title": "Product Manager",
        "description": """
Help us shape the future of our product as a Product Manager.

Requirements:
- 4+ years of product management experience
- Strong data analysis and business acumen
- Experience with SaaS products
- Familiarity with Agile methodology
- Excellent communication and leadership skills
- Knowledge of user research and design thinking
- Experience with analytics tools and SQL

Responsibilities:
- Define product strategy and roadmap
- Conduct user research and market analysis
- Work with engineering and design teams
- Create product requirements and specifications
- Track and analyze product metrics
- Prioritize features based on business impact
- Communicate product vision to stakeholders
        """,
        "skills": "Product Strategy, Agile, SQL, Analytics, Stakeholder Management, User Research, Roadmapping",
        "qualification": "Bachelor's degree, MBA preferred"
    },

    # Data Engineer Role
    1006: {
        "title": "Data Engineer",
        "description": """
Build data pipelines and infrastructure to support our analytics platform.

Requirements:
- 3+ years of data engineering experience
- Proficiency in Python or Java
- Experience with big data technologies (Spark, Hadoop)
- Knowledge of data warehousing (Snowflake, BigQuery, Redshift)
- SQL expertise
- Experience with ETL tools and data modeling
- Familiarity with cloud platforms

Responsibilities:
- Design and maintain data pipelines
- Develop ETL processes
- Optimize data warehouse queries
- Implement data quality checks
- Monitor data infrastructure
- Collaborate with data scientists and analysts
- Handle large-scale data processing
        """,
        "skills": "Python, Spark, SQL, Hive, Kafka, Data Warehousing, ETL, Airflow, Snowflake",
        "qualification": "Bachelor's in Computer Science or related field"
    },

    # Cybersecurity Role
    1007: {
        "title": "Cybersecurity Specialist",
        "description": """
Protect our systems and data as a Cybersecurity Specialist.

Requirements:
- 5+ years of cybersecurity experience
- Knowledge of network security and protocols
- Experience with security tools (SIEM, vulnerability scanning)
- Understanding of application security
- Knowledge of encryption and authentication
- Experience with security compliance (SOC 2, ISO 27001)
- Incident response experience

Responsibilities:
- Conduct security assessments and audits
- Implement security controls and policies
- Monitor and respond to security incidents
- Perform penetration testing
- Stay updated with security threats
- Train staff on security practices
- Maintain security documentation
        """,
        "skills": "Network Security, SIEM, Penetration Testing, Firewalls, Encryption, Compliance, Incident Response",
        "qualification": "Bachelor's in Cybersecurity or related field, CISSP/CEH cert preferred"
    },

    # Frontend Developer Role
    1008: {
        "title": "Senior Frontend Developer",
        "description": """
Build beautiful and performant web applications as a Senior Frontend Developer.

Requirements:
- 5+ years of frontend development experience
- Expert-level knowledge of React, Angular, or Vue.js
- Strong JavaScript/TypeScript skills
- Experience with state management libraries
- Knowledge of responsive design and accessibility
- Proficiency with CSS frameworks and preprocessors
- Experience with browser DevTools and performance optimization

Responsibilities:
- Develop and maintain frontend applications
- Optimize application performance
- Implement responsive designs
- Collaborate with UX/UI designers
- Mentor junior developers
- Implement accessibility standards
- Review code and maintain code quality
        """,
        "skills": "React, TypeScript, JavaScript, Redux, CSS, HTML, Webpack, Performance Optimization, Accessibility",
        "qualification": "Bachelor's in Computer Science or equivalent experience"
    },

    # Backend Developer Role
    1009: {
        "title": "Golang Backend Developer",
        "description": """
Build high-performance backend systems using Golang.

Requirements:
- 3+ years of backend development experience with Golang
- Strong understanding of REST and gRPC APIs
- Experience with relational databases (PostgreSQL, MySQL)
- Knowledge of microservices architecture
- Familiarity with message brokers (RabbitMQ, Kafka)
- Experience with containerization (Docker)
- Understanding of scalable system design

Responsibilities:
- Develop scalable backend services in Golang
- Design and implement APIs
- Optimize database queries and performance
- Work with Docker and orchestration platforms
- Implement logging and monitoring
- Participate in architecture decisions
- Collaborate with frontend teams
        """,
        "skills": "Golang, REST APIs, PostgreSQL, Docker, Kubernetes, gRPC, Microservices, MySQL",
        "qualification": "Bachelor's in Computer Science or equivalent experience"
    },

    # ML Engineer Role
    1010: {
        "title": "Machine Learning Engineer",
        "description": """
Develop and deploy machine learning models to solve real-world problems.

Requirements:
- 3+ years of ML/AI experience
- Proficiency in Python and ML libraries (TensorFlow, PyTorch)
- Strong understanding of ML algorithms and statistics
- Experience with data preprocessing and feature engineering
- Knowledge of model evaluation and validation
- Experience deploying models to production
- Familiarity with cloud ML platforms (AWS SageMaker, GCP ML Engine)

Responsibilities:
- Develop and train machine learning models
- Perform feature engineering and data analysis
- Evaluate and optimize model performance
- Deploy models to production
- Monitor model performance and drift
- Collaborate with data scientists and engineers
- Conduct research on new ML techniques
        """,
        "skills": "Python, TensorFlow, PyTorch, Machine Learning, Statistics, Scikit-learn, AWS SageMaker, SQL",
        "qualification": "Bachelor's/Master's in Computer Science, Math, or Statistics"
    },
}


# ============================================================================
# CANDIDATES CONFIGURATION - Diverse skill sets for matching
# ============================================================================
CANDIDATES_CONFIG = [
    # Candidate 1: Cloud/DevOps specialist
    {
        "first_name": "Michael",
        "last_name": "Chen",
        "self_promotion": "Cloud infrastructure expert with 5 years of AWS and Kubernetes experience. Passionate about DevOps automation and infrastructure as code.",
        "skills": ["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD", "Linux", "Prometheus", "Bash"],
        "academic_background": "Bachelor's in Computer Science",
        "experience": 5,
        "document_parsed_cv": {
            "experience_years": 5,
            "technical_skills": ["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD", "Linux", "Prometheus"],
            "education": "BS Computer Science",
            "achievements": ["Led Kubernetes migration", "Reduced cloud costs by 30%"]
        }
    },

    # Candidate 2: Mobile developer
    {
        "first_name": "Sarah",
        "last_name": "Johnson",
        "self_promotion": "Experienced mobile app developer with expertise in React Native. Successfully published 5+ apps on App Store and Google Play.",
        "skills": ["React Native", "JavaScript", "Firebase", "REST APIs", "Mobile UI/UX", "Git", "Android", "iOS"],
        "academic_background": "Bachelor's in Information Technology",
        "experience": 4,
        "document_parsed_cv": {
            "experience_years": 4,
            "technical_skills": ["React Native", "JavaScript", "Firebase", "REST APIs", "Mobile Design"],
            "education": "BS Information Technology",
            "achievements": ["Published 5+ mobile apps", "100K+ downloads"]
        }
    },

    # Candidate 3: DevOps engineer
    {
        "first_name": "David",
        "last_name": "Kumar",
        "self_promotion": "DevOps specialist with strong scripting skills in Python and Bash. Expert in Docker, Jenkins, and GitLab CI.",
        "skills": ["Docker", "Kubernetes", "Python", "Bash", "Jenkins", "GitLab CI", "AWS", "Monitoring"],
        "academic_background": "Bachelor's in Computer Engineering",
        "experience": 4,
        "document_parsed_cv": {
            "experience_years": 4,
            "technical_skills": ["Docker", "Kubernetes", "Python", "Bash", "Jenkins", "CI/CD"],
            "education": "BS Computer Engineering",
            "achievements": ["Automated CI/CD pipelines", "Zero-downtime deployments"]
        }
    },

    # Candidate 4: QA Automation engineer
    {
        "first_name": "Emma",
        "last_name": "Williams",
        "self_promotion": "QA Automation specialist with strong Selenium and TestNG expertise. Experienced in building scalable test frameworks.",
        "skills": ["Selenium", "Java", "TestNG", "Cypress", "REST APIs", "Jira", "SQL", "Python"],
        "academic_background": "Bachelor's in Software Engineering",
        "experience": 3,
        "document_parsed_cv": {
            "experience_years": 3,
            "technical_skills": ["Selenium", "Java", "TestNG", "Cypress", "REST APIs", "Jira"],
            "education": "BS Software Engineering",
            "achievements": ["Built automated test framework", "Increased test coverage to 85%"]
        }
    },

    # Candidate 5: Product Manager
    {
        "first_name": "James",
        "last_name": "Smith",
        "self_promotion": "Product Manager with 6 years of experience in SaaS products. Strong data-driven decision maker with SQL expertise.",
        "skills": ["Product Strategy", "Agile", "SQL", "Analytics", "User Research", "Roadmapping", "Jira", "Tableau"],
        "academic_background": "MBA from Stanford",
        "experience": 6,
        "document_parsed_cv": {
            "experience_years": 6,
            "technical_skills": ["Product Strategy", "Agile", "SQL", "Analytics", "Tableau"],
            "education": "MBA Stanford",
            "achievements": ["Grew product to $10M ARR", "Led team of 15"]
        }
    },

    # Candidate 6: Data Engineer
    {
        "first_name": "Lisa",
        "last_name": "Patel",
        "self_promotion": "Data Engineer with expertise in building ETL pipelines and data warehouses. Strong Python and SQL skills.",
        "skills": ["Python", "Spark", "SQL", "Kafka", "Data Warehousing", "ETL", "Airflow", "Snowflake"],
        "academic_background": "Master's in Data Science",
        "experience": 4,
        "document_parsed_cv": {
            "experience_years": 4,
            "technical_skills": ["Python", "Spark", "SQL", "Kafka", "ETL", "Airflow"],
            "education": "MS Data Science",
            "achievements": ["Built real-time data pipeline", "Designed data warehouse"]
        }
    },

    # Candidate 7: Cybersecurity specialist
    {
        "first_name": "Robert",
        "last_name": "Martinez",
        "self_promotion": "Cybersecurity expert with 7 years of experience. CISSP certified with strong skills in network security and incident response.",
        "skills": ["Network Security", "SIEM", "Firewall", "Encryption", "Incident Response", "Penetration Testing", "Compliance"],
        "academic_background": "Bachelor's in Cybersecurity, CISSP Certified",
        "experience": 7,
        "document_parsed_cv": {
            "experience_years": 7,
            "technical_skills": ["Network Security", "SIEM", "Incident Response", "Penetration Testing"],
            "education": "BS Cybersecurity, CISSP",
            "achievements": ["Led security audit", "Reduced breach risk by 50%"]
        }
    },

    # Candidate 8: Senior Frontend Developer
    {
        "first_name": "Jennifer",
        "last_name": "Lee",
        "self_promotion": "Senior Frontend Developer with 6 years of React expertise. Passionate about performance optimization and accessibility.",
        "skills": ["React", "TypeScript", "JavaScript", "Redux", "CSS", "HTML", "Webpack", "Performance Optimization"],
        "academic_background": "Bachelor's in Computer Science",
        "experience": 6,
        "document_parsed_cv": {
            "experience_years": 6,
            "technical_skills": ["React", "TypeScript", "JavaScript", "Redux", "CSS", "Performance"],
            "education": "BS Computer Science",
            "achievements": ["Led 5+ frontend projects", "Improved page load time by 60%"]
        }
    },

    # Candidate 9: Golang Backend Developer
    {
        "first_name": "Thomas",
        "last_name": "Anderson",
        "self_promotion": "Backend Developer specializing in Golang with 4 years of experience building microservices. Strong PostgreSQL expertise.",
        "skills": ["Golang", "REST APIs", "PostgreSQL", "Docker", "Kubernetes", "gRPC", "Microservices", "MySQL"],
        "academic_background": "Bachelor's in Computer Science",
        "experience": 4,
        "document_parsed_cv": {
            "experience_years": 4,
            "technical_skills": ["Golang", "REST APIs", "PostgreSQL", "Docker", "gRPC", "Microservices"],
            "education": "BS Computer Science",
            "achievements": ["Architected microservices", "Handled 1M+ requests/day"]
        }
    },

    # Candidate 10: ML Engineer
    {
        "first_name": "Rachel",
        "last_name": "Brown",
        "self_promotion": "ML Engineer with 4 years of experience in deep learning and production ML systems. Expert in TensorFlow and PyTorch.",
        "skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "Statistics", "Scikit-learn", "AWS SageMaker", "SQL"],
        "academic_background": "Master's in Machine Learning",
        "experience": 4,
        "document_parsed_cv": {
            "experience_years": 4,
            "technical_skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "AWS SageMaker"],
            "education": "MS Machine Learning",
            "achievements": ["Deployed 3 production ML models", "Achieved 95% accuracy"]
        }
    },

    # Candidate 11: Full stack developer (matches multiple roles)
    {
        "first_name": "Kevin",
        "last_name": "Zhang",
        "self_promotion": "Full-stack developer with expertise in both frontend and backend. Experienced in React, Node.js, and PostgreSQL.",
        "skills": ["React", "Node.js", "JavaScript", "PostgreSQL", "REST APIs", "Docker", "Git", "SQL", "HTML", "CSS"],
        "academic_background": "Bachelor's in Computer Science",
        "experience": 5,
        "document_parsed_cv": {
            "experience_years": 5,
            "technical_skills": ["React", "Node.js", "JavaScript", "PostgreSQL", "REST APIs", "Docker"],
            "education": "BS Computer Science",
            "achievements": ["Built scalable web platform", "Lead 3 developers"]
        }
    },

    # Candidate 12: Junior developer (various skills)
    {
        "first_name": "Alex",
        "last_name": "Garcia",
        "self_promotion": "Junior developer transitioning from bootcamp to industry. Comfortable with Python, JavaScript, and basic cloud concepts.",
        "skills": ["Python", "JavaScript", "React", "SQL", "Git", "REST APIs", "HTML", "CSS", "Basics"],
        "academic_background": "Coding Bootcamp Graduate",
        "experience": 1,
        "document_parsed_cv": {
            "experience_years": 1,
            "technical_skills": ["Python", "JavaScript", "React", "SQL", "REST APIs"],
            "education": "Coding Bootcamp",
            "achievements": ["Completed boot camp", "Built 3 projects"]
        }
    },

    # Candidate 13: Systems administrator (partial match for DevOps)
    {
        "first_name": "Patricia",
        "last_name": "Thompson",
        "self_promotion": "Systems admin with 6 years of Linux server management. Recently started learning Docker and cloud platforms.",
        "skills": ["Linux", "Bash", "AWS Basics", "Docker", "Networking", "Ubuntu", "CentOS", "Monitoring"],
        "academic_background": "Bachelor's in Information Systems",
        "experience": 6,
        "document_parsed_cv": {
            "experience_years": 6,
            "technical_skills": ["Linux", "Bash", "AWS Basics", "Docker", "Networking"],
            "education": "BS Information Systems",
            "achievements": ["Managed 50+ servers", "99.9% uptime"]
        }
    },

    # Candidate 14: Flutter developer (mobile)
    {
        "first_name": "Marcus",
        "last_name": "Davis",
        "self_promotion": "Flutter specialist with 3 years of cross-platform mobile development. Strong Dart and Firebase expertise.",
        "skills": ["Flutter", "Dart", "Firebase", "Mobile UI/UX", "REST APIs", "Git", "iOS", "Android", "SQLite"],
        "academic_background": "Bachelor's in Software Development",
        "experience": 3,
        "document_parsed_cv": {
            "experience_years": 3,
            "technical_skills": ["Flutter", "Dart", "Firebase", "REST APIs", "Mobile Design"],
            "education": "BS Software Development",
            "achievements": ["Published 2 Flutter apps", "50K+ downloads"]
        }
    },

    # Candidate 15: Data Scientist + Engineer hybrid
    {
        "first_name": "Nina",
        "last_name": "Gupta",
        "self_promotion": "Data professional with strong ML and engineering background. Comfortable with Python, Spark, and production ML deployment.",
        "skills": ["Python", "Spark", "SQL", "TensorFlow", "Machine Learning", "Scikit-learn", "Kafka", "Big Data"],
        "academic_background": "Master's in Statistics",
        "experience": 5,
        "document_parsed_cv": {
            "experience_years": 5,
            "technical_skills": ["Python", "Spark", "SQL", "TensorFlow", "Machine Learning"],
            "education": "MS Statistics",
            "achievements": ["Built recommendation engine", "Processed 100GB+ data"]
        }
    },
]


# ============================================================================
# MAIN FUNCTION - Insert all jobs and candidates
# ============================================================================
async def insert_all_data():
    """Insert multiple jobs and candidates into the database"""

    async with AsyncSessionLocal() as session:
        try:
            print("\n" + "="*80)
            print("INSERTING MULTIPLE JOBS AND CANDIDATES")
            print("="*80 + "\n")

            # ========== INSERT JOBS ==========
            print("📝 INSERTING JOBS:")
            print("-" * 80)

            for job_id, config in JOBS_CONFIG.items():
                job_query = select(Job).where(Job.job_id == job_id)
                existing_job = await session.execute(job_query)
                job_exists = existing_job.scalar_one_or_none()

                if job_exists:
                    print(f"  Job ID {job_id}: {config['title']} (UPDATED)")
                    job_exists.job_title = config["title"]
                    job_exists.job_description = config["description"]
                    job_exists.required_skills_text = config["skills"]
                    job_exists.required_qualification = config["qualification"]
                    job_exists.job_status = "Open"
                    job_exists.organization_id = 1
                else:
                    print(f"  Job ID {job_id}: {config['title']} (CREATED)")
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

            await session.commit()
            print(f"\n✅ Total jobs: {len(JOBS_CONFIG)} jobs processed\n")

            # ========== INSERT CANDIDATES ==========
            print("👥 INSERTING CANDIDATES:")
            print("-" * 80)

            # Get existing candidates count
            candidates_query = select(CandidatePool).where(CandidatePool.company_id == 1)
            existing_candidates = await session.execute(candidates_query)
            existing_count = len(existing_candidates.scalars().all())

            for i, cand_config in enumerate(CANDIDATES_CONFIG, 1):
                candidate = CandidatePool(
                    company_id=1,
                    first_name=cand_config["first_name"],
                    last_name=cand_config["last_name"],
                    self_promotion=cand_config["self_promotion"],
                    skill=cand_config["skills"],
                    academic_background=cand_config["academic_background"],
                    experience=cand_config["experience"],
                    document_parsed_cv=cand_config["document_parsed_cv"]
                )
                session.add(candidate)
                print(f"  Candidate {existing_count + i}: {cand_config['first_name']} {cand_config['last_name']} ({cand_config['experience']} yrs, Skills: {len(cand_config['skills'])})")

            await session.commit()
            print(f"\n✅ Total candidates: {len(CANDIDATES_CONFIG)} candidates created\n")

            # ========== GENERATE EMBEDDINGS ==========
            print("🔧 GENERATING EMBEDDINGS:")
            print("-" * 80)

            matcher = AIMatcherService()
            jobs_needing_embedding = []

            for job_id in JOBS_CONFIG.keys():
                job_query = select(Job).where(Job.job_id == job_id)
                job_result = await session.execute(job_query)
                job = job_result.scalar_one_or_none()
                if job and not job.embedding:
                    jobs_needing_embedding.append(job)

            if jobs_needing_embedding:
                print(f"  Generating embeddings for {len(jobs_needing_embedding)} jobs...")
                texts = [f"{j.job_title} {j.job_description}" for j in jobs_needing_embedding]
                new_embeddings = await matcher.get_embeddings_batch(texts)

                for job, emb in zip(jobs_needing_embedding, new_embeddings):
                    job.embedding = emb

                await session.commit()
                print(f"  ✅ Generated {len(jobs_needing_embedding)} embeddings")
            else:
                print("  ℹ️  All jobs already have embeddings")

            print("\n" + "="*80)
            print("✅ ALL DATA INSERTED SUCCESSFULLY!")
            print("="*80 + "\n")

            print("📊 SUMMARY:")
            print(f"  • Total Jobs: {len(JOBS_CONFIG)}")
            print(f"  • Total New Candidates: {len(CANDIDATES_CONFIG)}")
            print(f"  • Job Titles: {', '.join([JOBS_CONFIG[jid]['title'] for jid in sorted(JOBS_CONFIG.keys())[:3]])}...")
            print(f"  • Candidate Profiles: Various skill levels and job domains\n")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(insert_all_data())

