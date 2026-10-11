from collections import Counter

from src.analytics.seniority import detect_seniority
from src.database.connection import SessionLocal
from src.database.repository import JobRepository


def main() -> None:
    session = SessionLocal()

    try:
        jobs = JobRepository(session).get_all()

        counts = Counter()

        print("\n=== Job Seniority Inspection ===")
        print(f"Jobs analyzed: {len(jobs)}")

        for job in jobs:
            seniority = detect_seniority(job.title)

            counts[seniority.label] += 1

            print(
                f"{job.id:>3} | "
                f"{seniority.label:<10} | "
                f"{job.title} | "
                f"{job.company}"
            )

        print("\n=== Seniority Distribution ===")

        for label, count in counts.most_common():
            percentage = (
                count / len(jobs) * 100
                if jobs
                else 0.0
            )

            print(
                f"{label:<10} "
                f"{count:>3} jobs "
                f"({percentage:>6.2f}%)"
            )

    finally:
        session.close()


if __name__ == "__main__":
    main()