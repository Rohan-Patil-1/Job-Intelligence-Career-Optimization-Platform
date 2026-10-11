from dataclasses import dataclass
from urllib.parse import urlencode


@dataclass(frozen=True)
class SourceSearch:
    job_id: int | None
    company: str
    title: str
    query: str
    search_url: str


class SourceDiscovery:

    @staticmethod
    def build_query(job) -> str:
        company = (job.company or "").strip()
        title = (job.title or "").strip()
        location = (job.location or "").strip()

        parts = [
            f'"{company}"' if company else "",
            f'"{title}"' if title else "",
            location,
            "careers jobs",
        ]

        return " ".join(part for part in parts if part)

    @classmethod
    def create_search(cls, job) -> SourceSearch:
        query = cls.build_query(job)

        search_url = (
            "https://www.google.com/search?"
            + urlencode({"q": query})
        )

        return SourceSearch(
            job_id=job.id,
            company=job.company or "",
            title=job.title or "",
            query=query,
            search_url=search_url,
        )