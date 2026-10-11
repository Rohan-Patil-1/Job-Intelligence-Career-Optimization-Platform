from types import SimpleNamespace

from src.enrichment.source_validator import JobSourceValidator


def make_job():
    return SimpleNamespace(
        id=1,
        title="Data Scientist",
        company="Example Company",
        location="Chicago",
        source_job_id="12345",
    )


def test_verified_matching_source():
    result = JobSourceValidator.validate(
        job=make_job(),
        candidate_url="https://careers.example.com/jobs/12345",
        candidate_title="Data Scientist",
        candidate_company="Example Company",
        candidate_location="Chicago",
        candidate_requisition_id="12345",
        trusted_employer_source=True,
    )

    assert result.decision == "verified"


def test_unverified_employer_source():
    result = JobSourceValidator.validate(
        job=make_job(),
        candidate_url="https://example.com/jobs/12345",
        candidate_title="Data Scientist",
        candidate_company="Example Company",
        candidate_location="Chicago",
    )

    assert result.decision == "review_required"


def test_company_mismatch():
    result = JobSourceValidator.validate(
        job=make_job(),
        candidate_url="https://example.com/jobs/12345",
        candidate_title="Data Scientist",
        candidate_company="Different Company",
        candidate_location="Chicago",
    )

    assert result.decision == "rejected"


def test_title_mismatch():
    result = JobSourceValidator.validate(
        job=make_job(),
        candidate_url="https://example.com/jobs/12345",
        candidate_title="Marketing Manager",
        candidate_company="Example Company",
        candidate_location="Chicago",
    )

    assert result.decision == "rejected"


def test_invalid_url():
    result = JobSourceValidator.validate(
        job=make_job(),
        candidate_url="invalid-url",
        candidate_title="Data Scientist",
        candidate_company="Example Company",
        candidate_location="Chicago",
    )

    assert result.decision == "rejected"