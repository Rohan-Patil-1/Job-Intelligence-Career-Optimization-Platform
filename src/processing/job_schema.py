from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class JobRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    source: str = Field(min_length=1)
    source_job_id: Optional[str] = None

    title: str = Field(min_length=1)
    company: str = Field(min_length=1)

    location: Optional[str] = None
    remote_type: Optional[str] = None
    employment_type: Optional[str] = None

    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None

    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    skills: Optional[str] = None

    job_url: str = Field(min_length=1)

    posted_at: Optional[datetime] = None
    collected_at: datetime