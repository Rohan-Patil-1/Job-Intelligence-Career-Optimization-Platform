from src.analytics.title_diagnostics import TitleDiagnostics


def test_mixed_data_scientist_java_developer():
    result = TitleDiagnostics.analyze(
        "Junior Data Scientist/Data Analyst/Java Spring boot developer"
    )

    assert result.is_mixed_role
    assert "data_scientist" in result.detected_roles
    assert "data_analyst" in result.detected_roles
    assert "java_developer" in result.detected_roles


def test_single_data_scientist():
    result = TitleDiagnostics.analyze(
        "Data Scientist, Global Services Analytics"
    )

    assert not result.is_mixed_role


def test_single_machine_learning_engineer():
    result = TitleDiagnostics.analyze(
        "Machine Learning Engineer"
    )

    assert not result.is_mixed_role