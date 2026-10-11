
import re
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser


@dataclass(frozen=True)
class StructuredJobDetails:
    requirements: tuple[str, ...]
    responsibilities: tuple[str, ...]
    skills: tuple[str, ...]


class _TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.parts.append(text)

    def handle_starttag(self, tag, attrs):
        if tag.lower() in (
            "p", "br", "li", "div",
            "h1", "h2", "h3", "h4",
        ):
            self.parts.append("\n")


class StructuredJobExtractor:

    REQUIREMENT_HEADINGS = (
        "requirements",
        "qualifications",
        "minimum qualifications",
        "basic qualifications",
        "preferred qualifications",
        "what you bring",
        "what we're looking for",
        "what we are looking for",
    )

    RESPONSIBILITY_HEADINGS = (
        "responsibilities",
        "key responsibilities",
        "what you'll do",
        "what you will do",
        "the role",
        "your impact",
    )

    STOP_HEADINGS = (
        "benefits",
        "compensation",
        "salary",
        "salary range",
        "pay range",
        "about us",
        "about the company",
        "equal opportunity employer",
        "equal employment opportunity",
        "additional information",
        "workplace policy",
        "legal notice",
        "disclaimer",
        "privacy notice",
    )

    # Subsection labels are not standalone requirements.
    SUBSECTION_HEADINGS = (
        "education",
        "technical and statistical proficiency",
        "communication & client focus",
        "communication and client focus",
        "soft skills",
        "preferred skillsets",
        "preferred skills",
        "pharma collaboration & strategy",
        "real world data expertise",
        "methodology & platform contribution",
        "ai & llm innovation",
        "scientific interpretation & communication",
        "cross-functional collaboration",
    )

    SKILL_PATTERNS = {
        "Python": r"\bpython\b",
        "SQL": r"\bsql\b",
        "R": r"\bR\b",
        "Java": r"\bjava\b",
        "PyTorch": r"\bpytorch\b",
        "TensorFlow": r"\btensorflow\b",
        "scikit-learn": r"\bscikit.learn\b",
        "Spark": r"\bspark\b",
        "PySpark": r"\bpyspark\b",
        "AWS": r"\baws\b",
        "Azure": r"\bazure\b",
        "GCP": r"\bgcp\b",
        "Docker": r"\bdocker\b",
        "Kubernetes": r"\bkubernetes\b",
        "Machine Learning": r"\bmachine learning\b",
        "Deep Learning": r"\bdeep learning\b",
        "NLP": r"\bnlp\b",
        "Computer Vision": r"\bcomputer vision\b",
        "LLMs": r"\b(?:llms?|large language models?)\b",
        "RAG": r"\brag\b",
        "MLOps": r"\bmlops\b",
        "Statistics": r"\bstatistics?\b",
        "Survival Analysis": r"\bsurvival analysis\b",
        "Causal Inference": r"\bcausal inference\b",
        "Epidemiology": r"\bepidemiology\b",
        "Biostatistics": r"\bbiostatistics\b",
        "Real-World Evidence": r"\breal.world evidence\b|\brwe\b",
        "Real-World Data": r"\breal.world data\b|\brwd\b",
        "Clinical Trials": r"\bclinical trials?\b|\btrial design\b",
        "Oncology": r"\boncology\b",
        "EHR": r"\behr\b|\belectronic health records?\b",
        "BigQuery": r"\bbigquery\b",
        "Agentic AI": r"\bagentic (?:ai|frameworks?|workflows?)\b",
    }

    @staticmethod
    def clean_html(html: str) -> str:
        parser = _TextParser()
        parser.feed(unescape(html or ""))

        text = "\n".join(parser.parts)

        lines = [
            re.sub(r"\s+", " ", line).strip()
            for line in text.splitlines()
        ]

        return "\n".join(line for line in lines if line)

    @staticmethod
    def _normalize_heading(line: str) -> str:
        return line.strip().rstrip(":").casefold()

    @classmethod
    def _section_type(cls, line: str):
        heading = cls._normalize_heading(line)

        if heading in cls.REQUIREMENT_HEADINGS:
            return "requirements"

        if heading in cls.RESPONSIBILITY_HEADINGS:
            return "responsibilities"

        return None

    @classmethod
    def _is_metadata(cls, line: str) -> bool:
        return bool(
            re.fullmatch(
                r"#(?:LI|REQ|JOB)-[A-Za-z0-9_-]+",
                line.strip(),
                flags=re.IGNORECASE,
            )
        )

    @classmethod
    def _is_subsection_heading(cls, line: str) -> bool:
        return (
            cls._normalize_heading(line)
            in cls.SUBSECTION_HEADINGS
        )

    @staticmethod
    def _merge_fragments(items: list[str]) -> list[str]:
        """
        Merge only narrowly recognized fragments.
        Avoid joining unrelated requirements.
        """
        merged = []
        index = 0

        while index < len(items):
            current = items[index].strip()

            # Handle Tempus-style education/experience fragments.
            if (
                current.casefold() == "master’s degree and"
                or current.casefold() == "master's degree and"
            ):
                if (
                    index + 2 < len(items)
                    and re.fullmatch(
                        r"\d+\+?\s+years?",
                        items[index + 1].strip(),
                        flags=re.IGNORECASE,
                    )
                    and items[index + 2]
                    .strip()
                    .casefold()
                    .startswith("of additional work experience")
                ):
                    merged.append(
                        " ".join(
                            items[index:index + 3]
                        )
                    )
                    index += 3
                    continue

            # Join an introductory fragment with its immediate
            # continuation when the phrase is unambiguous.
            if (
                current.casefold() == "experience in"
                and index + 1 < len(items)
            ):
                merged.append(
                    f"{current} {items[index + 1].strip()}"
                )
                index += 2
                continue

            merged.append(current)
            index += 1

        return merged

    @classmethod
    def extract(cls, description: str) -> StructuredJobDetails:

        text = cls.clean_html(description)
        lines = text.splitlines()

        requirements = []
        responsibilities = []
        current_section = None

        for line in lines:
            section = cls._section_type(line)

            if section:
                current_section = section
                continue

            normalized = cls._normalize_heading(line)

            if normalized in cls.STOP_HEADINGS:
                current_section = None
                continue

            if (
                re.search(r"\$\s*\d[\d,]*", line)
                or normalized.startswith("the expected salary range")
                or normalized.startswith("we are an equal opportunity")
                or normalized.startswith("qualified applicants with arrest")
                or normalized.startswith("for remote roles open to")
            ):
                current_section = None
                continue

            if cls._is_metadata(line):
                continue

            if cls._is_subsection_heading(line):
                continue

            if current_section == "requirements":
                requirements.append(line)

            elif current_section == "responsibilities":
                responsibilities.append(line)

        requirements = cls._merge_fragments(requirements)
        responsibilities = cls._merge_fragments(responsibilities)

        skills = []

        for skill, pattern in cls.SKILL_PATTERNS.items():
            flags = 0 if skill == "R" else re.IGNORECASE

            if re.search(pattern, text, flags=flags):
                skills.append(skill)

        return StructuredJobDetails(
            requirements=tuple(requirements),
            responsibilities=tuple(responsibilities),
            skills=tuple(skills),
        )
