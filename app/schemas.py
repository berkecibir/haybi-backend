from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobCreateResponse(BaseModel):
    job_id: str

class Job(BaseModel):
    id: str
    status: str
    prompt: Optional[str]
    original_path: Optional[str]
    result_url: Optional[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None