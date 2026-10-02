from src.database.models import Job
from src.processing.job_schema import JobRecord


def job_record_to_model(job_record: JobRecord) -> Job:
    """Convert a validated JobRecord into a SQLAlchemy Job model."""

    return Job(
        source=job_record.source,
        source_job_id=job_record.source_job_id,
        title=job_record.title,
        company=job_record.company,
        location=job_record.location,
        remote_type=job_record.remote_type,
        employment_type=job_record.employment_type,
        salary_min=job_record.salary_min,
        salary_max=job_record.salary_max,
        salary_currency=job_record.salary_currency,
        description=job_record.description,
        requirements=job_record.requirements,
        responsibilities=job_record.responsibilities,
        skills=job_record.skills,
        job_url=job_record.job_url,
        posted_at=job_record.posted_at,
        collected_at=job_record.collected_at,
    )