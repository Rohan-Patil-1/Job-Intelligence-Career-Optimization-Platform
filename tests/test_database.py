from datetime import datetime

from sqlalchemy.orm import Session

from src.database.models import Job
from src.database.repository import JobRepository


def test_job_repository_add_and_retrieve(db_session: Session):
    repository = JobRepository(db_session)

    job = Job(
        source="test",
        source_job_id="test-001",
        title="Machine Learning Engineer",
        company="Test Company",
        location="Chicago, IL",
        job_url="https://example.com/job/1",
        collected_at=datetime.utcnow(),
    )

    repository.add(job)
    db_session.commit()

    retrieved = repository.get_by_source_job_id(
        source="test",
        source_job_id="test-001",
    )

    assert retrieved is not None
    assert retrieved.title == "Machine Learning Engineer"
    assert retrieved.company == "Test Company"
    assert retrieved.source == "test"
    assert retrieved.source_job_id == "test-001"


def test_job_repository_prevents_duplicate(db_session: Session):
    repository = JobRepository(db_session)

    job_1 = Job(
        source="test",
        source_job_id="duplicate-001",
        title="Data Scientist",
        company="Test Company",
        location="Chicago, IL",
        job_url="https://example.com/job/2",
        collected_at=datetime.utcnow(),
    )

    stored_job, inserted = repository.add_if_new(job_1)
    db_session.commit()

    assert inserted is True
    assert stored_job.source_job_id == "duplicate-001"

    job_2 = Job(
        source="test",
        source_job_id="duplicate-001",
        title="Data Scientist Updated",
        company="Test Company",
        location="Chicago, IL",
        job_url="https://example.com/job/2",
        collected_at=datetime.utcnow(),
    )

    existing_job, inserted = repository.add_if_new(job_2)
    db_session.commit()

    assert inserted is False
    assert existing_job.id == stored_job.id
    assert existing_job.title == "Data Scientist"