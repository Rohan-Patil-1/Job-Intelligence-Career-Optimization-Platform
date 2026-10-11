from dataclasses import dataclass
import math

from src.analytics.skills import SkillAnalyzer
from src.database.models import Job


@dataclass(frozen=True)
class JobMatch:
    job_id: int | None
    title: str
    company: str

    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]
    detected_skills: tuple[str, ...]

    match_percentage: float
    evidence_score: float
    ranking_score: float

    evidence_level: str


class JobMatcher:
    """
    Compare candidate skills against individual jobs.

    Match percentage:
        Percentage of detected job skills matched by the candidate.

    Evidence score:
        Confidence based on how many skills were actually detected.

    Ranking score:
        Match percentage discounted when evidence is sparse.
    """

    def __init__(
        self,
        candidate_skills: set[str],
    ) -> None:
        self.candidate_skills = {
            skill.strip().lower()
            for skill in candidate_skills
            if skill.strip()
        }

    @staticmethod
    def _evidence_score(
        detected_skill_count: int,
    ) -> float:
        """
        Convert detected skill count into a confidence score.

        Uses a saturating curve so additional evidence helps,
        but with diminishing returns.
        """
        if detected_skill_count <= 0:
            return 0.0

        score = (
            1 - math.exp(-detected_skill_count / 3)
        ) * 100

        return round(score, 2)

    @staticmethod
    def _evidence_level(
        detected_skill_count: int,
    ) -> str:
        if detected_skill_count == 0:
            return "insufficient"

        if detected_skill_count <= 2:
            return "low"

        if detected_skill_count <= 4:
            return "medium"

        return "high"

    def match_job(
        self,
        job: Job,
    ) -> JobMatch:
        analyzer = SkillAnalyzer([job])

        detected = set(
            analyzer.skills_for_job(job)
        )

        matched = (
            detected
            & self.candidate_skills
        )

        missing = (
            detected
            - self.candidate_skills
        )

        match_percentage = (
            (len(matched) / len(detected)) * 100
            if detected
            else 0.0
        )

        evidence_score = self._evidence_score(
            len(detected)
        )

        ranking_score = (
            match_percentage
            * (evidence_score / 100)
        )

        return JobMatch(
            job_id=job.id,
            title=job.title,
            company=job.company,

            matched_skills=tuple(
                sorted(matched)
            ),

            missing_skills=tuple(
                sorted(missing)
            ),

            detected_skills=tuple(
                sorted(detected)
            ),

            match_percentage=round(
                match_percentage,
                2,
            ),

            evidence_score=evidence_score,

            ranking_score=round(
                ranking_score,
                2,
            ),

            evidence_level=self._evidence_level(
                len(detected)
            ),
        )

    def rank_jobs(
        self,
        jobs: list[Job],
    ) -> list[JobMatch]:
        matches = [
            self.match_job(job)
            for job in jobs
        ]

        return sorted(
            matches,
            key=lambda item: (
                item.ranking_score,
                item.match_percentage,
                len(item.detected_skills),
            ),
            reverse=True,
        )