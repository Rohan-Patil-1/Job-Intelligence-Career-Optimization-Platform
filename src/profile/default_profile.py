from src.profile.candidate import CandidateProfile
from src.analytics.seniority import SeniorityLevel


DEFAULT_PROFILE = CandidateProfile(
    name="Rohan Patil",
    target_roles=[
        "data scientist",
        "machine learning engineer",
        "ai engineer",
        "applied scientist",
    ],
    skills={
        # Programming
        "python",
        "sql",
        "r",
        "java",

        # AI / ML
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "generative ai",
        "natural language processing",
        "computer vision",

        # ML frameworks / libraries
        "pytorch",
        "tensorflow",
        "keras",
        "scikit-learn",
        "pandas",
        "numpy",
        "opencv",

        # LLM / Agentic AI
        "large language models",
        "langgraph",
        "retrieval augmented generation",
        "vector databases",

        # Backend / APIs
        "fastapi",
        "rest api",

        # Engineering
        "git",
        "github",
        "ci/cd",

        # Analytics
        "statistics",
        "data analysis",
        "data visualization",
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