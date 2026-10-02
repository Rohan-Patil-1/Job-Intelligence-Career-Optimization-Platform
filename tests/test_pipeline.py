from src.ingestion.adzuna import AdzunaSource
from src.processing.normalizer import normalize_job


def test_adzuna_to_job_record_pipeline():
    raw_adzuna_job = {
        "id": 98765,
        "title": "  Data Scientist  ",
        "company": {
            "display_name": "  Example Analytics  "
        },
        "location": {
            "display_name": " Chicago, IL "
        },
        "salary_min": 85000,
        "salary_max": 110000,
        "description": "Analyze data and build machine learning models.",
        "redirect_url": "https://example.com/jobs/98765",
        "created": "2026-10-01T12:00:00Z",
    }

    normalized_data = AdzunaSource._normalize_response(
        raw_adzuna_job
    )

    job = normalize_job(normalized_data)

    assert job.source == "adzuna"
    assert job.source_job_id == "98765"
    assert job.title == "Data Scientist"
    assert job.company == "Example Analytics"
    assert job.location == "Chicago, IL"
    assert job.salary_min == 85000
    assert job.salary_max == 110000
    assert job.job_url == "https://example.com/jobs/98765"