import re


class TextCleaner:
    def clean(self, text: str) -> str:
        text = text or ""
        text = text.lower()
        text = re.sub(r"[^a-zA-Z0-9+#.\s-]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def words(self, text: str) -> list[str]:
        return self.clean(text).split()


def clean_text(text: str) -> str:
    return TextCleaner().clean(text)
