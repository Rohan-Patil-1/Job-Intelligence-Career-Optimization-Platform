from src.processing.normalizer import normalize_job


def test_normalize_job():
    raw_job = {
        "source": "test",
        "source_job_id": "123",
        "title": "  Machine   Learning   Engineer  ",
        "company": "  Example Corp  ",
        "location": " Chicago, IL ",
        "job_url": "https://example.com/job/123",
    }

    job = normalize_job(raw_job)

    assert job.title == "Machine Learning Engineer"
    assert job.company == "Example Corp"
    assert job.location == "Chicago, IL"
    assert job.source == "test"


def test_missing_optional_fields():
    raw_job = {
        "source": "test",
        "title": "Data Scientist",
        "company": "Example Corp",
        "job_url": "https://example.com/job/456",
    }

    job = normalize_job(raw_job)

    assert job.title == "Data Scientist"
    assert job.salary_min is None
    assert job.salary_max is None
    assert job.location is None