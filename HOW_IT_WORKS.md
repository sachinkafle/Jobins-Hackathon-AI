# 🎯 Complete Guide: How the AI Job Matching System Works

## 📋 Overview

Your job matching system uses **AI-powered semantic matching** to find the best candidate-job pairs. Here's the complete breakdown of how everything works together.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Database (MySQL)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │  Jobs Table  │  │ Candidates   │  │ Selection History  │    │
│  │  (pb_job)    │  │ (candidate   │  │ (Stores Results)   │    │
│  │              │  │  _pool)      │  │                    │    │
│  └──────────────┘  └──────────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│              API Layer (FastAPI Endpoints)                       │
│  POST /api/v1/job-to-candidates  ← Job ID → Get matching candidates
│  POST /api/v1/candidate-to-jobs  ← Candidate ID → Get matching jobs
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│           AI Matching Engine (AIMatcherService)                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Fetch from Database                                    │ │
│  │  2. Generate/Use Embeddings (OpenAI API)                  │ │
│  │  3. Calculate Semantic Similarity (Cosine Distance)        │ │
│  │  4. AI Scoring with LLM (GPT-4o-mini)                     │ │
│  │  5. Save Results to Database                              │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Step-by-Step Matching Process

### **When you call: POST /api/v1/job-to-candidates with job_id**

```python
{
  "job_id": 1001
}
```

Here's what happens internally:

---

### **STEP 1: Fetch Job Details from Database**

```python
# File: app/services/ai_matcher.py (line 166-169)
query = select(Job).where(Job.job_id == job_id)
res = await session.execute(query)
job = res.scalar_one_or_none()
```

**What it does:**
- Queries the `pb_job` table
- Gets job title, description, required_skills_text, required_qualification
- Checks if job exists and has valid data

**Example Data Retrieved:**
```python
Job(
  job_id=1001,
  job_title="Cloud Infrastructure Engineer",
  job_description="We are looking for an experienced Cloud Infrastructure Engineer...",
  required_skills_text="AWS, GCP, Kubernetes, Terraform, Docker, CI/CD, Linux, Prometheus",
  required_qualification="Bachelor's in Computer Science"
)
```

---

### **STEP 2: Fetch All Candidates (Up to 20 by default)**

```python
# File: app/services/ai_matcher.py (line 171-173)
candidates_query = select(CandidatePool).where(
    CandidatePool.company_id == (company_id or job.organization_id)
).limit(20)
cands_res = await session.execute(candidates_query)
candidates = cands_res.scalars().all()
```

**What it does:**
- Gets all candidates from the same company/organization
- Limited to 20 candidates for performance
- Fetches: name, skills, experience, CV data, background

**Example Data Retrieved:**
```python
Candidate(
  id=290,
  first_name="Michael",
  last_name="Chen",
  skill=["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD", "Linux", "Prometheus"],
  experience=5,
  academic_background="Bachelor's in Computer Science"
)
```

---

### **STEP 3: Create Formatted Text for Each Candidate**

```python
# File: app/services/ai_matcher.py (line 175)
tasks = [
  self.score_match(
    f"{c.first_name} {c.skill}",  # Candidate info
    f"{job.job_title} {job.job_description}"  # Job info
  ) 
  for c in candidates
]
```

**What it creates:**

**Candidate Text:**
```
Michael Chen ['AWS', 'Kubernetes', 'Docker', 'Terraform', 'CI/CD', 'Linux', 'Prometheus', 'Bash']
```

**Job Text:**
```
Cloud Infrastructure Engineer. We are looking for an experienced Cloud Infrastructure Engineer...
Requirements:
- 4+ years of cloud infrastructure experience
- Strong expertise in AWS or GCP
- Knowledge of Kubernetes and container orchestration
[...more requirements...]
```

---

### **STEP 4: Call AI Model with Prompts**

```python
# File: app/services/ai_matcher.py (line 61-68)
prompt = ChatPromptTemplate.from_messages([
    ("system", MATCHING_SYSTEM_PROMPT),
    ("user", MATCHING_USER_PROMPT)
])

chain = prompt | self.llm
response = await chain.ainvoke({
    "candidate": candidate_info,
    "job": job_info
})
```

**The System Prompt (Hard Rules):**
```
See: app/services/prompts.py (lines 1-29)

Key Rules:
- IF Job Requirements are EMPTY → return score 0
- NO assumptions if requirements are missing
- Be skeptical about high scores

Scoring Bands:
- 90-100: Exceptional Match
- 70-89: Strong Match
- 50-69: Average Match
- 1-49: Poor Match
- 0: No Match OR Missing Data
```

**The User Prompt:**
```
Evaluate this pair:

[CANDIDATE PROFILE]
{candidate_info}

[JOB REQUIREMENTS]
{job_info}

Final Recommendation:
```

