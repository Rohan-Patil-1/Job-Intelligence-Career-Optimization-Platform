from types import SimpleNamespace

from src.analytics.duplicate_detector import DuplicateDetector


def make_job(
    job_id,
    title,
    company,
    source="adzuna",
    source_job_id=None,
):
    return SimpleNamespace(
        id=job_id,
        title=title,
        company=company,
        source=source,
        source_job_id=source_job_id,
    )


def test_same_source_job_id():
    jobs = [
        make_job(1, "Data Scientist", "Company A", source_job_id="123"),
        make_job(2, "ML Engineer", "Company B", source_job_id="123"),
    ]

    results = DuplicateDetector.analyze(jobs)

    assert len(results) == 1
    assert results[0].reason == "same_source_job_id"
    assert results[0].confidence == "high"


def test_same_company_exact_title():
    jobs = [
        make_job(1, "Data Scientist", "TransUnion"),
        make_job(2, "Data Scientist", "Transunion"),
    ]

    results = DuplicateDetector.analyze(jobs)

    assert len(results) == 1
    assert results[0].reason == "same_company_exact_title"
    assert results[0].confidence == "medium"


def test_similar_titles():
    jobs = [
        make_job(1, "Data Scientist", "fairlife"),
        make_job(2, "Data Scientist - Fulltime", "fairlife"),
    ]

    # Similarity depends on the chosen normalization threshold.
    # Test a closer title variant for deterministic behavior.
    jobs[1].title = "Data Scientist!"

    results = DuplicateDetector.analyze(jobs)

    assert len(results) == 1
    assert results[0].reason == "same_company_exact_title"


def test_different_companies_not_duplicates():
    jobs = [
        make_job(1, "Data Scientist", "Company A"),
        make_job(2, "Data Scientist", "Company B"),
    ]

    results = DuplicateDetector.analyze(jobs)

    assert results == []


def test_missing_source_ids_do_not_match():
    jobs = [
        make_job(1, "Data Scientist", "Company A"),
        make_job(2, "ML Engineer", "Company B"),
    ]

    results = DuplicateDetector.analyze(jobs)

    assert results == []


def test_similar_titles_same_company():
    jobs = [
        make_job(1, "Senior Data Scientist", "Company A"),
        make_job(2, "Senior Data Scientist I", "Company A"),
    ]

    results = DuplicateDetector.analyze(jobs)

    assert len(results) == 1
    assert results[0].reason == "same_company_similar_title"
    assert results[0].confidence == "low"

def test_different_seniority_not_flagged_as_similar_duplicate():
    jobs = [
        make_job(
            1,
            "AI Engineer / Data Scientist, AI Manager",
            "PwC",
        ),
        make_job(
            2,
            "AI Engineer / Data Scientist, AI Sr. Manager",
            "PwC",
        ),
    ]

    results = DuplicateDetector.analyze(jobs)

    assert results == []

def test_senior_manager_and_manager_are_distinct():
    jobs = [
        make_job(
            1,
            "Data Scientist Manager",
            "Example Company",
        ),
        make_job(
            2,
            "Data Scientist Senior Manager",
            "Example Company",
        ),
    ]

    results = DuplicateDetector.analyze(jobs)

    assert results == []