
import argparse

from src.analytics.opportunity_diagnostics import (
    OpportunityDiagnostics,
)
from src.database.connection import SessionLocal
from src.database.enrichment_repository import (
    JobEnrichmentRepository,
)
from src.database.repository import JobRepository
from src.enrichment.score_comparison import (
    OpportunityScoreComparator,
)
from src.profile.default_profile import DEFAULT_PROFILE


def print_dimension(name, baseline, provisional):
    print(
        f"{name:<24}"
        f"{baseline:>10.2f}"
        f"{provisional:>14.2f}"
        f"{provisional - baseline:>12.2f}"
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Compare baseline and enriched opportunity scores "
            "without changing production data."
        )
    )

    parser.add_argument(
        "--job-id",
        type=int,
        required=True,
    )

    args = parser.parse_args()

    with SessionLocal() as session:
        job = next(
            (
                item
                for item in JobRepository(session).get_all()
                if item.id == args.job_id
            ),
            None,
        )

        if job is None:
            print(f"Job {args.job_id} not found.")
            return

        enrichments = JobEnrichmentRepository(
            session
        ).get_for_job(job.id)

        if not enrichments:
            print("No saved enrichment found.")
            return

        comparator = OpportunityScoreComparator(
            DEFAULT_PROFILE
        )

        for enrichment in enrichments:
            result = comparator.compare(
                job=job,
                enriched_description=(
                    enrichment.description or ""
                ),
                validation_status=(
                    enrichment.validation_status
                ),
                source_type=enrichment.source_type,
            )

            baseline = result.baseline
            provisional = result.provisional

            print("\n=== Opportunity Score Comparison ===")
            print(f"Job: [{job.id}] {job.title}")
            print(f"Company: {job.company}")
            print(f"Enrichment ID: {enrichment.id}")
            print(f"Source: {enrichment.source_url}")

            print("\n--- Evidence Trust ---")
            print("Source type:", result.source_type)
            print("Validation:", result.validation_status)
            print(
                "Production eligible:",
                result.production_eligible,
            )

            print("\n--- Score Comparison ---")
            print(
                f"{'Dimension':<24}"
                f"{'Baseline':>10}"
                f"{'Provisional':>14}"
                f"{'Delta':>12}"
            )

            print("-" * 60)

            for name, before, after in [
                (
                    "Opportunity score",
                    baseline.opportunity_score,
                    provisional.opportunity_score,
                ),
                (
                    "Skill match",
                    baseline.skill_match,
                    provisional.skill_match,
                ),
                (
                    "Evidence score",
                    baseline.evidence_score,
                    provisional.evidence_score,
                ),
                (
                    "Role fit",
                    baseline.role_fit,
                    provisional.role_fit,
                ),
                (
                    "Seniority fit",
                    baseline.seniority_fit,
                    provisional.seniority_fit,
                ),
                (
                    "Domain fit",
                    baseline.domain_fit,
                    provisional.domain_fit,
                ),
            ]:
                print_dimension(name, before, after)

            print("\n--- Additional Matched Skills ---")
            if result.newly_matched_skills:
                for skill in result.newly_matched_skills:
                    print(f"  + {skill}")
            else:
                print("None")

            print("\n--- Additional Missing Skills ---")
            if result.newly_missing_skills:
                for skill in result.newly_missing_skills:
                    print(f"  + {skill}")
            else:
                print("None")

            print("\n--- Recommendation Comparison ---")
            print(
                "Baseline:",
                result.baseline_diagnostic.recommendation,
            )
            print(
                "Provisional:",
                result.provisional_diagnostic.recommendation,
            )

            print("\n--- Confidence Comparison ---")
            print(
                "Baseline:",
                result.baseline_diagnostic.confidence,
            )
            print(
                "Provisional:",
                result.provisional_diagnostic.confidence,
            )

            if not result.production_eligible:
                print(
                    "\nWARNING: Third-party or unverified "
                    "enrichment. This result is provisional."
                )

            print(
                "\nRead-only comparison complete. "
                "Production data unchanged."
            )


if __name__ == "__main__":
    main()
