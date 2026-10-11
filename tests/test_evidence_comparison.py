
from src.enrichment.evidence_comparison import EvidenceComparator


def test_third_party_evidence_not_eligible():
    result = EvidenceComparator.compare(
        job_id=18,
        baseline_description="Experience with SQL.",
        enriched_description=(
            "Experience with SQL, Python, AWS, "
            "machine learning and agentic workflows."
        ),
        validation_status="review_required",
        source_type="third_party",
    )

    assert result.eligible_for_production_scoring is False
    assert "Python" in result.additional_skills
    assert "AWS" in result.additional_skills
    assert "SQL" not in result.additional_skills


def test_verified_employer_evidence_eligible():
    result = EvidenceComparator.compare(
        job_id=18,
        baseline_description="Experience with SQL.",
        enriched_description="Experience with SQL and Python.",
        validation_status="verified",
        source_type="employer",
    )

    assert result.eligible_for_production_scoring is True


def test_verified_third_party_not_eligible():
    result = EvidenceComparator.compare(
        job_id=18,
        baseline_description="SQL",
        enriched_description="SQL and Python",
        validation_status="verified",
        source_type="third_party",
    )

    assert result.eligible_for_production_scoring is False


def test_comparison_does_not_invent_skills():
    result = EvidenceComparator.compare(
        job_id=18,
        baseline_description="Experience with Python.",
        enriched_description="Experience with Python.",
        validation_status="review_required",
        source_type="third_party",
    )

    assert result.additional_skills == ()


def test_empty_baseline():
    result = EvidenceComparator.compare(
        job_id=18,
        baseline_description="",
        enriched_description="Experience with R and SQL.",
        validation_status="review_required",
        source_type="third_party",
    )

    assert "SQL" in result.additional_skills
    assert "R" in result.additional_skills
    assert result.baseline_description_length == 0
