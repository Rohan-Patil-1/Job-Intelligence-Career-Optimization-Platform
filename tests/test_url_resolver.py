from unittest.mock import Mock, patch

from src.enrichment.url_resolver import JobURLResolver


def test_missing_url():
    result = JobURLResolver.resolve(None)

    assert result.success is False
    assert result.reason == "missing_url"


def test_invalid_url():
    result = JobURLResolver.resolve("not-a-url")

    assert result.success is False
    assert result.reason == "invalid_url"


@patch("src.enrichment.url_resolver.requests.get")
def test_external_redirect(mock_get):
    response = Mock()
    response.status_code = 200
    response.url = "https://careers.example.com/jobs/123"

    mock_get.return_value = response

    result = JobURLResolver.resolve(
        "https://www.adzuna.com/land/ad/123"
    )

    assert result.success is True
    assert result.reason == "external_page_reached"
    assert result.final_url == response.url


@patch("src.enrichment.url_resolver.requests.get")
def test_adzuna_destination(mock_get):
    response = Mock()
    response.status_code = 200
    response.url = "https://www.adzuna.com/jobs/details/123"

    mock_get.return_value = response

    result = JobURLResolver.resolve(
        "https://www.adzuna.com/land/ad/123"
    )

    assert result.success is True
    assert result.reason == "still_on_adzuna"


@patch("src.enrichment.url_resolver.requests.get")
def test_request_failure(mock_get):
    import requests

    mock_get.side_effect = requests.Timeout()

    result = JobURLResolver.resolve(
        "https://www.adzuna.com/land/ad/123"
    )

    assert result.success is False
    assert result.reason == "request_failed"