**What GPT-4o-mini Returns:**
```json
{
  "score": 85,
  "reasoning": "The candidate has strong technical alignment with key skills such as 
  AWS, Kubernetes, Docker, Terraform, CI/CD, Linux, and Prometheus. With the requirement 
  of 4+ years of cloud infrastructure experience, the candidate's profile suggests a solid 
  foundation in relevant technologies, indicating a strong fit for the role..."
}
```

---

### **STEP 5: Process All Candidates in Parallel (Async)**

```python
# File: app/services/ai_matcher.py (line 176-177)
scores = await asyncio.gather(*tasks)  # Run all in parallel

# Gather all candidates with their scores
results = []
for cand, score_data in zip(candidates, scores):
    results.append(CandidateMatchResult(
        candidate_id=cand.id,
        score=score_data.get("score", 0),
        reasoning=score_data.get("reasoning", "")
    ))
```

**Why Parallel Processing?**
- Instead of scoring candidates one-by-one (20s+ for 20 candidates)
- Score all candidates simultaneously using `asyncio.gather()`
- Reduces total time from 20 seconds to ~2 seconds ⚡

---

### **STEP 6: Save Results to Database**

```python
# File: app/services/ai_matcher.py (line 50-59)
async def save_match_result(self, session, candidate_id, job_id, score, reasoning):
    new_history = SelectionHistory(
        candidate_id=candidate_id,
        job_id=job_id,
        match_score=score,
        match_reason=reasoning
    )
    session.add(new_history)
    await session.flush()
```

**Storage:**
```sql
INSERT INTO selection_history 
  (candidate_id, job_id, match_score, match_reason)
VALUES 
  (290, 1001, 85, "The candidate has strong technical alignment...")
```

---

### **STEP 7: Return Sorted Results**

```python
# File: app/services/ai_matcher.py (line 182-183)
results.sort(key=lambda x: x.score, reverse=True)
return results
```

**Final Response:**
```json
{
  "results": [
    {
      "candidate_id": 290,
      "score": 85,
      "reasoning": "Strong match due to AWS, Kubernetes expertise..."
    },
    {
      "candidate_id": 292,
      "score": 70,
      "reasoning": "Good match but missing Terraform experience..."
    },
    {
      "candidate_id": 302,
      "score": 30,
      "reasoning": "Poor match - lacks cloud platform experience..."
    }
    // ... more results sorted by score
  ]
}
```

---

## 📊 Data Creation Script: What We Built

### File: `app/db/create_many_jobs_candidates.py`

This script does three things:

### **1️⃣ CREATE 10 JOBS across different domains:**

```python
JOBS_CONFIG = {
    1001: {
        "title": "Cloud Infrastructure Engineer",
        "skills": "AWS, GCP, Kubernetes, Terraform, Docker, CI/CD, Linux, Prometheus",
        # + detailed description
    },
    1002: {
        "title": "Mobile App Developer",
        "skills": "React Native, Flutter, Swift, Kotlin, Mobile UI/UX, REST APIs, SQLite, Firebase",
        # + detailed description
    },
    1003: {
        "title": "DevOps Engineer",
        # ... and 7 more jobs
    },
    # [... covering Cloud, Mobile, DevOps, QA, Product, Data, Security, Frontend, Backend, ML ...]
}
```

**Why 10 different jobs?**
- Shows matching across diverse technical domains
- Demonstrates how different skill sets match different roles
- Tests the system with realistic variety

---

### **2️⃣ CREATE 15 CANDIDATES with varied profiles:**

```python
CANDIDATES_CONFIG = [
    # Specialist 1: Cloud Expert
    {
        "first_name": "Michael",
        "last_name": "Chen",
        "skills": ["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD", "Linux", "Prometheus"],
        "experience": 5,
        # Perfect for Cloud Infrastructure job ✅
    },
    
    # Specialist 2: Mobile Developer
    {
        "first_name": "Sarah",
        "last_name": "Johnson",
        "skills": ["React Native", "JavaScript", "Firebase", "REST APIs", "Mobile UI/UX"],
        "experience": 4,
        # Perfect for Mobile App Developer job ✅
    },
    
    # Hybrid: Full Stack Developer
    {
        "first_name": "Kevin",
        "last_name": "Zhang",
        "skills": ["React", "Node.js", "JavaScript", "PostgreSQL", "REST APIs", "Docker"],
        "experience": 5,
        # Matches both Frontend AND Backend jobs ✅
    },
    
    # Junior: Low experience
    {
        "first_name": "Alex",
        "last_name": "Garcia",
        "skills": ["Python", "JavaScript", "React", "SQL", "Git"],
        "experience": 1,
        # May match entry-level positions
    },
    
    # ... 11 more candidates with different specialties
]
```

