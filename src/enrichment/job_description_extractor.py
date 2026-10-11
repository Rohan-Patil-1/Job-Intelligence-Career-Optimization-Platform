import json
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlparse

import requests


@dataclass(frozen=True)
class ExtractedJob:
    url: str
    title: str | None
    company: str | None
    description: str | None
    identifier: str | None
    extraction_method: str


class _JSONLDScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside_script = False
        self.parts = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if (
            tag.lower() == "script"
            and attributes.get("type", "").lower()
            == "application/ld+json"
        ):
            self.inside_script = True
            self.parts = []

    def handle_data(self, data):
        if self.inside_script:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self.inside_script:
            self.scripts.append("".join(self.parts))
            self.inside_script = False


class JobDescriptionExtractor:

    TIMEOUT = 15

    @staticmethod
    def _job_postings(data):
        if isinstance(data, list):
            for item in data:
                yield from JobDescriptionExtractor._job_postings(item)

        elif isinstance(data, dict):
            types = data.get("@type", [])
            if isinstance(types, str):
                types = [types]

            if "JobPosting" in types:
                yield data

            for key in ("@graph",):
                if key in data:
                    yield from JobDescriptionExtractor._job_postings(
                        data[key]
                    )

    @classmethod
    def extract_from_html(cls, html: str, url: str):
        parser = _JSONLDScriptParser()
        parser.feed(html)

        for script in parser.scripts:
            try:
                data = json.loads(script)
            except json.JSONDecodeError:
                continue

            for posting in cls._job_postings(data):
                organization = posting.get("hiringOrganization")
                company = (
                    organization.get("name")
                    if isinstance(organization, dict)
                    else None
                )

                identifier = posting.get("identifier")
                if isinstance(identifier, dict):
                    identifier = identifier.get("value")

                description = posting.get("description")
                if isinstance(description, str):
                    description = unescape(description)

                return ExtractedJob(
                    url=url,
                    title=posting.get("title"),
                    company=company,
                    description=description,
                    identifier=(
                        str(identifier)
                        if identifier is not None
                        else None
                    ),
                    extraction_method="json_ld",
                )

        return None

    @classmethod
    def extract(cls, url: str):
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return None

        if not parsed.netloc:
            return None

        try:
            response = requests.get(
                url,
                timeout=cls.TIMEOUT,
                headers={
                    "User-Agent": "JobIntelligenceResearch/0.1"
                },
            )
            response.raise_for_status()

        except requests.RequestException:
            return None

        return cls.extract_from_html(
            response.text,
            response.url,
        )