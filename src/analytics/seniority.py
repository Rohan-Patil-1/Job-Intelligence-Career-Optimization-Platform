from dataclasses import dataclass
from enum import IntEnum
import re


class SeniorityLevel(IntEnum):
    UNKNOWN = 0
    ENTRY = 1
    MID = 2
    SENIOR = 3
    LEAD = 4
    MANAGER = 5
    DIRECTOR = 6
    VP = 7


@dataclass(frozen=True)
class SeniorityResult:
    level: SeniorityLevel
    label: str


SENIORITY_PATTERNS = {
    SeniorityLevel.VP: [
        r"\bvice president\b",
        r"\bvp\b",
    ],

    SeniorityLevel.DIRECTOR: [
        r"\bdirector\b",
    ],

    SeniorityLevel.MANAGER: [
        r"\bsr\.?\s+manager\b",
        r"\bsenior manager\b",
        r"\bmanager\b",
    ],

    SeniorityLevel.LEAD: [
        r"\blead\b",
        r"\bprincipal\b",
    ],

    SeniorityLevel.SENIOR: [
        r"\bsenior\b",
        r"\bsr\.?\b",
    ],

    SeniorityLevel.ENTRY: [
        r"\bjunior\b",
        r"\bjr\.?\b",
        r"\bentry[- ]level\b",
        r"\bassociate\b",
    ],
}


def detect_seniority(title: str) -> SeniorityResult:
    if not title:
        return SeniorityResult(
            level=SeniorityLevel.UNKNOWN,
            label="unknown",
        )

    normalized = title.lower().strip()

    # Search highest seniority first.
    for level in sorted(
        SENIORITY_PATTERNS,
        reverse=True,
    ):
        patterns = SENIORITY_PATTERNS[level]

        for pattern in patterns:
            if re.search(pattern, normalized):
                return SeniorityResult(
                    level=level,
                    label=level.name.lower(),
                )

    # No explicit seniority term.
    return SeniorityResult(
        level=SeniorityLevel.MID,
        label="mid",
    )