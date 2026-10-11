from dataclasses import dataclass

from src.analytics.opportunity import OpportunityScore
from src.analytics.title_diagnostics import TitleDiagnostics


@dataclass(frozen=True)
class OpportunityDiagnostic:
    recommendation: str
    confidence: str
    strengths: tuple[str, ...]
    concerns: tuple[str, ...]
    evidence_gaps: tuple[str, ...]


class OpportunityDiagnostics:

    @staticmethod
    def analyze(
        result: OpportunityScore,
    ) -> OpportunityDiagnostic:

        strengths = []
        concerns = []
        evidence_gaps = []

        title_diagnostic = TitleDiagnostics.analyze(result.title)

        if title_diagnostic.is_mixed_role:
            concerns.append(
                "Job title combines multiple professional roles."
            )

        # Role relevance
        if result.role_fit >= 85:
            strengths.append(
                "Strong alignment with target job roles."
            )
        elif result.role_fit < 50:
            concerns.append(
                "Job title has limited alignment with target roles."
            )

        # Seniority
        if result.seniority_label == "target":
            strengths.append(
                "Seniority matches the candidate's target level."
            )
        elif result.seniority_label == "stretch":
            concerns.append(
                "Position is a seniority stretch."
            )
        elif result.seniority_label in {
            "high_stretch",
            "unlikely",
            "poor_fit",
        }:
            concerns.append(
                "Seniority is substantially above the target level."
            )

        # Technical evidence
        if result.evidence_score == 0:
            evidence_gaps.append(
                "No technical skill evidence was detected."
            )
        elif result.evidence_score < 50:
            evidence_gaps.append(
                "Limited technical skill evidence is available."
            )

        if result.evidence_score > 0:
            if result.skill_match >= 80:
                strengths.append(
                    "Strong match among detected technical skills."
                )
            elif result.skill_match < 50:
                concerns.append(
                    "Low match among detected technical skills."
                )

        # Domain preference
        if result.domain_label == "preferred":
            strengths.append(
                "Job aligns with preferred industry or research domains."
            )
        elif result.domain_label == "unknown":
            evidence_gaps.append(
                "Insufficient information to determine job domain."
            )

        # Confidence based on available technical evidence
        if result.evidence_score >= 70:
            confidence = "high"
        elif result.evidence_score >= 40:
            confidence = "medium"
        else:
            confidence = "low"

        # Recommendation category
        if result.seniority_label in {
            "unlikely",
            "poor_fit",
        }:
            recommendation = "low_priority"

        elif (
            result.opportunity_score >= 70
            and confidence != "low"
            and not title_diagnostic.is_mixed_role
        ):
            recommendation = "strong_review"

        elif (
            result.role_fit >= 85
            and result.seniority_label in {
                "target",
                "stretch",
            }
            and confidence == "low"
        ):
            recommendation = "needs_more_evidence"

        elif title_diagnostic.is_mixed_role:
            recommendation = "needs_more_evidence"

        elif result.opportunity_score >= 50:
            recommendation = "consider"

        else:
            recommendation = "low_priority"

        return OpportunityDiagnostic(
            recommendation=recommendation,
            confidence=confidence,
            strengths=tuple(strengths),
            concerns=tuple(concerns),
            evidence_gaps=tuple(evidence_gaps),
        )