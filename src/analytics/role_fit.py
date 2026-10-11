from dataclasses import dataclass
import re

from src.database.models import Job


@dataclass(frozen=True)
class RoleFit:
    score: float
    label: str
    matched_role: str | None


class RoleFitAnalyzer:
    """Measure how closely a job title matches candidate target roles."""

    def __init__(
        self,
        target_roles: list[str],
    ) -> None:
        self.target_roles = [
            role.strip().lower()
            for role in target_roles
            if role.strip()
        ]

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.lower()

        text = re.sub(
            r"[^a-z0-9+#]+",
            " ",
            text,
        )

        return " ".join(text.split())

    def analyze(self, job: Job) -> RoleFit:
        title = self._normalize(job.title)

        if not title:
            return RoleFit(
                score=0.0,
                label="unknown",
                matched_role=None,
            )

        # Exact target role appears in title.
        for role in self.target_roles:
            normalized_role = self._normalize(role)

            if normalized_role in title:
                return RoleFit(
                    score=100.0,
                    label="target",
                    matched_role=role,
                )

        # Related data/AI roles.
        related_patterns = {
            "data analyst": 70.0,
            "machine learning scientist": 90.0,
            "research scientist": 85.0,
            "ai scientist": 90.0,
            "data science": 85.0,
            "ml engineer": 100.0,
        }

        for role, score in related_patterns.items():
            if role in title:
                return RoleFit(
                    score=score,
                    label="related",
                    matched_role=role,
                )

        return RoleFit(
            score=20.0,
            label="weak",
            matched_role=None,
        )