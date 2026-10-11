from src.analytics.skills import SkillAnalyzer
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


def test_skill_counts():
    jobs = [
        make_job(
            "Data Scientist",
            "Python, SQL and machine learning.",
        ),
        make_job(
            "ML Engineer",
            "Python, PyTorch and AWS.",
        ),
    ]

    analyzer = SkillAnalyzer(jobs)

    counts = analyzer.skill_counts()

    assert counts["python"] == 2
    assert counts["sql"] == 1
    assert counts["machine learning"] == 1
    assert counts["pytorch"] == 1
    assert counts["aws"] == 1


def test_skill_count_once_per_job():
    job = make_job(
        "Python Developer",
        "Python Python3 python 3",
    )

    analyzer = SkillAnalyzer([job])

    assert analyzer.skill_counts()["python"] == 1


def test_skill_stats():
    jobs = [
        make_job(
            "Data Scientist",
            "Python and SQL",
        ),
        make_job(
            "ML Engineer",
            "Python and AWS",
        ),
    ]

    analyzer = SkillAnalyzer(jobs)

    stats = {
        stat.skill: stat
        for stat in analyzer.skill_stats()
    }

    assert stats["python"].job_count == 2
    assert stats["python"].percentage == 100.0

    assert stats["sql"].job_count == 1
    assert stats["sql"].percentage == 50.0


def test_jobs_with_skills():
    jobs = [
        make_job(
            "Data Scientist",
            "Python and SQL",
        ),
        make_job(
            "Business Analyst",
            "Strong communication skills.",
        ),
    ]

    analyzer = SkillAnalyzer(jobs)

    assert analyzer.jobs_with_skills() == 1


def test_coverage_percentage():
    jobs = [
        make_job(
            "Data Scientist",
            "Python",
        ),
        make_job(
            "Analyst",
            "SQL",
        ),
        make_job(
            "Manager",
            "Leadership experience.",
        ),
        make_job(
            "Consultant",
            "Client-facing role.",
        ),
    ]

    analyzer = SkillAnalyzer(jobs)

    assert analyzer.coverage_percentage() == 50.0


def test_empty_jobs():
    analyzer = SkillAnalyzer([])

    assert analyzer.skill_counts() == {}
    assert analyzer.skill_stats() == []
    assert analyzer.jobs_with_skills() == 0
    assert analyzer.coverage_percentage() == 0.0