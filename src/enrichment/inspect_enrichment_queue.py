from src.database.connection import SessionLocal
from src.database.repository import JobRepository
from src.enrichment.enrichment_queue import EnrichmentQueue
from src.profile.default_profile import DEFAULT_PROFILE


def main() -> None:
    session = SessionLocal()

    try:
        jobs = JobRepository(session).get_all()
        queue = EnrichmentQueue(DEFAULT_PROFILE).build(jobs)

        print("\n=== Job Enrichment Queue ===")
        print(f"Total jobs: {len(jobs)}")
        print(f"Jobs needing enrichment: {len(queue)}")

        for index, item in enumerate(queue[:15], start=1):
            print("\n" + "=" * 65)
            print(f"{index}. [{item.job_id}] {item.title}")
            print(f"   Company: {item.company}")
            print(f"   Location: {item.location}")
            print(f"   Priority: {item.priority}")
            print(f"   Recommendation: {item.recommendation}")
            print(f"   Opportunity score: {item.opportunity_score:.2f}")
            print(f"   Evidence score: {item.evidence_score:.2f}")

    finally:
        session.close()


if __name__ == "__main__":
    main()