**Why 15 candidates?**
- Provides variety to match different job requirements
- Some are perfect matches (score 80+)
- Some have partial skills (score 40-70)
- Some are mismatched (score 0-10)
- Shows the full spectrum of matching quality

---

### **3️⃣ GENERATE EMBEDDINGS (Vector Representations):**

```python
# File: app/db/create_many_jobs_candidates.py (line 230-242)
matcher = AIMatcherService()
texts = [f"{j.job_title} {j.job_description}" for j in jobs_needing_embedding]
new_embeddings = await matcher.get_embeddings_batch(texts)

for job, emb in zip(jobs_needing_embedding, new_embeddings):
    job.embedding = emb
```

**What are embeddings?**
- Convert text (job description) to 1536-dimensional vector
- Used for semantic similarity calculations
- Allows finding similar jobs/candidates even if keywords don't match exactly

**Example:** 
```
Job: "Build mobile apps with React Native"
Embedding: [0.123, -0.045, 0.678, ..., 0.234] (1536 numbers)

This embedding captures the semantic meaning of "mobile app development"
Even if another job says "Create iOS applications using Swift",
it would have a similar embedding and be recognized as related
```

---

## 🎯 How Matching Quality Works

### **The Matching Algorithm (2-Stage Process)**

#### **Original System (in match_candidate_to_jobs):**

1. **Stage 1: Semantic Search (Fast Filter)**
   - Calculate cosine similarity between candidate and job embeddings
   - Pick top 10 most relevant matches
   - Eliminates obviously incompatible candidates quickly

2. **Stage 2: AI Reranking (Accurate Scoring)**
   - Feed top 10 candidates to GPT-4o-mini
   - AI model evaluates deep alignment
   - Returns score 0-100 with detailed reasoning
   - Saves results to database

#### **Why 2 Stages?**
- ⚡ **Performance**: Embedding similarity is fast (math only)
- 🧠 **Accuracy**: AI scoring is slow but accurate (API call)
- 💰 **Cost**: Reduces AI API calls from N (all candidates) to 10
- 🎯 **Quality**: Best of both worlds

### **Job-to-Candidates (Your Use Case)**

```python
# Simplified approach - doesn't use semantic search stage
tasks = [
  self.score_match(candidate_text, job_text) 
  for c in candidates
]
scores = await asyncio.gather(*tasks)
```

**Process:**
1. Get all candidates for the company (limit 20)
2. Score each candidate against the job using AI
3. Return sorted by score (highest first)

---

## 📈 Real Matching Results from Your System

### **Test 1: Cloud Infrastructure Engineer (Job ID 1001)**

```
Candidate: Michael Chen (Cloud Expert)
Skills: AWS, Kubernetes, Docker, Terraform, CI/CD, Linux, Prometheus
Score: 85 ✅ STRONG MATCH

Reasoning: "Strong technical alignment with key skills such as AWS, 
Kubernetes, Docker, Terraform, CI/CD, Linux, and Prometheus. With the 
requirement of 4+ years of cloud infrastructure experience, the 
candidate's profile suggests a solid foundation..."

---

Candidate: David Kumar (DevOps Engineer)
Skills: Docker, Kubernetes, Python, Bash, Jenkins, GitLab CI, AWS, Monitoring
Score: 70 ✅ GOOD MATCH

Reasoning: "Strong expertise in Kubernetes, AWS, and CI/CD tools align 
well with requirements. However, lacks specific experience with 
Infrastructure as Code tools like Terraform or CloudFormation..."

---

Candidate: Jennifer Lee (Senior Frontend Dev)
Skills: React, TypeScript, JavaScript, Redux, CSS, HTML, Webpack
Score: 1 ❌ POOR MATCH

Reasoning: "Candidate's technical skills primarily focus on frontend 
development, which do not align with cloud infrastructure requirements. 
Lacks cloud platforms, Kubernetes, and Infrastructure as Code experience..."
```

### **Test 2: Mobile App Developer (Job ID 1002)**

```
Candidate: Marcus Davis (Flutter Specialist)
Skills: Flutter, Dart, Firebase, Mobile UI/UX, REST APIs, Git, iOS, Android
Score: 85 ✅ STRONG MATCH

---

Candidate: Sarah Johnson (React Native Dev)
Skills: React Native, JavaScript, Firebase, REST APIs, Mobile UI/UX
Score: 70 ✅ GOOD MATCH

---

Candidate: Thomas Anderson (Golang Backend Dev)
Skills: Golang, REST APIs, PostgreSQL, Docker, Kubernetes, gRPC
Score: 20 ❌ WEAK MATCH

Reasoning: "Lacks mobile app development experience. Background is in 
backend web development, not mobile-specific technologies..."
```

### **Test 3: Data Engineer (Job ID 1006)**

