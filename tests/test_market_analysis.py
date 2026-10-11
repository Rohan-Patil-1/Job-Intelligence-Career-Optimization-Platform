from src.analytics.market import MarketAnalyzer
from src.database.models import Job


def test_market_analyzer_returns_summary(db_session):
    db_session.add_all(
        [
            Job(
                source="test",
                source_job_id="1",
                title="Data Scientist",
                company="Company A",
                job_url="https://example.com/1",
            ),
            Job(
                source="test",
                source_job_id="2",
                title="ML Engineer",
                company="Company A",
                job_url="https://example.com/2",
            ),
            Job(
                source="adzuna",
                source_job_id="3",
                title="Data Scientist",
                company="Company B",
                job_url="https://example.com/3",
            ),
        ]
    )

    db_session.commit()

    analyzer = MarketAnalyzer(db_session)

    result = analyzer.analyze()

    assert result["total_jobs"] == 3
    assert result["unique_companies"] == 2
    assert result["unique_sources"] == 2