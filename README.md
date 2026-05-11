# AI Hiring Intelligence System - AI Engine

FastAPI microservice for intelligent candidate-job matching and automated resume parsing.

## Features
- **AI Match Scoring**: Semantic matching between candidates and jobs with detailed reasoning.
- **Resume Parsing**: Automated extraction of structured data from PDF resumes (S3/Local/URL) into a comprehensive candidate profile.

## Setup Instructions (using uv)

### 1. Environment & Requirements
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment with uv
uv venv

# Activate environment
source .venv/bin/activate

# Install dependencies fast with uv
uv pip install -r requirements.txt

# Create missing database tables and columns
uv run python -m app.db.init_db

# Populate embeddings for existing jobs (run this once)
uv run python -m app.db.populate_embeddings

# test pdf parsing
uv run python app/tests/test_ai_parsing.py "natsudukiouka---中村翔太 (1).pdf"
```

### 2. Configuration (.env)
Create a `.env` file from the example:
```bash
cp .env.example .env
```
Update the `.env` file with your **OpenAI API Key** and **AWS S3 Credentials**:
```env
DATABASE_URL=mysql+aiomysql://local:secret@localhost/sasuke_new
OPENAI_API_KEY=your_actual_key_here
OPENAI_MODEL=gpt-4o-mini

# AWS S3 Configuration (Required for S3 resume parsing)
AWS_ACCESS_KEY_ID=your_aws_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
AWS_REGION=your_aws_region_here
AWS_S3_BUCKET=your_s3_bucket_name_here
```

### 3. Run the Service
```bash
uvicorn app.main:app --reload
```

## API Usage

### Resume Parsing
**Endpoint:** `POST /api/v1/parse-resume`

Extracts structured data from a PDF resume. Supports S3 URIs, public URLs, or local filenames (if `AWS_S3_BUCKET` is configured or file exists locally).

**Request:**
```json
{
    "file_path": "resume.pdf",
    "file_name": "resume.pdf",
    "upload_name": "my_resume.pdf"
}
```

*Note: `file_name` and `upload_name` are optional.*

*Note: If `file_path` is just a filename and `AWS_S3_BUCKET` is set, the service will first try to download it from that S3 bucket.*

### AI Match Scoring
**Endpoint:** `POST /api/v1/candidate-to-jobs`
Finds the best jobs for a specific candidate.

**Endpoint:** `POST /api/v1/job-to-candidates`
Finds the best candidates for a specific job.

## API Documentation
Once running, visit:
**Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
