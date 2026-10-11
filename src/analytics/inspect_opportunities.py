from src.analytics.opportunity import OpportunityScorer
from src.database.connection import SessionLocal
from src.database.repository import JobRepository
from src.profile.default_profile import DEFAULT_PROFILE
from src.analytics.opportunity_diagnostics import OpportunityDiagnostics


def main() -> None:
    session = SessionLocal()

    try:
        jobs = JobRepository(session).get_all()

        scorer = OpportunityScorer(
            DEFAULT_PROFILE
        )

        results = scorer.rank_jobs(jobs)

        print("\n=== Opportunity Ranking ===")
        print(f"Candidate: {DEFAULT_PROFILE.name}")
        print(f"Jobs analyzed: {len(jobs)}")

        for rank, result in enumerate(
            results,
            start=1,
        ):
            print("\n" + "=" * 70)

            print(
                f"#{rank} | "
                f"{result.title} | "
                f"{result.company}"
            )

            print(
                f"Opportunity score: "
                f"{result.opportunity_score:.2f}"
            )

            print(
                f"Skill match: "
                f"{result.skill_match:.2f}%"
            )

            print(
                f"Role fit: "
                f"{result.role_fit:.2f}% "
                f"({result.role_label})"
            )

            print(
                f"Evidence: "
                f"{result.evidence_score:.2f}%"
            )

            print(
                f"Seniority: "
                f"{result.seniority_level} | "
                f"{result.seniority_fit:.2f}% "
                f"({result.seniority_label})"
            )

            print(
                f"Seniority adjustment: "
                f"{result.seniority_multiplier:.2f}x"
            )

            print(
                f"Domain fit: "
                f"{result.domain_fit:.2f}% "
                f"({result.domain_label})"
            )

            print(
                "Matched domains: "
                + (
                    ", ".join(result.matched_domains)
                    if result.matched_domains
                    else "None detected"
                )
            )

            print(
                f"Domain evidence: "
                f"{result.domain_evidence_level}"
            )

            print(
                "Matched: "
                + (
                    ", ".join(result.matched_skills)
                    if result.matched_skills
                    else "None"
                )
            )

            print(
                "Missing: "
                + (
                    ", ".join(result.missing_skills)
                    if result.missing_skills
                    else "None"
                )
            )

            diagnostic = OpportunityDiagnostics.analyze(result)

            print("\nDiagnostic Assessment")

            print(
                f"Recommendation: "
                f"{diagnostic.recommendation}"
            )

            print(
                f"Technical evidence confidence: "
                f"{diagnostic.confidence}"
            )

            print("Strengths:")
            if diagnostic.strengths:
                for strength in diagnostic.strengths:
                    print(f"  + {strength}")
            else:
                print("  None identified")

            print("Concerns:")
            if diagnostic.concerns:
                for concern in diagnostic.concerns:
                    print(f"  - {concern}")
            else:
                print("  None identified")

            print("Evidence gaps:")
            if diagnostic.evidence_gaps:
                for gap in diagnostic.evidence_gaps:
                    print(f"  ? {gap}")
            else:
                print("  None identified")

    finally:
        session.close()


if __name__ == "__main__":
    main()