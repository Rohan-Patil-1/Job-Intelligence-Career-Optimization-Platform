import re
from dataclasses import dataclass


@dataclass(frozen=True)
class TitleDiagnostic:
    is_mixed_role: bool
    detected_roles: tuple[str, ...]
    label: str


class TitleDiagnostics:

    ROLE_PATTERNS = {
        "data_scientist": r"\bdata scientist\b",
        "data_analyst": r"\bdata analyst\b",
        "java_developer": r"\bjava(?:\s+spring\s+boot)?\s+developer\b",
        "software_engineer": r"\bsoftware engineer\b",
        "machine_learning_engineer": r"\bmachine learning engineer\b",
        "ai_engineer": r"\bai engineer\b",
        "business_analyst": r"\bbusiness analyst\b",
    }

    @classmethod
    def analyze(cls, title: str) -> TitleDiagnostic:
        normalized = re.sub(r"[-_/]+", " ", title.lower())

        detected = tuple(
            role
            for role, pattern in cls.ROLE_PATTERNS.items()
            if re.search(pattern, normalized)
        )

        mixed = len(detected) >= 2

        return TitleDiagnostic(
            is_mixed_role=mixed,
            detected_roles=detected,
            label="mixed_role" if mixed else "single_or_unknown",
        )