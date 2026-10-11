from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import JobEnrichment


class JobEnrichmentRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_by_job_and_url(
        self,
        job_id: int,
        source_url: str,
    ) -> JobEnrichment | None:

        statement = select(JobEnrichment).where(
            JobEnrichment.job_id == job_id,
            JobEnrichment.source_url == source_url,
        )

        return self.session.scalar(statement)

    def get_for_job(
        self,
        job_id: int,
    ) -> list[JobEnrichment]:

        statement = (
            select(JobEnrichment)
            .where(JobEnrichment.job_id == job_id)
            .order_by(JobEnrichment.extracted_at.desc())
        )

        return list(self.session.scalars(statement).all())

    def upsert(
        self,
        *,
        job_id: int,
        source_url: str,
        source_type: str,
        validation_status: str,
        external_identifier: str | None,
        title: str | None,
        company: str | None,
        description: str | None,
        requirements: list[str],
        responsibilities: list[str],
        skills: list[str],
        extraction_method: str = "json_ld",
    ) -> JobEnrichment:

        if validation_status not in (
            "verified",
            "review_required",
        ):
            raise ValueError(
                "Only verified or review_required "
                "enrichments may be saved."
            )

        if source_type not in ("employer", "third_party"):
            raise ValueError("Invalid source type.")

        record = self.get_by_job_and_url(
            job_id,
            source_url,
        )

        if record is None:
            record = JobEnrichment(
                job_id=job_id,
                source_url=source_url,
            )

            self.session.add(record)

        record.source_type = source_type
        record.validation_status = validation_status
        record.external_identifier = external_identifier
        record.title = title
        record.company = company
        record.description = description
        record.requirements = requirements
        record.responsibilities = responsibilities
        record.skills = skills
        record.extraction_method = extraction_method

        self.session.flush()

        return record