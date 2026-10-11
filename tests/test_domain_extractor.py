from src.analytics.domain_extractor import extract_domains


def test_healthcare_detection():
    result = extract_domains(
        "Clinical research using real world evidence."
    )

    assert "healthcare" in result


def test_medical_imaging_detection():
    result = extract_domains(
        "Develop radiology models using DICOM."
    )

    assert "medical_imaging" in result


def test_financial_services_detection():
    result = extract_domains(
        "Credit risk modeling for banking."
    )

    assert "financial_services" in result


def test_multiple_domains():
    result = extract_domains(
        "Machine learning research in clinical radiology."
    )

    assert "healthcare" in result
    assert "medical_imaging" in result


def test_no_domain():
    assert extract_domains(
        "Develop software applications."
    ) == {}