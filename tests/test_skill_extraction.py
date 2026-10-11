import pytest

from src.analytics.skill_extractor import (
    extract_skills,
    extract_skills_with_matches,
    normalize_text,
)


def test_normalize_text():
    text = "  Python   AND   PyTorch\nDeveloper  "

    assert normalize_text(text) == "python and pytorch developer"


def test_extract_basic_skills():
    text = """
    We are looking for a Machine Learning Engineer with
    Python, SQL, PyTorch, and AWS experience.
    """

    assert extract_skills(text) == [
        "aws",
        "machine learning",
        "python",
        "pytorch",
        "sql",
    ]


def test_case_insensitive_matching():
    text = "Experience with PYTHON, PyTorch, and AWS."

    assert extract_skills(text) == [
        "aws",
        "python",
        "pytorch",
    ]


def test_aliases_map_to_canonical_skill():
    text = "Experience with Python3, Torch, Sklearn, and K8s."

    assert extract_skills(text) == [
        "kubernetes",
        "python",
        "pytorch",
        "scikit-learn",
    ]


def test_duplicate_aliases_return_one_skill():
    text = "Python Python3 python 3 PYTHON"

    assert extract_skills(text) == ["python"]


def test_empty_text():
    assert extract_skills("") == []
    assert extract_skills(None) == []


def test_whitespace_only_text():
    assert extract_skills("   \n\t  ") == []


def test_multiskill_description():
    text = """
    The candidate will build RAG applications using LangGraph,
    FastAPI, PostgreSQL, Docker, Kubernetes, and AWS.
    """

    assert extract_skills(text) == [
        "aws",
        "docker",
        "fastapi",
        "kubernetes",
        "langgraph",
        "postgresql",
        "retrieval augmented generation",
    ]


def test_no_false_positive_for_python():
    text = "This role requires strong communication and leadership skills."

    assert "python" not in extract_skills(text)


def test_no_false_positive_for_r():
    text = "Strong experience with reporting and research."

    assert "r" not in extract_skills(text)


def test_matches_can_be_inspected():
    text = "Python3, PyTorch and sklearn experience required."

    result = extract_skills_with_matches(text)

    assert result["python"] == ["python3"]
    assert result["pytorch"] == ["pytorch"]
    assert result["scikit-learn"] == ["sklearn"]


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Java developer", ["java"]),
        ("C++ developer", ["c++"]),
        ("C# developer", ["c#"]),
        ("TensorFlow and Keras", ["keras", "tensorflow"]),
        ("Power BI and Tableau", ["power bi", "tableau"]),
    ],
)
def test_specific_skill_matching(text, expected):
    assert extract_skills(text) == expected


def test_ambiguous_short_aliases_do_not_create_false_positives():
    text = """
    The role involves artificial intelligence, computer vision,
    and machine learning. Candidates should demonstrate strong
    communication, teamwork, and business intelligence.
    """

    skills = extract_skills(text)

    assert "artificial intelligence" in skills
    assert "computer vision" in skills
    assert "machine learning" in skills

    # These should not be inferred from unrelated words.
    assert "r" not in skills


def test_r_requires_explicit_context():
    assert "r" not in extract_skills(
        "Strong research and reporting experience required."
    )

    assert "r" in extract_skills(
        "Experience with R programming is required."
    )


def test_ai_requires_explicit_context():
    text = """
    The candidate will work on artificial intelligence systems
    and AI-driven machine learning applications.
    """

    skills = extract_skills(text)

    assert "artificial intelligence" in skills
    assert "machine learning" in skills


def test_common_words_are_not_skills():
    text = """
    We are looking for a motivated professional with strong
    communication, collaboration, leadership, and problem-solving
    skills.
    """

    assert extract_skills(text) == []