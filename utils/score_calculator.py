from dataclasses import dataclass

from utils.ats_calculator import ATSBreakdown, ATSCalculator
from utils.skill_extractor import SkillExtractor
from utils.text_cleaner import TextCleaner


@dataclass
class AnalysisResult:
    resume_text: str
    jd_text: str
    resume_skills: list[str]
    jd_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    recommended_skills: list[str]
    emerging_skills: list[str]
    match_score: float
    ats_breakdown: ATSBreakdown
    resume_strength: int
    interview_readiness: int
    improvements: list[dict[str, str]]


class ResumeAnalysisEngine:
    def __init__(self, cleaner: TextCleaner | None = None, extractor: SkillExtractor | None = None):
        self.cleaner = cleaner or TextCleaner()
        self.extractor = extractor or SkillExtractor()
        self.ats = ATSCalculator()

    def analyze(self, resume_text: str, jd_text: str) -> AnalysisResult:
        clean_resume = self.cleaner.clean(resume_text)
        clean_jd = self.cleaner.clean(jd_text)
        resume_skills = self.extractor.extract(clean_resume)
        jd_skills = self.extractor.extract(clean_jd)
        matched = sorted(set(resume_skills) & set(jd_skills))
        missing = sorted(set(jd_skills) - set(resume_skills))
        match_score = calculate_score(resume_skills, jd_skills)
        ats_breakdown = self.ats.calculate(resume_text, resume_skills, jd_skills)
        recommended = self.extractor.recommend(missing)
        emerging = [skill for skill in recommended if skill not in missing][:5]
        strength = min(round((match_score * 0.45) + (ats_breakdown.total * 0.55)), 100)
        readiness = min(round((match_score * 0.5) + (len(matched) * 4) + (ats_breakdown.impact * 1.2)), 100)

        return AnalysisResult(
            resume_text=resume_text,
            jd_text=jd_text,
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            matched_skills=matched,
            missing_skills=missing,
            recommended_skills=recommended,
            emerging_skills=emerging,
            match_score=match_score,
            ats_breakdown=ats_breakdown,
            resume_strength=strength,
            interview_readiness=readiness,
            improvements=self._build_improvements(missing, matched),
        )

    def _build_improvements(self, missing: list[str], matched: list[str]) -> list[dict[str, str]]:
        primary_gap = ", ".join(missing[:3]) if missing else "role-specific tooling"
        proof = ", ".join(matched[:3]) if matched else "technical projects"
        return [
            {
                "before": "Worked on machine learning projects and built applications.",
                "after": f"Built measurable AI projects using {proof}, highlighting outcomes, deployment context, and business impact.",
            },
            {
                "before": "Skills listed without prioritization.",
                "after": f"Create a targeted skills section with the JD keywords first, especially {primary_gap}.",
            },
            {
                "before": "Project bullets describe tasks.",
                "after": "Rewrite project bullets with action, tool, metric, and result so ATS and recruiters can detect seniority signals.",
            },
        ]


def calculate_score(resume_skills: list[str], jd_skills: list[str]) -> float:
    if not jd_skills:
        return 0
    matched = set(resume_skills).intersection(set(jd_skills))
    return round((len(matched) / len(set(jd_skills))) * 100, 2)
