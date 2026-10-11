
from unittest.mock import patch

import pytest

from src.enrichment.score_comparison import (
    OpportunityScoreComparator,
)
from src.database.models import Job
from src.profile.candidate import CandidateProfile


def make_job():
    job = Job()
    job.id = 18
    job.title = "Data Scientist II"
    job.company = "Tempus AI"
    job.location = "Chicago"
    job.description = "Experience with SQL."
    job.source = "adzuna"
    job.source_job_id = "test-18"
    job.job_url = "https://example.com/jobs/test-18"
    return job


def make_candidate():
    return CandidateProfile(
        name="Test Candidate",
        target_roles=["Data Scientist"],
        skills={"SQL", "Python", "Machine Learning"},
        preferred_domains={"healthcare"},
    )


def test_original_job_not_modified():
    job = make_job()
    original_description = job.description

    comparator = OpportunityScoreComparator(
        make_candidate()
    )

    comparator.compare(
        job=job,
        enriched_description=(
            "Experience with SQL, Python and machine learning."
        ),
        validation_status="review_required",
        source_type="third_party",
    )

    assert job.description == original_description


def test_third_party_comparison_is_provisional():
    result = OpportunityScoreComparator(
        make_candidate()
    ).compare(
        job=make_job(),
        enriched_description="Python and machine learning.",
        validation_status="review_required",
        source_type="third_party",
    )

    assert result.production_eligible is False


def test_verified_employer_is_eligible():
    result = OpportunityScoreComparator(
        make_candidate()
    ).compare(
        job=make_job(),
        enriched_description="Python and machine learning.",
        validation_status="verified",
        source_type="employer",
    )

    assert result.production_eligible is True


def test_empty_enrichment_rejected():
    comparator = OpportunityScoreComparator(
        make_candidate()
    )

    with pytest.raises(ValueError):
        comparator.compare(
            job=make_job(),
            enriched_description="  ",
            validation_status="review_required",
            source_type="third_party",
        )


def test_score_delta_matches_scores():
    result = OpportunityScoreComparator(
        make_candidate()
    ).compare(
        job=make_job(),
        enriched_description=(
            "Experience with SQL, Python and machine learning."
        ),
        validation_status="review_required",
        source_type="third_party",
    )

    expected = round(
        result.provisional.opportunity_score
        - result.baseline.opportunity_score,
        2,
    )

    assert result.score_delta == expected
