from src.analytics.opportunity import OpportunityScore
from src.analytics.opportunity_diagnostics import (
    OpportunityDiagnostics,
)


def make_result(**overrides):
    values = {
        "job_id": 1,
        "title": "Data Scientist",
        "company": "Example",
        "skill_match": 100.0,
        "evidence_score": 75.0,
        "role_fit": 100.0,
        "role_label": "target",
        "matched_role": "data scientist",
        "seniority_level": "mid",
        "seniority_fit": 100.0,
        "seniority_label": "target",
        "seniority_multiplier": 1.0,
        "opportunity_score": 85.0,
        "domain_fit": 100.0,
        "domain_label": "preferred",
        "matched_domains": ("healthcare",),
        "domain_evidence_level": "high",
        "matched_skills": ("python", "sql"),
        "missing_skills": (),
    }

    values.update(overrides)

    return OpportunityScore(**values)


def test_strong_opportunity():
    result = make_result()

    diagnostic = OpportunityDiagnostics.analyze(result)

    assert diagnostic.recommendation == "strong_review"
    assert diagnostic.confidence == "high"
    assert len(diagnostic.strengths) > 0


def test_missing_skill_evidence():
    result = make_result(
        evidence_score=0.0,
        skill_match=0.0,
        opportunity_score=60.0,
    )

    diagnostic = OpportunityDiagnostics.analyze(result)

    assert diagnostic.confidence == "low"
    assert diagnostic.recommendation == "needs_more_evidence"
    assert len(diagnostic.evidence_gaps) > 0


def test_vp_job_is_low_priority():
    result = make_result(
        seniority_level="vp",
        seniority_label="poor_fit",
        seniority_fit=0.0,
        seniority_multiplier=0.15,
        opportunity_score=12.0,
    )

    diagnostic = OpportunityDiagnostics.analyze(result)

    assert diagnostic.recommendation == "low_priority"


def test_unknown_domain_is_evidence_gap():
    result = make_result(
        domain_fit=0.0,
        domain_label="unknown",
        matched_domains=(),
        domain_evidence_level="insufficient",
    )

    diagnostic = OpportunityDiagnostics.analyze(result)

    assert any(
        "domain" in gap.lower()
        for gap in diagnostic.evidence_gaps
    )

def test_mixed_role_requires_review():
    result = make_result(
        title="Junior Data Scientist/Data Analyst/Java Spring boot developer",
        opportunity_score=73.96,
        evidence_score=63.21,
    )

    diagnostic = OpportunityDiagnostics.analyze(result)

    assert diagnostic.recommendation == "needs_more_evidence"
    assert any(
        "multiple professional roles" in concern
        for concern in diagnostic.concerns
    )