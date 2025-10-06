from pydantic import BaseModel
from typing import Optional

class JobCreateResponse(BaseModel):
    job_id: str

class Job(BaseModel):
    id: str
    status: str
    prompt: Optional[str]
    original_path: Optional[str]
    result_url: Optional[str]