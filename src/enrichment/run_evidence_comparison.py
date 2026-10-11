
import argparse

from src.database.connection import SessionLocal
from src.database.repository import JobRepository
from src.database.enrichment_repository import JobEnrichmentRepository
from src.enrichment.evidence_comparison import EvidenceComparator


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-id", type=int, required=True)
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
            print(f"Job ID {args.job_id} not found.")
            return

        enrichments = JobEnrichmentRepository(
            session
        ).get_for_job(job.id)

        if not enrichments:
            print("No enrichment available for this job.")
            return

        # Compare one enrichment at a time.
        # Never silently combine different sources.
        for enrichment in enrichments:
            result = EvidenceComparator.compare(
                job_id=job.id,
                baseline_description=job.description or "",
                enriched_description=enrichment.description or "",
                validation_status=enrichment.validation_status,
                source_type=enrichment.source_type,
            )

            print("\n=== Evidence Comparison ===")
            print(f"Job: [{job.id}] {job.title}")
            print(f"Company: {job.company}")
            print(f"Enrichment ID: {enrichment.id}")
            print(f"Source: {enrichment.source_url}")

            print("\n--- Source Trust ---")
            print("Source type:", result.source_type)
            print("Validation:", result.validation_status)
            print(
                "Eligible for production scoring:",
                result.eligible_for_production_scoring,
            )

            print("\n--- Description Coverage ---")
            print(
                "Baseline characters:",
                result.baseline_description_length,
            )
            print(
                "Enriched characters:",
                result.enriched_description_length,
            )

            print("\n--- Skill Evidence ---")
            print("Baseline skills:", len(result.baseline_skills))
            print("Enriched skills:", len(result.enriched_skills))
            print("Additional skills:", len(result.additional_skills))

            for skill in result.additional_skills:
                print(f"  + {skill}")

            print("\n--- Structured Evidence ---")
            print(
                "Baseline requirements:",
                result.baseline_requirements_count,
            )
            print(
                "Enriched requirements:",
                result.enriched_requirements_count,
            )
            print(
                "Baseline responsibilities:",
                result.baseline_responsibilities_count,
            )
            print(
                "Enriched responsibilities:",
                result.enriched_responsibilities_count,
            )

            if not result.eligible_for_production_scoring:
                print(
                    "\nSupplemental evidence only. "
                    "Production scoring remains unchanged."
                )


if __name__ == "__main__":
    main()
