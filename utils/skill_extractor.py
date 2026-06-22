from pathlib import Path
from functools import lru_cache
import re

import pandas as pd


SKILLS_PATH = Path(__file__).resolve().parent.parent / "data" / "skills.csv"


@lru_cache(maxsize=1)
def load_skill_catalog() -> list[str]:
    if not SKILLS_PATH.exists():
        return []
    skills_df = pd.read_csv(SKILLS_PATH)
    return sorted({str(skill).strip().lower() for skill in skills_df["skill"].dropna() if str(skill).strip()})


class SkillExtractor:
    def __init__(self, skills: list[str] | None = None):
        self.skills = skills or load_skill_catalog()

    def extract(self, text: str) -> list[str]:
        normalized = f" {text.lower()} "
        found = []
        for skill in self.skills:
            pattern = rf"(?<![a-z0-9+#.]){re.escape(skill)}(?![a-z0-9+#.])"
            if re.search(pattern, normalized):
                found.append(skill)
        return sorted(set(found))

    def recommend(self, missing_skills: list[str], limit: int = 8) -> list[str]:
        emerging = [
            "generative ai",
            "llm",
            "rag",
            "vector database",
            "langchain",
            "prompt engineering",
            "mlops",
            "docker",
            "cloud deployment",
            "fastapi",
        ]
        combined = list(dict.fromkeys(missing_skills + emerging))
        return combined[:limit]


def extract_skills(text: str) -> list[str]:
    return SkillExtractor().extract(text)
