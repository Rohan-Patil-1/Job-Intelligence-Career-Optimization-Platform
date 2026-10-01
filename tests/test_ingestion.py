from typing import Any

from src.ingestion.base import JobSource


class FakeJobSource(JobSource):
    def fetch_jobs(
        self,
        query: str,
        location: str,
    ) -> list[dict[str, Any]]:
        return [
            {
                "source": "fake",
                "source_job_id": "123",
                "title": "Data Scientist",
                "company": "Example Corp",
                "location": location,
                "job_url": "https://example.com/job/123",
            }
        ]


def test_job_source_contract():
    source = FakeJobSource()

    jobs = source.fetch_jobs(
        query="data scientist",
        location="Chicago, IL",
    )

    assert len(jobs) == 1
    assert jobs[0]["title"] == "Data Scientist"
    assert jobs[0]["source"] == "fake"