from src.config import ADZUNA_APP_ID, ADZUNA_APP_KEY
from src.database.connection import SessionLocal, init_db
from src.ingestion.adzuna import AdzunaSource
from src.ingestion.pipeline import ingest_jobs


def test_live_adzuna_ingestion():
    init_db()

    source = AdzunaSource(
        app_id=ADZUNA_APP_ID,
        app_key=ADZUNA_APP_KEY,
    )

    session = SessionLocal()

    try:
        result = ingest_jobs(
            source=source,
            session=session,
            query="data scientist",
            location="Chicago",
        )

        print("\n--- Live Ingestion Result ---")
        print(f"Fetched:    {result.fetched}")
        print(f"Inserted:   {result.inserted}")
        print(f"Duplicates: {result.duplicates}")
        print(f"Failed:     {result.failed}")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(
                    f"- {error.source_job_id}: "
                    f"{error.error_type}: {error.message}"
                )

        assert result.fetched > 0
        assert result.inserted + result.duplicates + result.failed == result.fetched

    finally:
        session.close()