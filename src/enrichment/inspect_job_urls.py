from urllib.parse import urlparse

from src.database.connection import SessionLocal
from src.database.repository import JobRepository
from src.enrichment.url_resolver import JobURLResolver


def main() -> None:
    session = SessionLocal()

    try:
        jobs = JobRepository(session).get_all()

        print("\n=== Job URL Resolution Audit ===")
        print(f"Total jobs: {len(jobs)}")

        for job in jobs[:5]:
            print("\n" + "=" * 70)
            print(f"Job ID: {job.id}")
            print(f"Title: {job.title}")
            print(f"Company: {job.company}")

            result = JobURLResolver.resolve(job.job_url)

            print(f"Success: {result.success}")
            print(f"Status: {result.status_code}")
            print(f"Reason: {result.reason}")
            print(f"Final URL: {result.final_url}")

            if result.final_url:
                print(
                    "Final domain: "
                    f"{urlparse(result.final_url).netloc}"
                )

    finally:
        session.close()


if __name__ == "__main__":
    main()