from collections import Counter

from src.analytics.duplicate_detector import DuplicateDetector
from src.database.connection import SessionLocal
from src.database.repository import JobRepository


def main() -> None:
    session = SessionLocal()

    try:
        jobs = JobRepository(session).get_all()
        duplicates = DuplicateDetector.analyze(jobs)

        print("\n=== Duplicate Job Audit ===")
        print(f"Total jobs: {len(jobs)}")
        print(f"Suspected duplicate pairs: {len(duplicates)}")

        counts = Counter(
            item.reason for item in duplicates
        )

        print("\nDuplicate Reasons:")
        for reason, count in sorted(counts.items()):
            print(f"  {reason}: {count}")

        for index, item in enumerate(duplicates, start=1):
            print("\n" + "=" * 70)

            print(f"Pair #{index}")
            print(f"Company: {item.company}")

            print(
                f"Job A [{item.job_id_1}]: "
                f"{item.title_1}"
            )

            print(
                f"Job B [{item.job_id_2}]: "
                f"{item.title_2}"
            )

            print(f"Title similarity: {item.similarity:.3f}")
            print(f"Reason: {item.reason}")
            print(f"Confidence: {item.confidence}")

    finally:
        session.close()


if __name__ == "__main__":
    main()