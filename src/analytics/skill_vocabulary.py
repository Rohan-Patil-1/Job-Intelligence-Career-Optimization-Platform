"""
Canonical skill vocabulary and aliases used by the skill extractor.
"""

SKILL_VOCABULARY = {
    # Programming languages
    "python": ["python", "python3", "python 3"],
    "sql": ["sql"],
    "r": ["r programming", "r language"],
    "java": ["java"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "c sharp"],

    # Machine Learning / AI
    "machine learning": ["machine learning"],
    "deep learning": ["deep learning", "dl"],
    "artificial intelligence": ["artificial intelligence"],
    "generative ai": [
        "generative ai",
        "genai",
        "generative artificial intelligence",
    ],
    "natural language processing": [
        "natural language processing",
        "nlp",
    ],
    "computer vision": ["computer vision"],
    "reinforcement learning": ["reinforcement learning"],

    # ML frameworks / libraries
    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow"],
    "keras": ["keras"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "opencv": ["opencv", "open cv"],

    # LLM / Agentic AI
    "large language models": [
        "large language model",
        "large language models",
        "llm",
        "llms",
    ],
    "langchain": ["langchain"],
    "langgraph": ["langgraph"],
    "retrieval augmented generation": [
        "retrieval augmented generation",
        "retrieval-augmented generation",
        "rag",
    ],
    "vector databases": [
        "vector database",
        "vector databases",
        "vector db",
        "vector dbs",
    ],

    # Cloud
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],

    # Databases
    "postgresql": ["postgresql", "postgres"],
    "mysql": ["mysql"],
    "sqlite": ["sqlite"],
    "mongodb": ["mongodb", "mongo db", "mongo"],

    # Data engineering
    "etl": [
        "etl",
        "extract transform load",
        "extract-transform-load",
    ],
    "data pipelines": [
        "data pipeline",
        "data pipelines",
    ],
    "apache spark": ["apache spark", "spark"],
    "airflow": ["airflow", "apache airflow"],

    # APIs / Backend
    "fastapi": ["fastapi", "fast api"],
    "rest api": [
        "rest api",
        "restful api",
        "restful apis",
    ],
    "graphql": ["graphql"],

    # DevOps / Engineering
    "git": ["git"],
    "github": ["github"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "ci/cd": [
        "ci/cd",
        "cicd",
        "continuous integration",
        "continuous deployment",
    ],

    # Analytics
    "statistics": [
        "statistics",
        "statistical analysis",
    ],
    "data analysis": [
        "data analysis",
        "data analytics",
    ],
    "data visualization": [
        "data visualization",
        "data visualisation",
    ],
    "tableau": ["tableau"],
    "power bi": ["power bi", "powerbi"],
}

SKILL_ALIASES = {
    alias: skill
    for skill, aliases in SKILL_VOCABULARY.items()
    for alias in aliases
}

SKILL_CATEGORIES = {
    # Programming
    "python": "programming",
    "sql": "programming",
    "r": "programming",
    "java": "programming",
    "javascript": "programming",
    "typescript": "programming",
    "c++": "programming",
    "c#": "programming",

    # AI / ML
    "machine learning": "ai_ml",
    "deep learning": "ai_ml",
    "artificial intelligence": "ai_ml",
    "generative ai": "ai_ml",
    "natural language processing": "ai_ml",
    "computer vision": "ai_ml",
    "reinforcement learning": "ai_ml",

    # ML frameworks
    "pytorch": "ml_framework",
    "tensorflow": "ml_framework",
    "keras": "ml_framework",
    "scikit-learn": "ml_framework",
    "pandas": "data_library",
    "numpy": "data_library",
    "opencv": "ml_framework",

    # LLM / Agentic
    "large language models": "llm_agentic",
    "langchain": "llm_agentic",
    "langgraph": "llm_agentic",
    "retrieval augmented generation": "llm_agentic",
    "vector databases": "llm_agentic",

    # Cloud
    "aws": "cloud",
    "azure": "cloud",
    "gcp": "cloud",

    # Databases
    "postgresql": "database",
    "mysql": "database",
    "sqlite": "database",
    "mongodb": "database",

    # Data engineering
    "etl": "data_engineering",
    "data pipelines": "data_engineering",
    "apache spark": "data_engineering",
    "airflow": "data_engineering",

    # Backend
    "fastapi": "backend_api",
    "rest api": "backend_api",
    "graphql": "backend_api",

    # DevOps
    "git": "devops",
    "github": "devops",
    "docker": "devops",
    "kubernetes": "devops",
    "ci/cd": "devops",

    # Analytics
    "statistics": "analytics",
    "data analysis": "analytics",
    "data visualization": "analytics",
    "tableau": "analytics",
    "power bi": "analytics",
}