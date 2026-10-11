import pytest

from src.analytics.role_fit import RoleFitAnalyzer
from src.database.models import Job


def make_job(title: str) -> Job:
    return Job(
        source="test",
        title=title,
        company="Test Company",
        job_url="https://example.com",
    )


@pytest.fixture
def analyzer():
    return RoleFitAnalyzer(
        [
            "data scientist",
            "machine learning engineer",
            "ai engineer",
            "applied scientist",
        ]
    )


@pytest.mark.parametrize(
    "title",
    [
        "Data Scientist",
        "Senior Data Scientist",
        "Data Scientist II",
        "AI Engineer",
        "AI Engineer / Data Scientist",
        "Machine Learning Engineer",
        "Applied Scientist",
    ],
)
def test_target_roles(analyzer, title):
    result = analyzer.analyze(
        make_job(title)
    )

    assert result.score == 100.0
    assert result.label == "target"


def test_data_analyst_is_related(analyzer):
    result = analyzer.analyze(
        make_job("Data Analyst")
    )

    assert result.score == 70.0
    assert result.label == "related"


def test_research_scientist_is_related(analyzer):
    result = analyzer.analyze(
        make_job("Research Scientist")
    )

    assert result.score == 85.0
    assert result.label == "related"


def test_unrelated_role_is_weak(analyzer):
    result = analyzer.analyze(
        make_job("Java Developer")
    )

    assert result.score == 20.0
    assert result.label == "weak"


def test_empty_title():
    analyzer = RoleFitAnalyzer(
        ["data scientist"]
    )

    result = analyzer.analyze(
        make_job("")
    )

    assert result.score == 0.0
    assert result.label == "unknown"