from datetime import datetime
from pathlib import Path


class ReportGenerator:
    def __init__(self, output_dir: str | Path = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def build_markdown(self, result, ai_analysis: str, questions: str, roadmap: str, recruiter_summary: str) -> str:
        matched = ", ".join(result.matched_skills) or "None detected"
        missing = ", ".join(result.missing_skills) or "None detected"
        return f"""# ResumeIQ AI Resume Report

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Score Dashboard

- ATS Score: {result.ats_breakdown.total}/100
- Match Score: {result.match_score}%
- Resume Strength: {result.resume_strength}/100
- Interview Readiness: {result.interview_readiness}/100

## ATS Breakdown

{self._bullet_dict(result.ats_breakdown.as_dict())}

## Skills

Matched Skills: {matched}

Missing Skills: {missing}

Recommended Skills: {", ".join(result.recommended_skills)}

## AI Analysis

{ai_analysis}

## Interview Questions

{questions}

## Learning Roadmap

{roadmap}

## Recruiter Summary

{recruiter_summary}
"""

    def build_download_bytes(self, result, ai_analysis: str, questions: str, roadmap: str, recruiter_summary: str) -> bytes:
        report = self.build_markdown(result, ai_analysis, questions, roadmap, recruiter_summary)
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
            from io import BytesIO

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, title="ResumeIQ AI Resume Report")
            styles = getSampleStyleSheet()
            story = []
            for line in report.splitlines():
                if line.startswith("# "):
                    story.append(Paragraph(line[2:], styles["Title"]))
                elif line.startswith("## "):
                    story.append(Spacer(1, 12))
                    story.append(Paragraph(line[3:], styles["Heading2"]))
                elif line.strip():
                    story.append(Paragraph(line, styles["BodyText"]))
                    story.append(Spacer(1, 5))
            doc.build(story)
            return buffer.getvalue()
        except Exception:
            return report.encode("utf-8")

    def _bullet_dict(self, values: dict[str, float]) -> str:
        return "\n".join(f"- {key}: {value}" for key, value in values.items())
