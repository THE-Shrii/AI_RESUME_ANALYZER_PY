import os

from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    genai = None


load_dotenv()


class GeminiAnalyzer:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = None
        if genai and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model_name)

    @property
    def available(self) -> bool:
        return self.model is not None

    def generate(self, prompt: str, fallback: str) -> str:
        if not self.available:
            return fallback
        try:
            response = self.model.generate_content(prompt)
            return response.text or fallback
        except Exception as exc:
            return f"{fallback}\n\nNote: Gemini response was unavailable: {exc}"

    def resume_analysis(self, result) -> str:
        prompt = f"""
        You are an expert GenAI resume reviewer. Analyze the resume against the job description.
        Return concise markdown sections: Strengths, Weaknesses, Resume Summary, Improvement Suggestions,
        and Interview Readiness Score.

        Resume:
        {result.resume_text[:9000]}

        Job Description:
        {result.jd_text[:5000]}
        """
        fallback = f"""
### Strengths
- Matched skills: {", ".join(result.matched_skills[:8]) or "No direct skill overlap detected yet."}
- ATS structure score is {result.ats_breakdown.total}/100 with visible resume sections and keyword coverage.

### Weaknesses
- Missing skills: {", ".join(result.missing_skills[:8]) or "No major missing skills found."}
- Add stronger metric-driven bullets if outcomes are not clearly quantified.

### Resume Summary
Candidate shows a {result.match_score}% match against the target role and a resume strength score of {result.resume_strength}/100.

### Improvement Suggestions
- Move the highest-value JD keywords into the top skills section.
- Rewrite project bullets using action + tool + metric + result.
- Add deployment, collaboration, and measurable impact signals.

### Interview Readiness Score
{result.interview_readiness}/100
"""
        return self.generate(prompt, fallback)

    def interview_questions(self, result) -> str:
        prompt = f"""
        Generate interview questions from this resume and job description.
        Use markdown headings: Technical Questions, Behavioral Questions, Project-Based Questions, HR Questions.
        Include 5 questions per category.

        Resume:
        {result.resume_text[:8000]}

        Job Description:
        {result.jd_text[:5000]}
        """
        focus = ", ".join(result.missing_skills[:4] or result.jd_skills[:4] or ["the target role"])
        fallback = f"""
### Technical Questions
1. How would you design a project using {focus}?
2. Explain one technical tradeoff from your strongest project.
3. How do you validate model or application performance?
4. What would you improve in your current AI workflow?
5. How do you handle deployment and monitoring?

### Behavioral Questions
1. Tell me about a time you learned a missing skill quickly.
2. Describe a project setback and how you recovered.
3. How do you prioritize when requirements are unclear?
4. Explain how you communicate technical work to non-technical people.
5. What feedback changed the way you build software?

### Project-Based Questions
1. Walk me through your most relevant project architecture.
2. Which metrics prove the project worked?
3. What would break at scale?
4. How would you make the project production-ready?
5. What did you personally own?

### HR Questions
1. Why are you interested in this role?
2. What makes you a strong fit?
3. What are your next learning goals?
4. How do you handle deadlines?
5. Why should we hire you?
"""
        return self.generate(prompt, fallback)

    def learning_roadmap(self, result) -> str:
        skills = ", ".join(result.missing_skills or result.recommended_skills)
        prompt = f"""
        Create a 4-week learning roadmap for these missing skills: {skills}.
        Use Week 1, Week 2, Week 3, Week 4 headings. Include projects and outcomes.
        """
        fallback = f"""
### Week 1
- Study fundamentals for: {skills or "role-specific tools"}.
- Build short notes and one mini exercise per skill.

### Week 2
- Implement a small project using the top missing skills.
- Add tests, documentation, and GitHub commits.

### Week 3
- Convert the project into a portfolio case study with metrics.
- Practice explaining tradeoffs and architecture.

### Week 4
- Polish resume bullets, deploy the project, and rehearse interview answers.
- Re-run ResumeIQ and target a match score above 80%.
"""
        return self.generate(prompt, fallback)

    def recruiter_summary(self, result) -> str:
        prompt = f"""
        Write a recruiter summary for this candidate against the JD.
        Include Candidate Overview, Strength Areas, Concerns, and Hiring Recommendation.

        Resume:
        {result.resume_text[:8000]}

        JD:
        {result.jd_text[:5000]}
        """
        fallback = f"""
### Candidate Overview
The candidate currently matches {result.match_score}% of detected role skills with an ATS score of {result.ats_breakdown.total}/100.

### Strength Areas
- {", ".join(result.matched_skills[:8]) or "General technical foundation"}
- Resume strength score: {result.resume_strength}/100

### Concerns
- Missing skills: {", ".join(result.missing_skills[:8]) or "No critical keyword gaps detected"}
- Validate depth through project and system design questions.

### Hiring Recommendation
Proceed if the role values growth potential and the candidate can explain project ownership clearly. Prioritize screening around missing skills and production-readiness experience.
"""
        return self.generate(prompt, fallback)


def analyze_resume(resume_text: str, jd_text: str) -> str:
    from utils.score_calculator import ResumeAnalysisEngine

    result = ResumeAnalysisEngine().analyze(resume_text, jd_text)
    return GeminiAnalyzer().resume_analysis(result)
