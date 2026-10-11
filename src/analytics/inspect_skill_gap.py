from src.analytics.skill_gap import SkillGapAnalyzer
from src.database.connection import SessionLocal
from src.database.repository import JobRepository
from src.profile.default_profile import DEFAULT_PROFILE


def main() -> None:
    session = SessionLocal()

    try:
        jobs = JobRepository(session).get_all()

        analyzer = SkillGapAnalyzer(
            jobs=jobs,
            candidate_skills=DEFAULT_PROFILE.normalized_skills(),
        )

        summary = analyzer.summary()

        print("\n=== Candidate Skill Gap Analysis ===")
        print(f"Candidate: {DEFAULT_PROFILE.name}")
        print(f"Jobs analyzed: {len(jobs)}")

        print("\n=== Summary ===")
        print(f"Market skills observed: {summary.market_skills}")
        print(f"Candidate skills: {summary.candidate_skills}")
        print(f"Matched skills: {summary.matched_skills}")
        print(f"Missing skills: {summary.missing_skills}")
        print(f"Skill match: {summary.match_percentage:.2f}%")

        print(
            f"Weighted skill alignment: "
            f"{summary.weighted_match_percentage:.2f}%"
        )

        print("\n=== Matched Skills ===")

        matched = analyzer.matched_skills()

        if matched:
            for skill in matched:
                print(f"  + {skill}")
        else:
            print("  None")

        print("\n=== Observed Skill Gaps ===")

        gaps = analyzer.missing_skills()

        if gaps:
            for gap in gaps:
                print(
                    f"  - {gap.skill:<30}"
                    f"{gap.job_count:>3} jobs "
                    f"({gap.observed_percentage:>6.2f}%)"
                )
        else:
            print("  None")

        print("\nNOTE:")
        print(
            "Current Adzuna descriptions are partial snippets. "
            "Skill-gap results represent observed evidence, "
            "not complete market demand."
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()