```
Candidate: Lisa Patel (Data Engineer)
Skills: Python, Spark, SQL, Kafka, Data Warehousing, ETL, Airflow, Snowflake
Score: 85 ✅ PERFECT MATCH

---

Candidate: Nina Gupta (Data Scientist + Engineer)
Skills: Python, Spark, SQL, TensorFlow, Machine Learning, Scikit-learn
Score: 70 ✅ GOOD MATCH

(Strong in data tools, but lacks specific data warehouse experience)

---

Candidate: Michael Chen (Cloud Infrastructure)
Skills: AWS, Kubernetes, Docker, Terraform, CI/CD
Score: 1 ❌ NO MATCH

Reasoning: "Lacks experience in data engineering, big data technologies, 
and SQL expertise. Cloud infrastructure skills don't transfer to data 
engineering requirements..."
```

---

## 🚀 How to Run Everything

### **1. Create All Jobs and Candidates:**
```bash
cd /Users/binaya/code/hackathon/Jobins-Hackathon-AI
python -m app.db.create_many_jobs_candidates
```

**Output:**
```
================================================================================
INSERTING MULTIPLE JOBS AND CANDIDATES
================================================================================

📝 INSERTING JOBS:
  Job ID 1001: Cloud Infrastructure Engineer (CREATED)
  Job ID 1002: Mobile App Developer (CREATED)
  [... 10 jobs total ...]

✅ Total jobs: 10 jobs processed

👥 INSERTING CANDIDATES:
  Candidate 6: Michael Chen (5 yrs, Skills: 8)
  Candidate 7: Sarah Johnson (4 yrs, Skills: 8)
  [... 15 candidates total ...]

✅ Total candidates: 15 candidates created

🔧 GENERATING EMBEDDINGS:
  Generating embeddings for 10 jobs...
  ✅ Generated 10 embeddings

✅ ALL DATA INSERTED SUCCESSFULLY!
```

### **2. Start the Server:**
```bash
python app/main.py
```

### **3. Test Job Matching:**
```bash
# Test Cloud Infrastructure Engineer
curl -X POST http://127.0.0.1:8000/api/v1/job-to-candidates \
  -H "Content-Type: application/json" \
  -d '{"job_id": 1001}'

# Test Mobile App Developer
curl -X POST http://127.0.0.1:8000/api/v1/job-to-candidates \
  -H "Content-Type: application/json" \
  -d '{"job_id": 1002}'

# Test Data Engineer
curl -X POST http://127.0.0.1:8000/api/v1/job-to-candidates \
  -H "Content-Type: application/json" \
  -d '{"job_id": 1006}'
```

### **4. Get Results:**
```json
{
  "results": [
    {
      "candidate_id": 290,
      "score": 85,
      "reasoning": "The candidate has strong technical alignment..."
    },
    {
      "candidate_id": 292,
      "score": 70,
      "reasoning": "Good match but missing some requirements..."
    }
  ]
}
```

---

## 🔧 Key Technologies Used

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM Model** | GPT-4o-mini | AI score calculation |
| **Embeddings** | OpenAI text-embedding-3-small | Semantic similarity |
| **Framework** | FastAPI | REST API endpoints |
| **Database** | MySQL (async) | Store jobs, candidates, results |
| **Language** | Python 3.14 | Backend logic |
| **Async** | asyncio | Parallel processing |
| **ORM** | SQLAlchemy | Database queries |

---

## 📦 Files Created

```
/app/db/
├── create_many_jobs_candidates.py  ← Main data creation script
├── insert_test_data.py             ← Original test data (3 jobs)
├── populate_embeddings.py          ← Generate embeddings
├── init_db.py                      ← Database initialization
└── database.py                     ← DB connection setup

/app/services/
├── ai_matcher.py                   ← Matching algorithm
├── prompts.py                      ← AI prompts (system + user)
└── resume_parser.py                ← Resume parsing

/app/api/
└── endpoints.py                    ← API routes

/app/models/
├── db_models.py                    ← Database schema
└── schemas.py                      ← Pydantic schemas
```

---

## ✅ Summary

**What we built:**
1. ✅ 10 different jobs spanning multiple tech domains
2. ✅ 15 candidates with varied skill levels
3. ✅ AI-powered job-to-candidate matching
4. ✅ Real-time scoring with explanations
5. ✅ Database persistence of results

**How it works:**
1. You send a job_id to the API
2. System fetches job details
3. Retrieves all candidates
4. AI scores each candidate against the job
5. Returns ranked results with reasoning
6. Saves results to database for future reference

**Technology Stack:**
- OpenAI GPT-4o-mini for scoring
- Semantic embeddings for similarity
- FastAPI for REST endpoints
- MySQL for data persistence
- asyncio for parallel processing

You can now run `/api/v1/job-to-candidates` with any job_id and get quality matches! 🎉

