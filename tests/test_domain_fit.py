from src.analytics.domain_fit import DomainFitAnalyzer
from src.database.models import Job


def make_job(title: str, description: str = "") -> Job:
    return Job(
        source="test",
        title=title,
        company="Test Company",
        description=description,
        job_url="https://example.com/job",
    )


def make_analyzer() -> DomainFitAnalyzer:
    return DomainFitAnalyzer(
        {"healthcare", "medical_imaging", "ai_research"}
    )


def test_preferred_healthcare_domain():
    result = make_analyzer().analyze(
        make_job("Data Scientist", "Clinical patient data")
    )

    assert result.score == 100.0
    assert result.label == "preferred"


def test_other_domain():
    result = make_analyzer().analyze(
        make_job("Data Scientist", "Banking and credit risk")
    )

    assert result.score == 40.0
    assert result.label == "other_domain"


def test_unknown_domain():
    result = make_analyzer().analyze(
        make_job("Data Scientist", "Build data models")
    )

    assert result.score == 0.0
    assert result.label == "unknown"


def test_multiple_preferred_domains():
    result = make_analyzer().analyze(
        make_job(
            "Medical Imaging Research Scientist",
            "Clinical radiology research",
        )
    )

    assert "healthcare" in result.matched_domains
    assert "medical_imaging" in result.matched_domains

def test_domain_evidence_count():
    analyzer = make_analyzer()

    job = make_job(
        "Data Scientist, Life Sciences",
        "Clinical healthcare research using real world evidence.",
    )

    result = analyzer.analyze(job)

    assert result.evidence_count >= 3
    assert result.evidence_level in {"medium", "high"}


def test_repeated_keyword_not_double_counted():
    analyzer = make_analyzer()

    job = make_job(
        "Clinical Data Scientist",
        "Clinical clinical clinical data.",
    )

    result = analyzer.analyze(job)

    assert result.evidence_count == 1
    assert result.evidence_level == "low"


def test_domain_evidence_sources():
    analyzer = make_analyzer()

    job = make_job(
        "Medical Imaging Scientist",
        "Clinical radiology research.",
    )

    result = analyzer.analyze(job)

    assert "title" in result.evidence_sources
    assert "description" in result.evidence_sources

    assert "medical_imaging" in result.evidence_by_source["title"]
    assert "healthcare" in result.evidence_by_source["description"]


def test_unknown_domain_has_no_evidence():
    analyzer = make_analyzer()

    job = make_job(
        "Data Scientist",
        "Build predictive models.",
    )

    result = analyzer.analyze(job)

    assert result.evidence_count == 0
    assert result.evidence_level == "insufficient"
    assert result.evidence_sources == ()


def test_same_keyword_across_sources_counted_once():
    analyzer = make_analyzer()

    job = make_job(
        "Clinical Data Scientist",
        "Work with clinical data.",
    )

    result = analyzer.analyze(job)

    assert result.evidence_count == 1
    assert result.evidence_sources == ("title", "description")