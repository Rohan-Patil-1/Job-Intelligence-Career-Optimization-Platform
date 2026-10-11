
from src.enrichment.structured_extractor import StructuredJobExtractor


def test_merges_education_experience_fragments():
    description = """
    <h2>Requirements</h2>
    <p>Education:</p>
    <p>Master’s degree and</p>
    <p>2+ years</p>
    <p>of additional work experience</p>
    """

    result = StructuredJobExtractor.extract(description)

    assert (
        "Master’s degree and 2+ years of additional work experience"
        in result.requirements
    )
    assert "Education:" not in result.requirements


def test_removes_job_posting_metadata():
    description = """
    <h2>Requirements</h2>
    <p>Proficient in SQL and Python.</p>
    <p>#LI-DA1</p>
    """

    result = StructuredJobExtractor.extract(description)

    assert "#LI-DA1" not in result.requirements
    assert "Proficient in SQL and Python." in result.requirements


def test_excludes_subsection_headings():
    description = """
    <h2>Requirements</h2>
    <p>Technical and Statistical Proficiency</p>
    <p>Proficient in R and SQL.</p>
    <p>Soft Skills:</p>
    <p>Excellent written communication.</p>
    """

    result = StructuredJobExtractor.extract(description)

    assert "Technical and Statistical Proficiency" not in result.requirements
    assert "Soft Skills:" not in result.requirements
    assert "Proficient in R and SQL." in result.requirements
    assert "Excellent written communication." in result.requirements


def test_preserves_responsibilities():
    description = """
    <h2>Responsibilities</h2>
    <p>AI & LLM Innovation:</p>
    <p>Incorporate LLMs and agentic workflows.</p>
    """

    result = StructuredJobExtractor.extract(description)

    assert result.responsibilities == (
        "Incorporate LLMs and agentic workflows.",
    )
    assert "LLMs" in result.skills
    assert "Agentic AI" in result.skills


def test_salary_section_does_not_leak():
    description = """
    <h2>Requirements</h2>
    <p>Experience with Python.</p>
    <h2>Salary Range</h2>
    <p>$120,000 - $150,000</p>
    <p>Benefits include health insurance.</p>
    """

    result = StructuredJobExtractor.extract(description)

    assert result.requirements == (
        "Experience with Python.",
    )
