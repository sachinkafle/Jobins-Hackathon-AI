from pydantic import BaseModel
from typing import List, Optional, Any

class CandidateMatchRequest(BaseModel):
    candidate_id: int

class JobMatchRequest(BaseModel):
    job_id: int

class JobMatchResult(BaseModel):
    job_id: int
    score: int
    reasoning: str

class CandidateMatchResult(BaseModel):
    candidate_id: int
    candidate_company_id: int
    score: int
    reasoning: str

class JobMatchResponse(BaseModel):
    results: List[JobMatchResult]

class CandidateMatchResponse(BaseModel):
    results: List[CandidateMatchResult]

class ErrorResponse(BaseModel):
    detail: str

class FileInfo(BaseModel):
    url: str
    file_name: str
    upload_name: str
    uuid: Optional[Any] = False

class WorkHistory(BaseModel):
    job_change_reason: Optional[str] = None
    company_name: Optional[str] = None
    employment_date_from: Optional[str] = None
    employment_date_to: Optional[str] = None
    sub_industry_id: Optional[int] = None
    no_of_employee: Optional[int] = None
    other_details: Optional[str] = None
    industry_id: Optional[int] = None

class SkillInfo(BaseModel):
    title: str
    level: int

class ResumeData(BaseModel):
    file: Optional[FileInfo] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    furigana_last_name: Optional[str] = None
    furigana_first_name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    postal_code: Optional[str] = None
    prefecture_id: Optional[int] = None
    address_details: Optional[str] = None
    nearest_station: Optional[str] = None
    spouse: Optional[str] = None
    phone: Optional[str] = None
    phone_secondary: Optional[str] = None
    email: Optional[str] = None
    academic_background: Optional[str] = None
    literature_and_science_classification: Optional[str] = None
    educational_background_details: Optional[str] = None
    candidate_pool_qualification: Optional[List[str]] = []
    japanese_skills: Optional[str] = None
    english_skills: Optional[str] = None
    chinese_skills: Optional[str] = None
    toeic: Optional[int] = None
    toefl: Optional[int] = None
    other_languages: Optional[str] = None
    current_employment_status: Optional[str] = None
    no_of_company_change: Optional[int] = 0
    sub_job_type_id: Optional[int] = None
    sub_industry_type_id: Optional[int] = None
    experience: Optional[int] = 0
    years_of_industry_experience: Optional[int] = 0
    current_employment_type: Optional[str] = None
    current_position: Optional[str] = None
    current_year_salary: Optional[int] = None
    current_hourly_wage: Optional[int] = None
    most_recent_workplace: Optional[str] = None
    self_promotion: Optional[str] = None
    candidate_work_history: Optional[List[WorkHistory]] = []
    desired_locations: Optional[Any] = None
    location_desired: Optional[Any] = None
    desired_occupation: Optional[Any] = None
    occupation_desired: Optional[Any] = None
    candidate_specified_desired_sub_industry: Optional[Any] = None
    industry_desired: Optional[Any] = None
    desired_job_change_timing: Optional[Any] = None
    desired_job_change_motivation: Optional[Any] = None
    desired_employment_type: Optional[Any] = None
    min_desire_salary: Optional[Any] = None
    desired_hourly_wage: Optional[Any] = None
    relocation: Optional[Any] = None
    desired_position: Optional[Any] = None
    application_route_id: Optional[Any] = None
    job_offer_at_entry_time: Optional[Any] = None
    entry_date: Optional[Any] = None
    assignee_agent_id: Optional[Any] = None
    first_interview_date: Optional[Any] = None
    candidate_rank: Optional[Any] = None
    tag: Optional[Any] = None
    last_contact_date: Optional[Any] = None
    phase: Optional[Any] = None
    phase_date: Optional[Any] = None
    reason_for_release: Optional[Any] = None
    recommendation: Optional[Any] = None
    selection_status_of_other_companies: Optional[Any] = None
    job_change_restrictions: Optional[Any] = None
    job_change_axis: Optional[Any] = None
    job_support_factors: Optional[Any] = None
    acceptable_employment_types: Optional[Any] = None
    candidate_personality: Optional[Any] = None
    convenient_times_to_contact: Optional[Any] = None
    remarks: Optional[Any] = None
    data_registration_date: Optional[Any] = None
    operation_handling_classification_id: Optional[Any] = None
    validity_period_start_date: Optional[Any] = None
    validity_period_end_date: Optional[Any] = None
    job_change_prohibition_period: Optional[Any] = None
    employment_separation_date: Optional[Any] = None
    employment_confirmation_continuation_date: Optional[Any] = None
    employment_separation_survey_date: Optional[Any] = None
    refund_date: Optional[Any] = None
    termination_status_investigation: Optional[Any] = None
    system_info_remarks: Optional[Any] = None
    education: Optional[List[Any]] = []
    skills: Optional[List[SkillInfo]] = []
    document_parsed_id: Optional[int] = None

class ResumeParseResponse(BaseModel):
    success: bool
    message: str
    data: ResumeData

class ResumeParseRequest(BaseModel):
    file_path: str # Can be S3 URL, HTTPS URL, or just a filename
    file_name: Optional[str] = None
    upload_name: Optional[str] = None
