from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import Job


class JobRepository:
    """Database operations for job records."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_source_job_id(
        self,
        source: str,
        source_job_id: str,
    ) -> Job | None:
        statement = select(Job).where(
            Job.source == source,
            Job.source_job_id == source_job_id,
        )

        return self.session.scalar(statement)

    def add(self, job: Job) -> Job:
        self.session.add(job)
        self.session.flush()

        return job

    def get_all(self) -> list[Job]:
        statement = select(Job).order_by(Job.id)

        return list(self.session.scalars(statement).all())

    def add_if_new(self, job: Job) -> tuple[Job, bool]:
        """Add a job only if it does not already exist.

        Returns:
            tuple[Job, bool]:
                The stored/existing job and whether it was newly inserted.
        """

        if job.source_job_id:
            existing = self.get_by_source_job_id(
                source=job.source,
                source_job_id=job.source_job_id,
            )

            if existing is not None:
                return existing, False

        self.session.add(job)
        self.session.flush()

        return job, True