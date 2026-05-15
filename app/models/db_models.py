from sqlalchemy import Column, Integer, String, Text, BigInteger, Boolean, DateTime, JSON
from app.db.database import Base

class CandidatePool(Base):
    __tablename__ = "candidate_pool"
    id = Column(BigInteger, primary_key=True, index=True)
    company_id = Column(Integer)
    first_name = Column(String(255))
    last_name = Column(String(255))
    furigana_first_name = Column(String(255))
    furigana_last_name = Column(String(255))
    gender = Column(String(255))
    dob = Column(String(50))
    nationality = Column(String(255))
    phone = Column(String(255))
    email = Column(String(255))
    # Education & skills
    academic_background = Column(String(255))
    educational_background_details = Column(Text)
    literature_and_science_classification = Column(String(255))
    skill = Column(JSON)
    qualification = Column(JSON)
    education = Column(JSON)
    # Languages
    japanese_skills = Column(String(255))
    english_skills = Column(String(255))
    chinese_skills = Column(String(255))
    other_languages = Column(Text)
    toeic = Column(Integer)
    toefl = Column(Integer)
    # Experience
    experience = Column(Integer)
    years_of_industry_experience = Column(Integer)
    no_of_company_change = Column(Integer)
    current_employment_status = Column(String(255))
    current_employment_type = Column(String(255))
    current_position = Column(String(255))
    current_year_salary = Column(Integer)
    most_recent_workplace = Column(String(255))
    # Self promotion & CV data
    self_promotion = Column(Text)
    document_parsed_cv = Column(JSON)
    document_parsed_resume = Column(JSON)
    employment_histories = Column(JSON)
    # Desired conditions
    desired_job_change_timing = Column(String(255))
    desired_job_change_motivation = Column(String(255))
    desired_employment_type = Column(JSON)
    desired_position = Column(String(255))
    min_desire_salary = Column(Integer)
    relocation = Column(String(255))
    # Location
    postal_code = Column(String(255))
    address_details = Column(String(255))
    nearest_station = Column(String(255))
    specified_desired_locations = Column(JSON)
    specified_desired_occupations = Column(JSON)
    specified_desired_sub_industries = Column(JSON)
    # Misc
    self_promotion = Column(Text)
    candidate_rank = Column(String(255))
    candidate_personality = Column(Text)
    job_change_axis = Column(Text)
    job_support_factors = Column(Text)
    job_change_restrictions = Column(Text)
    embedding = Column(JSON) # To store the vector

class Job(Base):
    __tablename__ = "pb_job"
    job_id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer) # Maps to company_id
    job_title = Column(Text)
    job_description = Column(Text)
    job_responsibilities = Column(Text)
    application_condition = Column(Text)
    welcome_condition = Column(Text)
    job_change_possibility_description = Column(Text)
    minimum_education_level = Column(Text)
    minimum_job_experience = Column(Text)
    minimum_industry_experience = Column(Text)
    employment_status = Column(Text)
    job_employment_category = Column(JSON)
    experience = Column(Text)
    academic_level = Column(Text)
    pref_nationality = Column(Text)
    gender = Column(Text)
    age_min = Column(Text)
    age_max = Column(Text)
    min_year_salary = Column(Text)
    max_year_salary = Column(Text)
    min_month_salary = Column(Text)
    max_month_salary = Column(Text)
    location_desc = Column(Text)
    working_hours = Column(Text)
    holidays = Column(Text)
    benefits = Column(Text)
    allowances = Column(Text)
    selection_flow = Column(Text)
    organization_description = Column(Text)
    recruitment_status = Column(Text)
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
