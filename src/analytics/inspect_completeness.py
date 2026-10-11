from src.analytics.data_completeness import (
    DataCompletenessAnalyzer,
)
from src.database.connection import SessionLocal
from src.database.repository import JobRepository


def main() -> None:
    session = SessionLocal()

    try:
        jobs = JobRepository(session).get_all()

        summary = DataCompletenessAnalyzer.analyze_jobs(jobs)

        print("\n=== Job Data Completeness Audit ===")
        print(f"Total jobs: {summary.total_jobs}")
        print(
            f"Average completeness: "
            f"{summary.average_completeness:.2f}%"
        )

        print("\nMissing Fields:")

        for field, count in sorted(
            summary.missing_field_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            percentage = (
                count / summary.total_jobs * 100
                if summary.total_jobs
                else 0.0
            )

            print(
                f"  {field}: {count} "
                f"({percentage:.1f}%)"
            )

        print("\nQuality Distribution:")

        for label in ("high", "medium", "low"):
            print(
                f"  {label}: "
                f"{summary.quality_distribution.get(label, 0)}"
            )

        print("\nJobs With Lowest Completeness:")

        ranked = sorted(
            summary.jobs,
            key=lambda item: (
                item.completeness_score,
                item.description_length,
            ),
        )

        for item in ranked[:10]:
            print("\n" + "-" * 65)

            print(
                f"[{item.job_id}] "
                f"{item.title} | {item.company}"
            )

            print(
                f"Completeness: "
                f"{item.completeness_score:.2f}%"
            )

            print(
                f"Description length: "
                f"{item.description_length} characters"
            )

            print(
                "Missing: "
                + (
                    ", ".join(item.missing_fields)
                    if item.missing_fields
                    else "None"
                )
            )

    finally:
        session.close()


if __name__ == "__main__":
    main()