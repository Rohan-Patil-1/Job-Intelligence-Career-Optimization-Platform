from src.config import ADZUNA_APP_ID, ADZUNA_APP_KEY
from src.ingestion.adzuna import AdzunaSource
from src.processing.normalizer import normalize_job


def test_live_adzuna_pipeline():
    source = AdzunaSource(
        app_id=ADZUNA_APP_ID,
        app_key=ADZUNA_APP_KEY,
    )

    raw_jobs = source.fetch_jobs(
        query="data scientist",
        location="Chicago",
        results_per_page=5,
    )

    assert len(raw_jobs) > 0

    jobs = [
        normalize_job(raw_job)
        for raw_job in raw_jobs
    ]

    assert len(jobs) == len(raw_jobs)

    for job in jobs:
        assert job.source == "adzuna"
        assert job.title
        assert job.company
        assert job.job_url
        assert job.collected_at is not None

        if job.posted_at is not None:
            assert job.posted_at.year >= 2020