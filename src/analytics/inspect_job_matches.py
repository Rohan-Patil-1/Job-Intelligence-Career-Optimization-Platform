from src.analytics.job_matcher import JobMatcher
from src.database.connection import SessionLocal
from src.database.repository import JobRepository
from src.profile.default_profile import DEFAULT_PROFILE


def main() -> None:
    session = SessionLocal()

    try:
        jobs = JobRepository(session).get_all()

        matcher = JobMatcher(
            DEFAULT_PROFILE.normalized_skills()
        )

        matches = matcher.rank_jobs(jobs)

        print("\n=== Candidate Job Ranking ===")
        print(f"Candidate: {DEFAULT_PROFILE.name}")
        print(f"Jobs analyzed: {len(jobs)}")

        for rank, result in enumerate(
            matches,
            start=1,
        ):
            print("\n" + "=" * 70)

            print(
                f"#{rank} | "
                f"{result.title} | "
                f"{result.company}"
            )

            print(
                f"Skill match: "
                f"{result.match_percentage:.2f}%"
            )

            print(
                f"Evidence: "
                f"{result.evidence_score:.2f}% "
                f"({result.evidence_level})"
            )

            print(
                f"Ranking score: "
                f"{result.ranking_score:.2f}"
            )

            print(
                f"Detected skills: "
                f"{len(result.detected_skills)}"
            )

            print(
                "Matched: "
                + (
                    ", ".join(result.matched_skills)
                    if result.matched_skills
                    else "None"
                )
            )

            print(
                "Missing: "
                + (
                    ", ".join(result.missing_skills)
                    if result.missing_skills
                    else "None"
                )
            )

        print("\n" + "=" * 70)

        print(
        "\nNOTE: Ranking score combines observed skill match "
        "with evidence availability. Jobs with insufficient "
        "posting evidence are unscored rather than treated "
        "as confirmed poor matches."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()