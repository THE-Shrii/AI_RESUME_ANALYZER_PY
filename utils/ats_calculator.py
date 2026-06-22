import re
from dataclasses import dataclass


@dataclass
class ATSBreakdown:
    skill_match: float
    contact_info: float
    structure: float
    impact: float
    readability: float

    @property
    def total(self) -> int:
        return round(self.skill_match + self.contact_info + self.structure + self.impact + self.readability)

    def as_dict(self) -> dict[str, float]:
        return {
            "Skill Match": round(self.skill_match, 1),
            "Contact Info": round(self.contact_info, 1),
            "Structure": round(self.structure, 1),
            "Impact": round(self.impact, 1),
            "Readability": round(self.readability, 1),
        }


class ATSCalculator:
    def calculate(self, resume_text: str, resume_skills: list[str], jd_skills: list[str]) -> ATSBreakdown:
        lower = resume_text.lower()
        matched = len(set(resume_skills) & set(jd_skills))
        skill_match = (matched / len(jd_skills) * 40) if jd_skills else 0

        contact_info = 0
        if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", resume_text):
            contact_info += 5
        if re.search(r"(\+?\d[\d\s().-]{8,}\d)", resume_text):
            contact_info += 5
        if "linkedin" in lower or "github" in lower:
            contact_info += 5

        sections = ["experience", "education", "projects", "skills", "summary"]
        structure = min(sum(1 for section in sections if section in lower) * 4, 20)

        impact_words = ["built", "improved", "reduced", "increased", "automated", "deployed", "optimized", "led"]
        metrics = len(re.findall(r"\b\d+[%+]?\b", resume_text))
        impact = min(sum(1 for word in impact_words if word in lower) * 2 + metrics * 2, 15)

        word_count = len(resume_text.split())
        readability = 10 if 300 <= word_count <= 900 else 7 if 180 <= word_count < 300 else 5

        return ATSBreakdown(skill_match, contact_info, structure, impact, readability)


def calculate_ats_score(resume_text: str, resume_skills: list[str], jd_skills: list[str]) -> int:
    return ATSCalculator().calculate(resume_text, resume_skills, jd_skills).total
