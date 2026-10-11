from src.analytics.skill_demand import SkillDemandAnalyzer
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


def test_skill_demand():
    jobs = [
        make_job(
            "Data Scientist",
            "Python SQL machine learning",
        ),
        make_job(
            "ML Engineer",
            "Python PyTorch AWS",
        ),
        make_job(
            "Analyst",
            "Strong communication skills.",
        ),
    ]

    analyzer = SkillDemandAnalyzer(jobs)

    results = {
        item.skill: item
        for item in analyzer.demand()
    }

    python = results["python"]

    assert python.job_count == 2
    assert python.total_jobs == 3
    assert python.jobs_with_skill_data == 2

    assert python.observed_percentage == 66.67
    assert python.coverage_adjusted_percentage == 100.0


def test_partial_skill_demand():
    jobs = [
        make_job("Job 1", "Python"),
        make_job("Job 2", "Python"),
        make_job("Job 3", "SQL"),
        make_job("Job 4", "Leadership"),
    ]

    analyzer = SkillDemandAnalyzer(jobs)

    results = {
        item.skill: item
        for item in analyzer.demand()
    }

    assert results["python"].observed_percentage == 50.0
    assert (
        results["python"].coverage_adjusted_percentage
        == 66.67
    )


def test_top_skills_limit():
    jobs = [
        make_job(
            "Job 1",
            "Python SQL AWS Docker",
        ),
        make_job(
            "Job 2",
            "Python SQL AWS",
        ),
    ]

    analyzer = SkillDemandAnalyzer(jobs)

    results = analyzer.top_skills(limit=2)

    assert len(results) == 2
    assert results[0].skill in {"python", "sql", "aws"}


def test_top_skills_zero_limit():
    jobs = [
        make_job("Job", "Python SQL"),
    ]

    analyzer = SkillDemandAnalyzer(jobs)

    assert analyzer.top_skills(limit=0) == []


def test_empty_dataset():
    analyzer = SkillDemandAnalyzer([])

    assert analyzer.demand() == []
    assert analyzer.top_skills() == []

def test_category_counts_once_per_job():
    jobs = [
        make_job(
            "Engineer",
            "Python SQL Java AWS Docker",
        ),
    ]

    analyzer = SkillDemandAnalyzer(jobs)

    counts = analyzer.category_counts()

    assert counts["programming"] == 1
    assert counts["cloud"] == 1
    assert counts["devops"] == 1


def test_category_demand():
    jobs = [
        make_job(
            "Data Scientist",
            "Python SQL machine learning AWS",
        ),
        make_job(
            "ML Engineer",
            "Python PyTorch Docker",
        ),
        make_job(
            "Analyst",
            "SQL Tableau",
        ),
    ]

    analyzer = SkillDemandAnalyzer(jobs)

    results = {
        item.category: item
        for item in analyzer.category_demand()
    }

    assert results["programming"].job_count == 3
    assert results["programming"].percentage == 100.0

    assert results["ai_ml"].job_count == 1
    assert results["ai_ml"].percentage == 33.33

    assert results["cloud"].job_count == 1
    assert results["cloud"].percentage == 33.33

    assert results["devops"].job_count == 1
    assert results["devops"].percentage == 33.33


def test_empty_category_demand():
    analyzer = SkillDemandAnalyzer([])

    assert analyzer.category_counts() == {}
    assert analyzer.category_demand() == []