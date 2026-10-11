import pytest

from src.analytics.seniority import (
    SeniorityLevel,
    detect_seniority,
)


@pytest.mark.parametrize(
    "title, expected",
    [
        (
            "Junior Data Scientist",
            SeniorityLevel.ENTRY,
        ),
        (
            "Data Scientist",
            SeniorityLevel.MID,
        ),
        (
            "Senior Data Scientist",
            SeniorityLevel.SENIOR,
        ),
        (
            "Sr. Data Scientist",
            SeniorityLevel.SENIOR,
        ),
        (
            "Lead Data Scientist",
            SeniorityLevel.LEAD,
        ),
        (
            "Principal Data Scientist",
            SeniorityLevel.LEAD,
        ),
        (
            "Data Science Manager",
            SeniorityLevel.MANAGER,
        ),
        (
            "Senior Manager, Data Science",
            SeniorityLevel.MANAGER,
        ),
        (
            "Director of Data Science",
            SeniorityLevel.DIRECTOR,
        ),
        (
            "VP Data Scientist",
            SeniorityLevel.VP,
        ),
        (
            "Vice President - Data Scientist",
            SeniorityLevel.VP,
        ),
    ],
)
def test_detect_seniority(
    title,
    expected,
):
    result = detect_seniority(title)

    assert result.level == expected


def test_empty_title_returns_unknown():
    result = detect_seniority("")

    assert result.level == SeniorityLevel.UNKNOWN
    assert result.label == "unknown"


def test_highest_seniority_wins():
    result = detect_seniority(
        "Vice President - Data Scientist Lead"
    )

    assert result.level == SeniorityLevel.VP