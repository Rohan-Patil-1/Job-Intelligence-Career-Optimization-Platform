from src.analytics.opportunity import OpportunityScorer
from src.analytics.seniority import SeniorityLevel
from src.database.models import Job
from src.profile.candidate import CandidateProfile


def make_job(
    title: str,
    description: str,
    company: str = "Test Company",
) -> Job:
    return Job(
        source="test",
        title=title,
        company=company,
        description=description,
        job_url="https://example.com/job",
    )


def make_candidate() -> CandidateProfile:
    return CandidateProfile(
        name="Test Candidate",

        target_roles=[
            "data scientist",
            "machine learning engineer",
            "ai engineer",
            "applied scientist",
        ],

        skills={
            "python",
            "sql",
            "machine learning",
            "statistics",
        },

        target_seniority={
            SeniorityLevel.ENTRY,
            SeniorityLevel.MID,
        },

        preferred_domains={
            "healthcare",
            "medical_imaging",
            "ai_research",
        },
    )


def test_target_job_scores_higher_than_vp():
    candidate = make_candidate()

    scorer = OpportunityScorer(candidate)

    target_job = make_job(
        "Data Scientist",
        "Python SQL machine learning statistics",
    )

    vp_job = make_job(
        "VP Data Scientist",
        "Python SQL machine learning statistics",
    )

    target_result = scorer.score_job(target_job)
    vp_result = scorer.score_job(vp_job)

    assert (
        target_result.opportunity_score
        > vp_result.opportunity_score
    )

    assert target_result.seniority_fit == 100.0
    assert vp_result.seniority_fit == 0.0


def test_skill_match_is_preserved():
    scorer = OpportunityScorer(
        make_candidate()
    )

    job = make_job(
        "Data Scientist",
        "Python SQL AWS Docker",
    )

    result = scorer.score_job(job)

    assert result.skill_match == 50.0

    assert result.matched_skills == (
        "python",
        "sql",
    )

    assert result.missing_skills == (
        "aws",
        "docker",
    )


def test_senior_job_is_stretch():
    scorer = OpportunityScorer(
        make_candidate()
    )

    job = make_job(
        "Senior Data Scientist",
        "Python SQL machine learning",
    )

    result = scorer.score_job(job)

    assert result.seniority_level == "senior"
    assert result.seniority_fit == 70.0
    assert result.seniority_label == "stretch"


def test_rank_jobs_prefers_target_seniority():
    scorer = OpportunityScorer(
        make_candidate()
    )

    jobs = [
        make_job(
            "VP Data Scientist",
            "Python SQL machine learning statistics",
        ),
        make_job(
            "Data Scientist",
            "Python SQL machine learning statistics",
        ),
        make_job(
            "Senior Data Scientist",
            "Python SQL machine learning statistics",
        ),
    ]

    results = scorer.rank_jobs(jobs)

    assert results[0].title == "Data Scientist"
    assert results[1].title == "Senior Data Scientist"
    assert results[2].title == "VP Data Scientist"


def test_zero_skill_evidence_does_not_mean_zero_opportunity():
    scorer = OpportunityScorer(
        make_candidate()
    )

    job = make_job(
        "Data Scientist",
        "Work with business stakeholders.",
    )

    result = scorer.score_job(job)

    assert result.skill_match == 0.0
    assert result.evidence_score == 0.0

    # Seniority evidence still exists.
    assert result.seniority_fit == 100.0

    assert result.role_fit == 100.0
    assert result.role_label == "target"
    assert result.seniority_fit == 100.0
    assert result.seniority_multiplier == 1.0
    assert result.opportunity_score == 55.0

def test_vp_receives_strong_seniority_penalty():
    scorer = OpportunityScorer(
        make_candidate()
    )

    job = make_job(
        "VP Data Scientist",
        "Python SQL machine learning statistics",
    )

    result = scorer.score_job(job)

    assert result.seniority_label == "poor_fit"
    assert result.seniority_multiplier == 0.15
    assert result.opportunity_score < 20.0


def test_target_seniority_has_no_penalty():
    scorer = OpportunityScorer(
        make_candidate()
    )

    job = make_job(
        "Data Scientist",
        "Python SQL machine learning statistics",
    )

    result = scorer.score_job(job)

    assert result.seniority_label == "target"
    assert result.seniority_multiplier == 1.0


def test_senior_role_gets_moderate_penalty():
    scorer = OpportunityScorer(
        make_candidate()
    )

    job = make_job(
        "Senior Data Scientist",
        "Python SQL machine learning statistics",
    )

    result = scorer.score_job(job)

    assert result.seniority_label == "stretch"
    assert result.seniority_multiplier == 0.90


def test_candidate_domain_preferences_are_respected():
    candidate = make_candidate()

    candidate.preferred_domains = {"financial_services"}

    scorer = OpportunityScorer(candidate)

    financial_job = make_job(
        "Data Scientist",
        "Banking and credit risk analytics.",
    )

    healthcare_job = make_job(
        "Data Scientist",
        "Clinical healthcare research.",
    )

    financial_result = scorer.score_job(financial_job)
    healthcare_result = scorer.score_job(healthcare_job)

    assert financial_result.domain_label == "preferred"
    assert "financial_services" in financial_result.matched_domains

    assert healthcare_result.domain_label == "other_domain"

    assert (
        financial_result.opportunity_score
        > healthcare_result.opportunity_score
    )


def test_empty_domain_preferences_do_not_add_bonus():
    candidate = make_candidate()

    candidate.preferred_domains = set()

    scorer = OpportunityScorer(candidate)

    job = make_job(
        "Data Scientist",
        "Clinical healthcare research.",
    )

    result = scorer.score_job(job)

    assert result.domain_label == "other_domain"
    assert result.matched_domains == ()
    assert result.opportunity_score == 55.0