from dataclasses import dataclass
from collections import Counter

from src.database.models import Job


AUDIT_FIELDS = (
    "title",
    "company",
    "location",
    "description",
    "requirements",
    "responsibilities",
    "skills",
    "job_url",
)

OPTIONAL_SALARY_FIELDS = (
    "salary_min",
    "salary_max",
)


@dataclass(frozen=True)
class JobCompleteness:
    job_id: int | None
    title: str
    company: str
    completeness_score: float
    missing_fields: tuple[str, ...]
    description_length: int
    quality_label: str


@dataclass(frozen=True)
class CompletenessSummary:
    total_jobs: int
    average_completeness: float
    missing_field_counts: dict[str, int]
    quality_distribution: dict[str, int]
    jobs: tuple[JobCompleteness, ...]


class DataCompletenessAnalyzer:

    @staticmethod
    def _has_value(value) -> bool:
        if value is None:
            return False

        if isinstance(value, str):
            return bool(value.strip())

        if isinstance(value, (list, tuple, set, dict)):
            return bool(value)

        return True

    @classmethod
    def analyze_job(cls, job: Job) -> JobCompleteness:
        missing = []

        for field in AUDIT_FIELDS:
            value = getattr(job, field, None)

            if not cls._has_value(value):
                missing.append(field)

        salary_available = any(
            cls._has_value(getattr(job, field, None))
            for field in OPTIONAL_SALARY_FIELDS
        )

        if not salary_available:
            missing.append("salary")

        total_fields = len(AUDIT_FIELDS) + 1
        available_fields = total_fields - len(missing)

        score = round(
            available_fields / total_fields * 100,
            2,
        )

        if score >= 80:
            quality_label = "high"
        elif score >= 50:
            quality_label = "medium"
        else:
            quality_label = "low"

        description = getattr(job, "description", None) or ""

        return JobCompleteness(
            job_id=job.id,
            title=job.title or "",
            company=job.company or "",
            completeness_score=score,
            missing_fields=tuple(missing),
            description_length=len(description.strip()),
            quality_label=quality_label,
        )

    @classmethod
    def analyze_jobs(
        cls,
        jobs: list[Job],
    ) -> CompletenessSummary:

        results = tuple(
            cls.analyze_job(job)
            for job in jobs
        )

        missing_counts = Counter()
        quality_counts = Counter()

        for result in results:
            missing_counts.update(result.missing_fields)
            quality_counts[result.quality_label] += 1

        average = (
            round(
                sum(
                    result.completeness_score
                    for result in results
                ) / len(results),
                2,
            )
            if results
            else 0.0
        )

        return CompletenessSummary(
            total_jobs=len(results),
            average_completeness=average,
            missing_field_counts=dict(missing_counts),
            quality_distribution=dict(quality_counts),
            jobs=results,
        )