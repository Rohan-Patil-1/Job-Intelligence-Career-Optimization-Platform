from sqlalchemy import inspect

from src.database.connection import engine
from src.database.models import Base, Job, JobEnrichment


def init_db() -> None:
    print("\n=== Database Initialization ===")

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print("Database tables:")
    for table in tables:
        print(f"  - {table}")

    if "job_enrichments" in tables:
        print("\nJob enrichment table is ready.")
    else:
        raise RuntimeError(
            "Failed to create job_enrichments table."
        )


if __name__ == "__main__":
    init_db()