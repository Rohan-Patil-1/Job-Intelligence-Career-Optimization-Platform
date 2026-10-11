import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from itertools import combinations
from src.analytics.seniority import detect_seniority

from src.database.models import Job


@dataclass(frozen=True)
class DuplicateCandidate:
    job_id_1: int | None
    job_id_2: int | None
    company: str
    title_1: str
    title_2: str
    similarity: float
    reason: str
    confidence: str


class DuplicateDetector:

    TITLE_SIMILARITY_THRESHOLD = 0.85

    @staticmethod
    def normalize(value: str | None) -> str:
        if not value:
            return ""

        value = value.lower().strip()
        value = re.sub(r"[^a-z0-9]+", " ", value)
        return " ".join(value.split())

    @classmethod
    def analyze(
        cls,
        jobs: list[Job],
    ) -> list[DuplicateCandidate]:

        duplicates = []

        for first, second in combinations(jobs, 2):

            first_source = cls.normalize(first.source)
            second_source = cls.normalize(second.source)

            first_source_id = str(
                first.source_job_id or ""
            ).strip()

            second_source_id = str(
                second.source_job_id or ""
            ).strip()

            same_source_identity = (
                bool(first_source)
                and first_source == second_source
                and bool(first_source_id)
                and first_source_id == second_source_id
            )

            company_1 = cls.normalize(first.company)
            company_2 = cls.normalize(second.company)

            same_company = (
                bool(company_1)
                and company_1 == company_2
            )

            title_1 = cls.normalize(first.title)
            title_2 = cls.normalize(second.title)

            similarity = (
                SequenceMatcher(
                    None,
                    title_1,
                    title_2,
                ).ratio()
                if title_1 and title_2
                else 0.0
            )

            seniority_1 = detect_seniority(first.title)
            seniority_2 = detect_seniority(second.title)

            different_seniority = seniority_1 != seniority_2

            # Detect senior-manager distinctions that the general
            # seniority classifier may group under MANAGER.
            senior_manager_pattern = (
                r"\b(?:senior|sr)\.?\s+manager\b"
            )

            first_is_senior_manager = bool(
                re.search(senior_manager_pattern, first.title.lower())
            )

            second_is_senior_manager = bool(
                re.search(senior_manager_pattern, second.title.lower())
            )

            if first_is_senior_manager != second_is_senior_manager:
                different_seniority = True

            if same_source_identity:
                reason = "same_source_job_id"
                confidence = "high"

            elif same_company and title_1 == title_2 and title_1:
                reason = "same_company_exact_title"
                confidence = "medium"

            elif (
                same_company
                and similarity >= cls.TITLE_SIMILARITY_THRESHOLD
                and not different_seniority
            ):
                reason = "same_company_similar_title"
                confidence = "low"

            else:
                continue

            duplicates.append(
                DuplicateCandidate(
                    job_id_1=first.id,
                    job_id_2=second.id,
                    company=first.company or "",
                    title_1=first.title or "",
                    title_2=second.title or "",
                    similarity=round(similarity, 3),
                    reason=reason,
                    confidence=confidence,
                )
            )

        return sorted(
            duplicates,
            key=lambda item: (
                {"high": 3, "medium": 2, "low": 1}[
                    item.confidence
                ],
                item.similarity,
            ),
            reverse=True,
        )