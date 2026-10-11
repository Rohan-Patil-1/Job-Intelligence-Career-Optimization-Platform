from src.enrichment.structured_extractor import (
    StructuredJobExtractor,
)


def test_extract_structured_sections():
    description = """
    <h2>Responsibilities</h2>
    <ul>
        <li>Build machine learning models.</li>
        <li>Develop production Python pipelines.</li>
    </ul>

    <h2>Qualifications</h2>
    <ul>
        <li>Experience with SQL and PyTorch.</li>
        <li>Knowledge of statistics.</li>
    </ul>

    <h2>Benefits</h2>
    <p>Health insurance.</p>
    """

    result = StructuredJobExtractor.extract(description)

    assert len(result.responsibilities) == 2
    assert len(result.requirements) == 2
    assert "Python" in result.skills
    assert "SQL" in result.skills
    assert "PyTorch" in result.skills


def test_empty_description():
    result = StructuredJobExtractor.extract("")

    assert result.requirements == ()
    assert result.responsibilities == ()
    assert result.skills == ()


def test_skills_without_sections():
    description = """
    We use Python, SQL, Docker, and AWS
    to develop machine learning systems.
    """

    result = StructuredJobExtractor.extract(description)

    assert "Python" in result.skills
    assert "SQL" in result.skills
    assert "Docker" in result.skills
    assert "AWS" in result.skills

    assert result.requirements == ()
    assert result.responsibilities == ()


def test_benefits_not_in_requirements():
    description = """
    Requirements:
    Experience with Python.
    Benefits:
    Health insurance.
    """

    result = StructuredJobExtractor.extract(description)

    assert "Experience with Python." in result.requirements
    assert "Health insurance." not in result.requirements

def test_salary_disclosure_not_in_requirements():
    description = """
    <h2>Qualifications</h2>
    <ul>
        <li>Experience with R and SQL.</li>
        <li>Knowledge of survival analysis.</li>
    </ul>
    <p>CHI: $100,000-$140,000</p>
    <p>The expected salary range may vary.</p>
    <p>We are an equal opportunity employer.</p>
    """

    result = StructuredJobExtractor.extract(description)

    assert "Experience with R and SQL." in result.requirements

    assert not any(
        "salary" in item.lower()
        or "$100,000" in item
        or "equal opportunity" in item.lower()
        for item in result.requirements
    )


def test_healthcare_research_skills():
    description = """
    Experience with survival analysis, causal inference,
    epidemiology, biostatistics, real-world evidence,
    EHR data, oncology, and clinical trials.
    """

    result = StructuredJobExtractor.extract(description)

    assert "Survival Analysis" in result.skills
    assert "Causal Inference" in result.skills
    assert "Epidemiology" in result.skills
    assert "Biostatistics" in result.skills
    assert "Real-World Evidence" in result.skills
    assert "EHR" in result.skills
    assert "Oncology" in result.skills
    assert "Clinical Trials" in result.skills