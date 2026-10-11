from types import SimpleNamespace

from src.analytics.data_completeness import (
    DataCompletenessAnalyzer,
)


def make_job(**overrides):
    values = {
        "id": 1,
        "title": "Data Scientist",
        "company": "Example",
        "location": "Chicago",
        "description": "Python and machine learning.",
        "requirements": "Python",
        "responsibilities": "Build ML models",
        "skills": "Python, SQL",
        "job_url": "https://example.com/job/1",
        "salary_min": 90000,
        "salary_max": 120000,
    }

    values.update(overrides)
    return SimpleNamespace(**values)


def test_complete_job():
    result = DataCompletenessAnalyzer.analyze_job(
        make_job()
    )

    assert result.completeness_score == 100.0
    assert result.missing_fields == ()
    assert result.quality_label == "high"


def test_missing_fields():
    result = DataCompletenessAnalyzer.analyze_job(
        make_job(
            requirements=None,
            responsibilities="",
            skills=None,
            salary_min=None,
            salary_max=None,
        )
    )

    assert "requirements" in result.missing_fields
    assert "responsibilities" in result.missing_fields
    assert "skills" in result.missing_fields
    assert "salary" in result.missing_fields


def test_partial_salary_is_available():
    result = DataCompletenessAnalyzer.analyze_job(
        make_job(
            salary_min=90000,
            salary_max=None,
        )
    )

    assert "salary" not in result.missing_fields


def test_empty_job_collection():
    summary = DataCompletenessAnalyzer.analyze_jobs([])

    assert summary.total_jobs == 0
    assert summary.average_completeness == 0.0
    assert summary.jobs == ()


def test_quality_distribution():
    jobs = [
        make_job(id=1),
        make_job(
            id=2,
            requirements=None,
            responsibilities=None,
            skills=None,
            salary_min=None,
            salary_max=None,
        ),
    ]

    summary = DataCompletenessAnalyzer.analyze_jobs(jobs)

    assert summary.total_jobs == 2
    assert summary.quality_distribution["high"] == 1
    assert summary.quality_distribution["medium"] == 1