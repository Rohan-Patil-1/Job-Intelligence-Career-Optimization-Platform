from src.config import ADZUNA_APP_ID, ADZUNA_APP_KEY
from src.ingestion.adzuna import AdzunaSource


def test_adzuna_live_connection():
    source = AdzunaSource(
        app_id=ADZUNA_APP_ID,
        app_key=ADZUNA_APP_KEY,
    )

    jobs = source.fetch_jobs(
        query="data scientist",
        location="Chicago",
        results_per_page=5,
    )

    assert isinstance(jobs, list)

    print(f"\nRetrieved {len(jobs)} jobs")

    if jobs:
        print("First job:")
        print(jobs[0])