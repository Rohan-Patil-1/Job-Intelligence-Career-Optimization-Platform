from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from src.database.mappers import job_record_to_model
from src.database.repository import JobRepository
from src.ingestion.base import JobSource
from src.processing.normalizer import normalize_job


@dataclass
class IngestionError:
    source_job_id: str | None
    error_type: str
    message: str


@dataclass
class IngestionResult:
    fetched: int = 0
    inserted: int = 0
    duplicates: int = 0
    failed: int = 0
    errors: list[IngestionError] = field(default_factory=list)


def ingest_jobs(
    source: JobSource,
    session: Session,
    query: str,
    location: str,
) -> IngestionResult:
    """Fetch, normalize, deduplicate, and persist jobs."""

    repository = JobRepository(session)

    raw_jobs = source.fetch_jobs(
        query=query,
        location=location,
    )

    result = IngestionResult(fetched=len(raw_jobs))

    for raw_job in raw_jobs:
        source_job_id = raw_job.get("source_job_id")

        try:
            job_record = normalize_job(raw_job)
            job_model = job_record_to_model(job_record)

            _, inserted = repository.add_if_new(job_model)

            if inserted:
                result.inserted += 1
            else:
                result.duplicates += 1

        except Exception as exc:
            result.failed += 1

            result.errors.append(
                IngestionError(
                    source_job_id=source_job_id,
                    error_type=type(exc).__name__,
                    message=str(exc),
                )
            )

    session.commit()

    return result