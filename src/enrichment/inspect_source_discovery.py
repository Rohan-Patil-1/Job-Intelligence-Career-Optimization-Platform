from src.database.connection import SessionLocal
from src.database.repository import JobRepository
from src.enrichment.source_discovery import SourceDiscovery


PILOT_JOB_IDS = {43, 6, 18, 5, 7}


def main() -> None:
    session = SessionLocal()

    try:
        jobs = JobRepository(session).get_all()

        selected = [
            job for job in jobs
            if job.id in PILOT_JOB_IDS
        ]

        print("\n=== Verified Source Discovery Pilot ===")
        print(f"Selected jobs: {len(selected)}")

        for job in selected:
            result = SourceDiscovery.create_search(job)

            print("\n" + "=" * 70)
            print(f"Job ID: {result.job_id}")
            print(f"Company: {result.company}")
            print(f"Title: {result.title}")
            print(f"Query: {result.query}")
            print(f"Search URL: {result.search_url}")

    finally:
        session.close()


if __name__ == "__main__":
    main()