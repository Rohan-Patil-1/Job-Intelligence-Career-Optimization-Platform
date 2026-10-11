from collections import defaultdict

from src.analytics.opportunity import OpportunityScorer
from src.analytics.opportunity_diagnostics import OpportunityDiagnostics
from src.database.connection import SessionLocal
from src.database.repository import JobRepository
from src.profile.default_profile import DEFAULT_PROFILE


RECOMMENDATION_ORDER = (
    "strong_review",
    "needs_more_evidence",
    "consider",
    "low_priority",
)


def main() -> None:
    session = SessionLocal()

    try:
        jobs = JobRepository(session).get_all()

        scorer = OpportunityScorer(DEFAULT_PROFILE)
        results = scorer.rank_jobs(jobs)

        groups = defaultdict(list)

        for result in results:
            diagnostic = OpportunityDiagnostics.analyze(result)
            groups[diagnostic.recommendation].append(
                (result, diagnostic)
            )

        print("\n=== Opportunity Review Priorities ===")
        print(f"Candidate: {DEFAULT_PROFILE.name}")
        print(f"Jobs analyzed: {len(results)}")

        print("\nRecommendation Distribution")

        for recommendation in RECOMMENDATION_ORDER:
            print(
                f"{recommendation}: "
                f"{len(groups[recommendation])}"
            )

        for recommendation in RECOMMENDATION_ORDER:
            items = groups[recommendation]

            if not items:
                continue

            print("\n" + "=" * 70)
            print(
                f"{recommendation.upper()} "
                f"({len(items)} jobs)"
            )

            for rank, (result, diagnostic) in enumerate(
                items,
                start=1,
            ):
                print(
                    f"\n{rank}. {result.title} | "
                    f"{result.company}"
                )

                print(
                    f"   Opportunity score: "
                    f"{result.opportunity_score:.2f}"
                )

                print(
                    f"   Technical evidence confidence: "
                    f"{diagnostic.confidence}"
                )

                print(
                    f"   Domain: {result.domain_label}"
                )

                if diagnostic.concerns:
                    print(
                        "   Concerns: "
                        + "; ".join(diagnostic.concerns)
                    )

                if diagnostic.evidence_gaps:
                    print(
                        "   Evidence gaps: "
                        + "; ".join(diagnostic.evidence_gaps)
                    )

    finally:
        session.close()


if __name__ == "__main__":
    main()