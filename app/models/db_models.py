from sqlalchemy import Column, Integer, String, Text, BigInteger, Boolean, DateTime, JSON
from app.db.database import Base

class CandidatePool(Base):
    __tablename__ = "candidate_pool"
    id = Column(BigInteger, primary_key=True, index=True)
    company_id = Column(Integer)
    first_name = Column(String(255))
    last_name = Column(String(255))
    self_promotion = Column(Text)
    skill = Column(JSON)
    academic_background = Column(String(255))
    experience = Column(Integer)
    document_parsed_cv = Column(JSON)

class Job(Base):
    __tablename__ = "pb_job"
    job_id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer) # Maps to company_id
    job_title = Column(Text)
    job_description = Column(Text)
    required_skills_text = Column(Text)
    required_qualification = Column(Text)
    job_status = Column(String(50)) # 'Open', 'Close', etc.
    embedding = Column(JSON) # To store the vector

class SelectionHistory(Base):
    __tablename__ = "selection_history"
    id = Column(BigInteger, primary_key=True, index=True)
    candidate_id = Column(BigInteger)
    job_id = Column(Integer)
    match_score = Column(Integer)
    match_reason = Column(Text)
    recommended_bulk = Column(Boolean, default=True)
