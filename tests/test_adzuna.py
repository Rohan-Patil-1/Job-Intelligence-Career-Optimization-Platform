from src.ingestion.adzuna import AdzunaSource


def test_adzuna_response_normalization():
    raw_response = {
        "id": 12345,
        "title": "Machine Learning Engineer",
        "company": {
            "display_name": "Example AI"
        },
        "location": {
            "display_name": "Chicago, IL"
        },
        "salary_min": 90000,
        "salary_max": 120000,
        "description": "Build machine learning systems.",
        "redirect_url": "https://example.com/job/12345",
        "created": "2026-10-01T12:00:00Z",
    }

    normalized = AdzunaSource._normalize_response(
        raw_response
    )

    assert normalized["source"] == "adzuna"
    assert normalized["source_job_id"] == "12345"
    assert normalized["title"] == "Machine Learning Engineer"
    assert normalized["company"] == "Example AI"
    assert normalized["location"] == "Chicago, IL"
    assert normalized["salary_min"] == 90000
    assert normalized["salary_max"] == 120000
    assert normalized["salary_currency"] == "USD"
    assert normalized["job_url"] == "https://example.com/job/12345"