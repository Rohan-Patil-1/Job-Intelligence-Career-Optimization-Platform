from src.profile.candidate import CandidateProfile


def test_candidate_profile_normalizes_skills():
    profile = CandidateProfile(
        name="Test Candidate",
        skills={
            " Python ",
            "SQL",
            "PyTorch",
        },
    )

    assert profile.normalized_skills() == {
        "python",
        "sql",
        "pytorch",
    }


def test_empty_candidate_profile():
    profile = CandidateProfile(
        name="Test Candidate",
    )

    assert profile.normalized_skills() == set()
    assert profile.target_roles == []