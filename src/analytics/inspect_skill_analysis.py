from src.analytics.skills import SkillAnalyzer
from src.database.connection import SessionLocal
from src.database.repository import JobRepository


def main() -> None:
    session = SessionLocal()

    try:
        jobs = JobRepository(session).get_all()
        analyzer = SkillAnalyzer(jobs)

        print("\n=== Skill Analysis ===")
        print(f"Total jobs: {len(jobs)}")
        print(f"Jobs with detected skills: {analyzer.jobs_with_skills()}")
        print(
            f"Extraction coverage: "
            f"{analyzer.coverage_percentage():.2f}%"
        )

        print("\n=== Observed Skill Mentions ===")

        for stat in analyzer.skill_stats():
            print(
                f"{stat.skill:<35}"
                f"{stat.job_count:>3} jobs "
                f"({stat.percentage:>6.2f}%)"
            )

        print("\nNOTE:")
        print(
            "Adzuna descriptions are partial ~500-character snippets. "
            "Percentages represent observed mentions, not true market demand."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()