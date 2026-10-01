from abc import ABC, abstractmethod
from typing import Any


class JobSource(ABC):
    """Base interface for external job data sources."""

    @abstractmethod
    def fetch_jobs(self, query: str, location: str) -> list[dict[str, Any]]:
        """Fetch raw job postings from the source."""
        raise NotImplementedError