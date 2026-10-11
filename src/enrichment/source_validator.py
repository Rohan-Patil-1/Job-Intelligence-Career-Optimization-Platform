import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from urllib.parse import urlparse


@dataclass(frozen=True)
class SourceValidation:
    job_id: int | None
    candidate_url: str
    title_similarity: float
    company_match: bool
    location_match: bool
    requisition_match: bool
    decision: str
    reasons: tuple[str, ...]


class JobSourceValidator:

    @staticmethod
    def normalize(value: str | None) -> str:
        if not value:
            return ""

        value = value.casefold()
        value = re.sub(r"[^a-z0-9]+", " ", value)

        return " ".join(value.split())

    @classmethod
    def validate(
        cls,
        job,
        candidate_url: str,
        candidate_title: str,
        candidate_company: str,
        candidate_location: str,
        candidate_requisition_id: str | None = None,
        trusted_employer_source: bool = False,
    ) -> SourceValidation:

        original_title = cls.normalize(job.title)
        external_title = cls.normalize(candidate_title)

        title_similarity = (
            SequenceMatcher(
                None,
                original_title,
                external_title,
            ).ratio()
            if original_title and external_title
            else 0.0
        )

        company_match = (
            bool(cls.normalize(job.company))
            and cls.normalize(job.company)
            == cls.normalize(candidate_company)
        )

        original_location = cls.normalize(job.location)
        external_location = cls.normalize(candidate_location)

        location_match = (
            bool(original_location)
            and bool(external_location)
            and (
                original_location in external_location
                or external_location in original_location
            )
        )

        requisition_match = (
            bool(candidate_requisition_id)
            and bool(job.source_job_id)
            and str(candidate_requisition_id).strip()
            == str(job.source_job_id).strip()
        )

        reasons = []

        parsed_url = urlparse(candidate_url)

        valid_url = (
            parsed_url.scheme in ("http", "https")
            and bool(parsed_url.netloc)
        )

        if not valid_url:
            reasons.append("invalid_candidate_url")

        if not company_match:
            reasons.append("company_mismatch")

        if title_similarity < 0.85:
            reasons.append("title_mismatch")

        if not location_match:
            reasons.append("location_not_confirmed")

        if requisition_match:
            reasons.append("requisition_id_match")

        if not trusted_employer_source:
            reasons.append("employer_source_not_verified")

        if (
            valid_url
            and company_match
            and title_similarity >= 0.90
            and location_match
            and requisition_match
            and trusted_employer_source
        ):
            decision = "verified"

        elif (
            valid_url
            and company_match
            and title_similarity >= 0.85
        ):
            decision = "review_required"

        else:
            decision = "rejected"

        return SourceValidation(
            job_id=job.id,
            candidate_url=candidate_url,
            title_similarity=round(title_similarity, 3),
            company_match=company_match,
            location_match=location_match,
            requisition_match=requisition_match,
            decision=decision,
            reasons=tuple(reasons),
        )