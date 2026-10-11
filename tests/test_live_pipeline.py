from src.config import ADZUNA_APP_ID, ADZUNA_APP_KEY
from src.ingestion.adzuna import AdzunaSource
from src.processing.normalizer import normalize_job
import pytest
import requests

def test_live_adzuna_pipeline():
    source = AdzunaSource(
        app_id=ADZUNA_APP_ID,
        app_key=ADZUNA_APP_KEY,
    )

    try:
        raw_jobs = source.fetch_jobs(
            query="data scientist",
            location="Chicago",
            results_per_page=5,
        )
    except requests.HTTPError as exc:
        status_code = (
            exc.response.status_code
            if exc.response is not None
            else None
        )

        if status_code in (429, 500, 502, 503, 504):
            pytest.skip(
                f"Adzuna API temporarily unavailable: HTTP {status_code}"
            )

        raise

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