from collections import Counter

from src.database.connection import SessionLocal
from src.database.repository import JobRepository


def main() -> None:
    session = SessionLocal()

    try:
        jobs = JobRepository(session).get_all()

        print("\n=== Job Source Data Inspection ===")
        print(f"Total jobs: {len(jobs)}")

        description_lengths = [
            len((job.description or "").strip())
            for job in jobs
        ]

        print("\nDescription Length Distribution:")

        for length, count in sorted(
            Counter(description_lengths).items()
        ):
            print(f"  {length} characters: {count} jobs")

        print("\nSource Distribution:")

        for source, count in Counter(
            job.source for job in jobs
        ).items():
            print(f"  {source}: {count}")

        print("\nSample Job Records:")

        for job in jobs[:5]:
            print("\n" + "=" * 70)

            print(f"ID: {job.id}")
            print(f"Source: {job.source}")
            print(f"Source Job ID: {job.source_job_id}")
            print(f"Title: {job.title}")
            print(f"Company: {job.company}")
            print(f"Job URL: {job.job_url}")

            print(
                "Description length: "
                f"{len(job.description or '')}"
            )

            print(
                "Description:\n"
                f"{job.description or 'None'}"
            )

    finally:
        session.close()


if __name__ == "__main__":
    main()