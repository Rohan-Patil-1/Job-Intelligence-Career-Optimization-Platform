
from dataclasses import dataclass

from src.enrichment.structured_extractor import StructuredJobExtractor


@dataclass(frozen=True)
class EvidenceComparison:
    job_id: int
    validation_status: str
    source_type: str
    baseline_description_length: int
    enriched_description_length: int
    baseline_skills: tuple[str, ...]
    enriched_skills: tuple[str, ...]
    additional_skills: tuple[str, ...]
    baseline_requirements_count: int
    enriched_requirements_count: int
    baseline_responsibilities_count: int
    enriched_responsibilities_count: int
    eligible_for_production_scoring: bool


class EvidenceComparator:

    @staticmethod
    def compare(
        *,
        job_id: int,
        baseline_description: str,
        enriched_description: str,
        validation_status: str,
        source_type: str,
    ) -> EvidenceComparison:

        baseline = StructuredJobExtractor.extract(
            baseline_description or ""
        )

        enriched = StructuredJobExtractor.extract(
            enriched_description or ""
        )

        baseline_skill_set = set(baseline.skills)

        additional_skills = tuple(
            skill
            for skill in enriched.skills
            if skill not in baseline_skill_set
        )

        eligible = (
            validation_status == "verified"
            and source_type == "employer"
        )

        return EvidenceComparison(
            job_id=job_id,
            validation_status=validation_status,
            source_type=source_type,
            baseline_description_length=len(
                baseline_description or ""
            ),
            enriched_description_length=len(
                enriched_description or ""
            ),
            baseline_skills=baseline.skills,
            enriched_skills=enriched.skills,
            additional_skills=additional_skills,
            baseline_requirements_count=len(
                baseline.requirements
            ),
            enriched_requirements_count=len(
                enriched.requirements
            ),
            baseline_responsibilities_count=len(
                baseline.responsibilities
            ),
            enriched_responsibilities_count=len(
                enriched.responsibilities
            ),
            eligible_for_production_scoring=eligible,
        )
