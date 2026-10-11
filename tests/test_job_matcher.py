from src.analytics.job_matcher import JobMatcher
from src.database.models import Job


def make_job(
    title: str,
    description: str | None = None,
    company: str = "Test Company",
) -> Job:
    return Job(
        source="test",
        title=title,
        company=company,
        description=description,
        job_url="https://example.com/job",
    )


def test_full_job_match():
    job = make_job(
        "Data Scientist",
        "Python SQL machine learning statistics",
    )

    matcher = JobMatcher(
        {
            "python",
            "sql",
            "machine learning",
            "statistics",
        }
    )

    result = matcher.match_job(job)

    assert result.match_percentage == 100.0
    assert result.missing_skills == ()
    assert len(result.matched_skills) == 4


def test_partial_job_match():
    job = make_job(
        "ML Engineer",
        "Python PyTorch AWS Docker",
    )

    matcher = JobMatcher(
        {
            "python",
            "pytorch",
        }
    )

    result = matcher.match_job(job)

    assert result.match_percentage == 50.0

    assert result.matched_skills == (
        "python",
        "pytorch",
    )

    assert result.missing_skills == (
        "aws",
        "docker",
    )


def test_no_detected_skills_returns_zero():
    job = make_job(
        "Research Scientist",
        "Work with scientific teams.",
    )

    matcher = JobMatcher(
        {"python", "sql"}
    )

    result = matcher.match_job(job)

    assert result.match_percentage == 0.0
    assert result.detected_skills == ()
    assert result.matched_skills == ()
    assert result.missing_skills == ()


def test_no_candidate_skill_match():
    job = make_job(
        "Cloud Engineer",
        "AWS Docker Kubernetes",
    )

    matcher = JobMatcher(
        {"python", "sql"}
    )

    result = matcher.match_job(job)

    assert result.match_percentage == 0.0
    assert result.matched_skills == ()

    assert result.missing_skills == (
        "aws",
        "docker",
        "kubernetes",
    )


def test_candidate_skills_are_normalized():
    job = make_job(
        "Data Scientist",
        "Python SQL",
    )

    matcher = JobMatcher(
        {
            " Python ",
            "SQL",
        }
    )

    result = matcher.match_job(job)

    assert result.match_percentage == 100.0


def test_jobs_ranked_by_match_percentage():
    jobs = [
        make_job(
            "Job A",
            "Python SQL AWS Docker",
        ),
        make_job(
            "Job B",
            "Python SQL",
        ),
        make_job(
            "Job C",
            "Python AWS Docker",
        ),
    ]

    matcher = JobMatcher(
        {
            "python",
            "sql",
        }
    )

    results = matcher.rank_jobs(jobs)

    assert results[0].title == "Job B"
    assert results[0].match_percentage == 100.0

    assert results[1].title == "Job A"
    assert results[1].match_percentage == 50.0

    assert results[2].title == "Job C"
    assert results[2].match_percentage == 33.33


def test_ranking_uses_detected_skills_as_tiebreaker():
    jobs = [
        make_job(
            "Job A",
            "Python",
        ),
        make_job(
            "Job B",
            "Python SQL machine learning",
        ),
    ]

    matcher = JobMatcher(
        {
            "python",
            "sql",
            "machine learning",
        }
    )

    results = matcher.rank_jobs(jobs)

    assert results[0].title == "Job B"
    assert results[1].title == "Job A"

def test_evidence_increases_with_detected_skills():
    matcher = JobMatcher(
        {
            "python",
            "sql",
            "machine learning",
            "statistics",
        }
    )

    weak_job = make_job(
        "Weak Evidence",
        "Python",
    )

    strong_job = make_job(
        "Strong Evidence",
        "Python SQL machine learning statistics",
    )

    weak = matcher.match_job(weak_job)
    strong = matcher.match_job(strong_job)

    assert strong.evidence_score > weak.evidence_score
    assert strong.ranking_score > weak.ranking_score


def test_zero_skills_is_insufficient_evidence():
    job = make_job(
        "Unknown Job",
        "Work with business teams.",
    )

    matcher = JobMatcher(
        {"python"}
    )

    result = matcher.match_job(job)

    assert result.match_percentage == 0.0
    assert result.evidence_score == 0.0
    assert result.ranking_score == 0.0
    assert result.evidence_level == "insufficient"


def test_single_skill_has_low_evidence():
    job = make_job(
        "Python Job",
        "Python",
    )

    matcher = JobMatcher(
        {"python"}
    )

    result = matcher.match_job(job)

    assert result.match_percentage == 100.0
    assert result.evidence_level == "low"
    assert result.ranking_score < 100.0


def test_ranking_prefers_more_evidence():
    jobs = [
        make_job(
            "Weak Match",
            "Python",
        ),
        make_job(
            "Strong Match",
            "Python SQL machine learning statistics",
        ),
    ]

    matcher = JobMatcher(
        {
            "python",
            "sql",
            "machine learning",
            "statistics",
        }
    )

    results = matcher.rank_jobs(jobs)

    assert results[0].title == "Strong Match"
    assert results[1].title == "Weak Match"