from dataclasses import dataclass

from src.analytics.seniority import (
    SeniorityLevel,
    detect_seniority,
)
from src.database.models import Job


@dataclass(frozen=True)
class SeniorityFit:
    job_level: SeniorityLevel
    job_level_label: str
    fit_score: float
    fit_label: str


class SeniorityFitAnalyzer:
    """Evaluate job seniority against candidate target levels."""

    def __init__(
        self,
        target_levels: set[SeniorityLevel],
    ) -> None:
        self.target_levels = target_levels

    def analyze(self, job: Job) -> SeniorityFit:
        result = detect_seniority(job.title)

        if result.level == SeniorityLevel.UNKNOWN:
            return SeniorityFit(
                job_level=result.level,
                job_level_label=result.label,
                fit_score=0.0,
                fit_label="unknown",
            )

        if result.level in self.target_levels:
            return SeniorityFit(
                job_level=result.level,
                job_level_label=result.label,
                fit_score=100.0,
                fit_label="target",
            )

        if not self.target_levels:
            return SeniorityFit(
                job_level=result.level,
                job_level_label=result.label,
                fit_score=0.0,
                fit_label="unknown",
            )

        distance = min(
            abs(
                int(result.level)
                - int(target_level)
            )
            for target_level in self.target_levels
        )

        scores = {
            1: (70.0, "stretch"),
            2: (40.0, "high_stretch"),
            3: (15.0, "unlikely"),
        }

        score, label = scores.get(
            distance,
            (0.0, "poor_fit"),
        )

        return SeniorityFit(
            job_level=result.level,
            job_level_label=result.label,
            fit_score=score,
            fit_label=label,
        )