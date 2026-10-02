from datetime import datetime

from sqlalchemy.orm import Session

from src.database.models import Job
from src.ingestion.base import JobSource
from src.ingestion.pipeline import ingest_jobs


class FakeJobSource(JobSource):
    """Fake source for testing the complete ingestion pipeline."""

    def fetch_jobs(
        self,
        query: str,
        location: str,
    ) -> list[dict]:
        return [
            {
                "source": "fake",
                "source_job_id": "fake-001",
                "title": "Machine Learning Engineer",
                "company": "Test Company",
                "location": "Chicago, IL",
                "job_url": "https://example.com/job/1",
                "posted_at": "2026-09-30T12:00:00Z",
                "collected_at": datetime.utcnow(),
            },
            {
                "source": "fake",
                "source_job_id": "fake-002",
                "title": "Data Scientist",
                "company": "Another Company",
                "location": "Chicago, IL",
                "job_url": "https://example.com/job/2",
                "posted_at": "2026-09-29T12:00:00Z",
                "collected_at": datetime.utcnow(),
            },
        ]


def test_ingestion_pipeline_persists_jobs(db_session: Session):
    source = FakeJobSource()

    result = ingest_jobs(
        source=source,
        session=db_session,
        query="machine learning",
        location="Chicago",
    )

    assert result.fetched == 2
    assert result.inserted == 2
    assert result.duplicates == 0
    assert result.failed == 0

    jobs = db_session.query(Job).all()

    assert len(jobs) == 2
    assert jobs[0].source == "fake"
    assert jobs[1].source == "fake"

def test_ingestion_pipeline_deduplicates_jobs(db_session: Session):
    source = FakeJobSource()

    first_result = ingest_jobs(
        source=source,
        session=db_session,
        query="machine learning",
        location="Chicago",
    )

    second_result = ingest_jobs(
        source=source,
        session=db_session,
        query="machine learning",
        location="Chicago",
    )

    assert first_result.fetched == 2
    assert first_result.inserted == 2
    assert first_result.duplicates == 0
    assert first_result.failed == 0

    assert second_result.fetched == 2
    assert second_result.inserted == 0
    assert second_result.duplicates == 2
    assert second_result.failed == 0

    jobs = db_session.query(Job).all()

    assert len(jobs) == 2

def test_ingestion_pipeline_reports_invalid_jobs(db_session: Session):
    class MixedJobSource(JobSource):
        def fetch_jobs(
            self,
            query: str,
            location: str,
        ) -> list[dict]:
            return [
                {
                    "source": "fake",
                    "source_job_id": "valid-001",
                    "title": "Data Scientist",
                    "company": "Valid Company",
                    "location": "Chicago, IL",
                    "job_url": "https://example.com/job/valid",
                    "collected_at": datetime.utcnow(),
                },
                {
                    "source": "fake",
                    "source_job_id": "invalid-001",
                    "title": "",
                    "company": "Invalid Company",
                    "location": "Chicago, IL",
                    "job_url": "https://example.com/job/invalid",
                    "collected_at": datetime.utcnow(),
                },
            ]

    source = MixedJobSource()

    result = ingest_jobs(
        source=source,
        session=db_session,
        query="data scientist",
        location="Chicago",
    )

    assert result.fetched == 2
    assert result.inserted == 1
    assert result.duplicates == 0
    assert result.failed == 1

    assert len(result.errors) == 1
    assert result.errors[0].source_job_id == "invalid-001"
    assert result.errors[0].error_type == "ValidationError"

    jobs = db_session.query(Job).all()

    assert len(jobs) == 1
    assert jobs[0].source_job_id == "valid-001"