from src.analytics.seniority import SeniorityLevel
from src.analytics.seniority_fit import SeniorityFitAnalyzer
from src.database.models import Job


def make_job(title: str) -> Job:
    return Job(
        source="test",
        title=title,
        company="Test Company",
        job_url="https://example.com/job",
    )


def make_analyzer() -> SeniorityFitAnalyzer:
    return SeniorityFitAnalyzer(
        {
            SeniorityLevel.ENTRY,
            SeniorityLevel.MID,
        }
    )


def test_entry_is_target():
    result = make_analyzer().analyze(
        make_job("Junior Data Scientist")
    )

    assert result.fit_score == 100.0
    assert result.fit_label == "target"


def test_mid_is_target():
    result = make_analyzer().analyze(
        make_job("Data Scientist")
    )

    assert result.fit_score == 100.0
    assert result.fit_label == "target"


def test_senior_is_stretch():
    result = make_analyzer().analyze(
        make_job("Senior Data Scientist")
    )

    assert result.fit_score == 70.0
    assert result.fit_label == "stretch"


def test_lead_is_high_stretch():
    result = make_analyzer().analyze(
        make_job("Lead Data Scientist")
    )

    assert result.fit_score == 40.0
    assert result.fit_label == "high_stretch"


def test_manager_is_unlikely():
    result = make_analyzer().analyze(
        make_job("Data Science Manager")
    )

    assert result.fit_score == 15.0
    assert result.fit_label == "unlikely"


def test_vp_is_poor_fit():
    result = make_analyzer().analyze(
        make_job("VP Data Scientist")
    )

    assert result.fit_score == 0.0
    assert result.fit_label == "poor_fit"


def test_empty_targets():
    analyzer = SeniorityFitAnalyzer(set())

    result = analyzer.analyze(
        make_job("Data Scientist")
    )

    assert result.fit_score == 0.0
    assert result.fit_label == "unknown"