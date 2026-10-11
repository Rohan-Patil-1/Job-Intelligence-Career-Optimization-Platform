from abc import ABC, abstractmethod
from typing import Any


class AnalyticsModule(ABC):
    """Base interface for analytics modules."""

    @abstractmethod
    def analyze(self, *args: Any, **kwargs: Any) -> Any:
        """Run an analytics operation."""
        raise NotImplementedError