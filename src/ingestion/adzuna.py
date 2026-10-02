from typing import Any

import requests

from src.ingestion.base import JobSource


class AdzunaSource(JobSource):
    """Adzuna job source adapter."""

    BASE_URL = "https://api.adzuna.com/v1/api/jobs"

    def __init__(
        self,
        app_id: str,
        app_key: str,
        country: str = "us",
    ) -> None:
        self.app_id = app_id
        self.app_key = app_key
        self.country = country

    def fetch_jobs(
        self,
        query: str,
        location: str,
        page: int = 1,
        results_per_page: int = 20,
    ) -> list[dict[str, Any]]:
        url = (
            f"{self.BASE_URL}/{self.country}/search/{page}"
        )

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": query,
            "where": location,
            "results_per_page": results_per_page,
            "content-type": "application/json",
        }

        response = requests.get(
            url,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        return [
            self._normalize_response(job)
            for job in data.get("results", [])
        ]

    @staticmethod
    def _normalize_response(job: dict[str, Any]) -> dict[str, Any]:
        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")

        return {
            "source": "adzuna",
            "source_job_id": str(job["id"]),
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "remote_type": None,
            "employment_type": None,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_currency": "USD",
            "description": job.get("description"),
            "requirements": None,
            "responsibilities": None,
            "skills": None,
            "job_url": job.get("redirect_url"),
            "posted_at": job.get("created"),
        }