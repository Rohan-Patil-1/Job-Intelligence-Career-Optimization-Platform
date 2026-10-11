from dataclasses import dataclass, field

from src.analytics.seniority import SeniorityLevel


@dataclass
class CandidateProfile:
    name: str
    target_roles: list[str] = field(default_factory=list)
    skills: set[str] = field(default_factory=set)

    target_seniority: set[SeniorityLevel] = field(
        default_factory=set
    )
    preferred_domains: set[str] = field(default_factory=set)

    def normalized_skills(self) -> set[str]:
        return {
            skill.strip().lower()
            for skill in self.skills
            if skill.strip()
        }