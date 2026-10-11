import pytest

from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from src.database.models import Base, Job, JobEnrichment
from src.database.enrichment_repository import JobEnrichmentRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)

    with Session(engine) as db:
        # The repository tests require an existing parent job.
        # We create it without depending on production data.
        job = Job(
            source="test",
            source_job_id="test-18",
            title="Data Scientist II",
            company="Tempus AI",
            location="Chicago",
            job_url="https://example.com/jobs/test-18",
        )
        db.add(job)
        db.flush()

        # Use the actual ID assigned by SQLite.
        db.info["test_job_id"] = job.id

        yield db

    engine.dispose()


def enrichment_payload(job_id):
    return {
        "job_id": job_id,
        "source_url": "https://example.com/jobs/tempus-18",
        "source_type": "third_party",
        "validation_status": "review_required",
        "external_identifier": "11443687",
        "title": "Data Scientist II",
        "company": "Tempus AI",
        "description": "Experience with R, SQL and RWE.",
        "requirements": ["Experience with SQL."],
        "responsibilities": ["Analyze healthcare data."],
        "skills": ["SQL", "R", "Real-World Evidence"],
    }


def test_create_enrichment(session):
    repository = JobEnrichmentRepository(session)
    job_id = session.info["test_job_id"]

    record = repository.upsert(**enrichment_payload(job_id))
    session.commit()

    saved = session.scalar(select(JobEnrichment))

    assert saved is not None
    assert saved.id == record.id
    assert saved.validation_status == "review_required"
    assert "SQL" in saved.skills


def test_upsert_does_not_duplicate(session):
    repository = JobEnrichmentRepository(session)
    job_id = session.info["test_job_id"]

    first = repository.upsert(**enrichment_payload(job_id))

    updated_payload = enrichment_payload(job_id)
    updated_payload["skills"] = ["SQL", "R", "AWS"]

    second = repository.upsert(**updated_payload)
    session.commit()

    records = session.scalars(select(JobEnrichment)).all()

    assert len(records) == 1
    assert first.id == second.id
    assert "AWS" in records[0].skills


def test_rejected_enrichment_not_saved(session):
    repository = JobEnrichmentRepository(session)
    job_id = session.info["test_job_id"]

    payload = enrichment_payload(job_id)
    payload["validation_status"] = "rejected"

    with pytest.raises(ValueError):
        repository.upsert(**payload)

    assert session.scalar(select(JobEnrichment)) is None


def test_get_for_job(session):
    repository = JobEnrichmentRepository(session)
    job_id = session.info["test_job_id"]

    repository.upsert(**enrichment_payload(job_id))
    session.commit()

    records = repository.get_for_job(job_id)

    assert len(records) == 1
    assert records[0].job_id == job_id