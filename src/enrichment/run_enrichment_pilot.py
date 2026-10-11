
import argparse
from urllib.parse import urlparse

from src.database.connection import SessionLocal
from src.database.repository import JobRepository
from src.database.enrichment_repository import JobEnrichmentRepository

from src.enrichment.job_description_extractor import JobDescriptionExtractor
from src.enrichment.source_validator import JobSourceValidator
from src.enrichment.structured_extractor import StructuredJobExtractor


# Sources explicitly classified for this pilot.
# Other domains must be reviewed before saving.
THIRD_PARTY_DOMAINS = {
    "builtinchicago.org",
    "www.builtinchicago.org",
}


def classify_source(url: str) -> str | None:
    hostname = (urlparse(url).hostname or "").lower()

    if hostname in THIRD_PARTY_DOMAINS:
        return "third_party"

    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract, validate, and optionally save job enrichment."
    )

    parser.add_argument("--job-id", type=int, required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--location", default="")
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the enrichment record after validation.",
    )

    args = parser.parse_args()

    parsed_url = urlparse(args.url)

    if (
        parsed_url.scheme not in ("http", "https")
        or not parsed_url.netloc
        or not parsed_url.hostname
    ):
        print("\nInvalid URL supplied.")
        print("Use a plain HTTP/HTTPS URL without Markdown formatting.")
        return

    session = SessionLocal()

    try:
        jobs = JobRepository(session).get_all()

        job = next(
            (item for item in jobs if item.id == args.job_id),
            None,
        )

        if job is None:
            print(f"\nJob ID {args.job_id} not found.")
            return

        print("\n=== Enrichment Pilot ===")
        print(f"Database job: [{job.id}] {job.title}")
        print(f"Company: {job.company}")

        # ----------------------------------------
        # STEP 1: EXTRACT JOB POSTING
        # ----------------------------------------

        extracted = JobDescriptionExtractor.extract(args.url)

        if extracted is None:
            print(
                "\nExtraction failed or JobPosting JSON-LD unavailable."
            )
            return

        print(f"\nExtracted title: {extracted.title}")
        print(f"Extracted company: {extracted.company}")
        print(f"Employer identifier: {extracted.identifier}")
        print(
            f"Description length: "
            f"{len(extracted.description or '')}"
        )

        # ----------------------------------------
        # STEP 2: VALIDATE JOB IDENTITY
        # ----------------------------------------

        validation = JobSourceValidator.validate(
            job=job,
            candidate_url=extracted.url,
            candidate_title=extracted.title or "",
            candidate_company=extracted.company or "",
            candidate_location=args.location,
            # Adzuna IDs are not employer requisition IDs.
            candidate_requisition_id=None,
            # This pilot does not independently verify employers.
            trusted_employer_source=False,
        )

        print(f"\nValidation decision: {validation.decision}")
        print(f"Title similarity: {validation.title_similarity}")
        print(f"Company match: {validation.company_match}")
        print(f"Location match: {validation.location_match}")
        print(f"Reasons: {validation.reasons}")

        if validation.decision == "rejected":
            print("\nSource rejected. No enrichment prepared.")
            return

        # ----------------------------------------
        # STEP 3: EXTRACT STRUCTURED INFORMATION
        # ----------------------------------------

        description = extracted.description or ""

        details = StructuredJobExtractor.extract(description)

        print("\n=== Enrichment Preview ===")
        print("Source requires independent identity verification.")

        print("\n--- Technical Skills ---")

        if details.skills:
            for skill in details.skills:
                print(f"  - {skill}")
        else:
            print("  No technical skills detected.")

        print("\n--- Requirements ---")

        if details.requirements:
            for requirement in details.requirements:
                print(f"  - {requirement}")
        else:
            print("  No requirements section detected.")

        print("\n--- Responsibilities ---")

        if details.responsibilities:
            for responsibility in details.responsibilities:
                print(f"  - {responsibility}")
        else:
            print("  No responsibilities section detected.")

        print("\n--- Extraction Summary ---")
        print(f"Description length: {len(description)}")
        print(f"Skills detected: {len(details.skills)}")
        print(
            f"Requirements extracted: "
            f"{len(details.requirements)}"
        )
        print(
            f"Responsibilities extracted: "
            f"{len(details.responsibilities)}"
        )

        # ----------------------------------------
        # STEP 4: PREVIEW OR SAVE
        # ----------------------------------------

        if not args.save:
            print("\nPreview only. Database unchanged.")
            return

        if not description.strip():
            print("\nEmpty description. Nothing saved.")
            return

        # ----------------------------------------
        # STEP 5: CLASSIFY SOURCE
        # ----------------------------------------

        source_type = classify_source(extracted.url)

        if source_type is None:
            print(
                "\nSource type has not been independently classified."
            )
            print(
                "Saving is disabled for this URL."
            )
            return

        print("\n--- Source Classification ---")
        print(f"Source type: {source_type}")
        print(f"Validation status: {validation.decision}")

        # ----------------------------------------
        # STEP 6: SAVE ENRICHMENT
        # ----------------------------------------

        repository = JobEnrichmentRepository(session)

        try:
            record = repository.upsert(
                job_id=job.id,
                source_url=extracted.url,
                source_type=source_type,
                validation_status=validation.decision,
                external_identifier=extracted.identifier,
                title=extracted.title,
                company=extracted.company,
                description=description,
                requirements=list(details.requirements),
                responsibilities=list(details.responsibilities),
                skills=list(details.skills),
                extraction_method=extracted.extraction_method,
            )

            session.commit()

            print("\n=== Enrichment Saved ===")
            print(f"Enrichment ID: {record.id}")
            print(f"Job ID: {record.job_id}")
            print(f"Source type: {record.source_type}")
            print(f"Validation: {record.validation_status}")
            print(f"Source: {record.source_url}")
            print(f"Skills stored: {len(record.skills)}")
            print(
                f"Requirements stored: "
                f"{len(record.requirements)}"
            )
            print(
                f"Responsibilities stored: "
                f"{len(record.responsibilities)}"
            )

        except Exception:
            session.rollback()
            raise

    finally:
        session.close()


if __name__ == "__main__":
    main()
