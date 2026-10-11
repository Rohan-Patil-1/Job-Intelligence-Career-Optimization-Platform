from src.enrichment.job_description_extractor import (
    JobDescriptionExtractor,
)


def test_extract_jobposting_jsonld():
    html = """
    <html>
      <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@type": "JobPosting",
        "title": "Data Scientist",
        "hiringOrganization": {
          "@type": "Organization",
          "name": "Example Company"
        },
        "identifier": {
          "@type": "PropertyValue",
          "value": "REQ-123"
        },
        "description": "Build machine learning models."
      }
      </script>
    </html>
    """

    result = JobDescriptionExtractor.extract_from_html(
        html,
        "https://careers.example.com/jobs/123",
    )

    assert result is not None
    assert result.title == "Data Scientist"
    assert result.company == "Example Company"
    assert result.identifier == "REQ-123"
    assert "machine learning" in result.description


def test_missing_jobposting():
    html = "<html><body>No structured job data</body></html>"

    result = JobDescriptionExtractor.extract_from_html(
        html,
        "https://example.com",
    )

    assert result is None


def test_invalid_jsonld():
    html = """
    <script type="application/ld+json">
    { invalid json }
    </script>
    """

    result = JobDescriptionExtractor.extract_from_html(
        html,
        "https://example.com",
    )

    assert result is None


def test_jsonld_graph():
    html = """
    <script type="application/ld+json">
    {
      "@graph": [
        {
          "@type": "Organization",
          "name": "Example Company"
        },
        {
          "@type": "JobPosting",
          "title": "ML Engineer",
          "hiringOrganization": {
            "name": "Example Company"
          },
          "description": "Develop ML systems."
        }
      ]
    }
    </script>
    """

    result = JobDescriptionExtractor.extract_from_html(
        html,
        "https://example.com/jobs/ml",
    )

    assert result is not None
    assert result.title == "ML Engineer"