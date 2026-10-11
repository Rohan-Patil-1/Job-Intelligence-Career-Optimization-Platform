from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.analytics.base import AnalyticsModule
from src.database.models import Job


class MarketAnalyzer(AnalyticsModule):
    """Core market-level analytics over stored job postings."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def analyze(self) -> dict[str, int]:
        """Return high-level statistics for the stored job market."""

        total_jobs = self.session.scalar(
            select(func.count()).select_from(Job)
        )

        unique_companies = self.session.scalar(
            select(func.count(func.distinct(Job.company)))
        )

        unique_sources = self.session.scalar(
            select(func.count(func.distinct(Job.source)))
        )

        return {
            "total_jobs": total_jobs or 0,
            "unique_companies": unique_companies or 0,
            "unique_sources": unique_sources or 0,
        }