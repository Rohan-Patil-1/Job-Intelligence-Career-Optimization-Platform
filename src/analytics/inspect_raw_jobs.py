from src.database.connection import SessionLocal
from src.database.repository import JobRepository


def main() -> None:
    session = SessionLocal()

    try:
        repository = JobRepository(session)
        jobs = repository.get_all()

        for job in jobs[:5]:
            print("\n" + "=" * 80)
            print(f"ID: {job.id}")
            print(f"TITLE: {job.title}")
            print(f"\nDESCRIPTION:\n{job.description}")
            print(f"\nREQUIREMENTS:\n{job.requirements}")
            print(f"\nRESPONSIBILITIES:\n{job.responsibilities}")
            print(f"\nEXISTING SKILLS FIELD:\n{job.skills}")

    finally:
        session.close()


if __name__ == "__main__":
    main()