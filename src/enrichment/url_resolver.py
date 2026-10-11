from dataclasses import dataclass
from urllib.parse import urlparse

import requests


@dataclass(frozen=True)
class ResolvedJobURL:
    original_url: str
    final_url: str | None
    status_code: int | None
    success: bool
    reason: str


class JobURLResolver:

    TIMEOUT = 15

    @classmethod
    def resolve(cls, url: str | None) -> ResolvedJobURL:

        original_url = url or ""

        if not url:
            return ResolvedJobURL(
                original_url=original_url,
                final_url=None,
                status_code=None,
                success=False,
                reason="missing_url",
            )

        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return ResolvedJobURL(
                original_url=original_url,
                final_url=None,
                status_code=None,
                success=False,
                reason="invalid_url",
            )

        try:
            response = requests.get(
                url,
                allow_redirects=True,
                timeout=cls.TIMEOUT,
                headers={
                    "User-Agent": "JobIntelligenceResearch/0.1"
                },
            )

            final_url = response.url
            final_domain = urlparse(final_url).netloc.lower()

            if response.status_code != 200:
                return ResolvedJobURL(
                    original_url=original_url,
                    final_url=final_url,
                    status_code=response.status_code,
                    success=False,
                    reason="http_error",
                )

            if "adzuna.com" in final_domain:
                reason = "still_on_adzuna"
            else:
                reason = "external_page_reached"

            return ResolvedJobURL(
                original_url=original_url,
                final_url=final_url,
                status_code=response.status_code,
                success=True,
                reason=reason,
            )

        except requests.RequestException:
            return ResolvedJobURL(
                original_url=original_url,
                final_url=None,
                status_code=None,
                success=False,
                reason="request_failed",
            )