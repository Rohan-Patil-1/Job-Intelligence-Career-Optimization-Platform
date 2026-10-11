from src.analytics.skill_gap import SkillGapAnalyzer
from src.database.models import Job


def make_job(
    title: str,
    description: str | None = None,
) -> Job:
    return Job(
        source="test",
        title=title,
        company="Test Company",
        description=description,
        job_url="https://example.com/job",
    )


def test_matched_skills():
    jobs = [
        make_job(
            "Data Scientist",
            "Python SQL machine learning AWS",
        ),
        make_job(
            "ML Engineer",
            "Python PyTorch Docker",
        ),
    ]

    candidate_skills = {
        "python",
        "sql",
        "pytorch",
    }

    analyzer = SkillGapAnalyzer(
        jobs,
        candidate_skills,
    )

    assert analyzer.matched_skills() == [
        "python",
        "pytorch",
        "sql",
    ]


def test_missing_skills_ranked_by_demand():
    jobs = [
        make_job(
            "Job 1",
            "Python AWS Docker",
        ),
        make_job(
            "Job 2",
            "Python AWS",
        ),
        make_job(
            "Job 3",
            "Python machine learning",
        ),
    ]

    analyzer = SkillGapAnalyzer(
        jobs,
        {"python"},
    )

    gaps = analyzer.missing_skills()

    assert gaps[0].skill == "aws"
    assert gaps[0].job_count == 2

    missing_names = {
        gap.skill
        for gap in gaps
    }

    assert missing_names == {
        "aws",
        "docker",
        "machine learning",
    }


def test_summary():
    jobs = [
        make_job(
            "Job 1",
            "Python SQL AWS",
        ),
        make_job(
            "Job 2",
            "Python Docker",
        ),
    ]

    analyzer = SkillGapAnalyzer(
        jobs,
        {
            "python",
            "sql",
        },
    )

    summary = analyzer.summary()

    assert summary.market_skills == 4
    assert summary.candidate_skills == 2
    assert summary.matched_skills == 2
    assert summary.missing_skills == 2
    assert summary.match_percentage == 50.0


def test_candidate_skills_are_normalized():
    jobs = [
        make_job(
            "Job",
            "Python SQL",
        ),
    ]

    analyzer = SkillGapAnalyzer(
        jobs,
        {
            " Python ",
            "SQL",
        },
    )

    assert analyzer.matched_skills() == [
        "python",
        "sql",
    ]


def test_empty_market():
    analyzer = SkillGapAnalyzer(
        [],
        {"python", "sql"},
    )

    summary = analyzer.summary()

    assert summary.market_skills == 0
    assert summary.matched_skills == 0
    assert summary.missing_skills == 0
    assert summary.match_percentage == 0.0

    assert analyzer.matched_skills() == []
    assert analyzer.missing_skills() == []


def test_weighted_match_percentage():
    jobs = [
        make_job("Job 1", "Python AWS"),
        make_job("Job 2", "Python AWS"),
        make_job("Job 3", "Python"),
        make_job("Job 4", "Python Docker"),
    ]

    analyzer = SkillGapAnalyzer(
        jobs,
        {"python"},
    )

    # Observed occurrences:
    #
    # python = 4
    # aws = 2
    # docker = 1
    #
    # total weight = 7
    # matched weight = 4
    #
    # 4 / 7 = 57.14%

    assert analyzer.weighted_match_percentage() == 57.14


def test_weighted_match_empty_market():
    analyzer = SkillGapAnalyzer(
        [],
        {"python"},
    )

    assert analyzer.weighted_match_percentage() == 0.0