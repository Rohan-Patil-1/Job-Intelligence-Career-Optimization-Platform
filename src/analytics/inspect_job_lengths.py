from src.database.connection import SessionLocal
from src.database.repository import JobRepository


def main() -> None:
    session = SessionLocal()

    try:
        repository = JobRepository(session)
        jobs = repository.get_all()

        print("\n=== Job Description Lengths ===")

        for job in jobs:
            description_length = len(job.description or "")
            requirements_length = len(job.requirements or "")
            responsibilities_length = len(job.responsibilities or "")

            print(
                f"ID={job.id:<3} "
                f"Title={job.title[:45]:<45} "
                f"Description={description_length:<5} "
                f"Requirements={requirements_length:<5} "
                f"Responsibilities={responsibilities_length:<5}"
            )

    finally:
        session.close()


if __name__ == "__main__":
    main()