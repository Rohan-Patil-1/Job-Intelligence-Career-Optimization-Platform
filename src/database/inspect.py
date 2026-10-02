from sqlalchemy import func, select

from src.database.connection import SessionLocal
from src.database.models import Job


def inspect_database() -> None:
    session = SessionLocal()

    try:
        total_jobs = session.scalar(
            select(func.count()).select_from(Job)
        )

        source_counts = session.execute(
            select(Job.source, func.count())
            .group_by(Job.source)
        ).all()

        company_counts = session.execute(
            select(Job.company, func.count())
            .group_by(Job.company)
            .order_by(func.count().desc())
            .limit(10)
        ).all()

        location_counts = session.execute(
            select(Job.location, func.count())
            .where(Job.location.is_not(None))
            .group_by(Job.location)
            .order_by(func.count().desc())
            .limit(10)
        ).all()

        print("\n=== Job Database Summary ===")
        print(f"Total jobs: {total_jobs}")

        print("\nJobs by source:")
        for source, count in source_counts:
            print(f"  {source}: {count}")

        print("\nTop companies:")
        for company, count in company_counts:
            print(f"  {company}: {count}")

        print("\nTop locations:")
        for location, count in location_counts:
            print(f"  {location}: {count}")

    finally:
        session.close()


if __name__ == "__main__":
    inspect_database()