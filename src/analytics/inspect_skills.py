"""
Inspect extracted skills across the current job database.

Read-only: does not modify the database.
"""

from collections import Counter

from src.analytics.skill_extractor import extract_skills
from src.database.connection import SessionLocal
from src.database.repository import JobRepository


def main() -> None:
    session = SessionLocal()

    try:
        repository = JobRepository(session)
        jobs = repository.get_all()

        print("\n=== Skill Extraction Inspection ===")
        print(f"Jobs analyzed: {len(jobs)}")

        skill_counts = Counter()

        for job in jobs:
            text = " ".join(
                value
                for value in (
                    job.title,
                    job.description,
                    job.requirements,
                    job.responsibilities,
                )
                if value
            )

            skills = extract_skills(text)
            skill_counts.update(skills)

            print("\n" + "=" * 70)
            print(f"Job ID: {job.id}")
            print(f"Title: {job.title}")
            print(f"Company: {job.company}")
            print(f"Skills: {', '.join(skills) if skills else 'None'}")

        print("\n" + "=" * 70)
        print("\n=== Skill Frequency ===")

        if not skill_counts:
            print("No skills extracted.")
            return

        for skill, count in skill_counts.most_common():
            percentage = (count / len(jobs)) * 100

            print(
                f"{skill:<35} "
                f"{count:>3} jobs "
                f"({percentage:>5.1f}%)"
            )

    finally:
        session.close()


if __name__ == "__main__":
    main()