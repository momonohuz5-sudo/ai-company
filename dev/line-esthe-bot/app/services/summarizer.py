from abc import ABC, abstractmethod
from pathlib import Path

from app.models.review import Review
from app.models.summary import SummaryResult

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "summary_prompt.txt"


def build_prompt(reviews: list[Review]) -> str:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    reviews_text = "\n".join(
        f"口コミ{i}：\n「{review.text}」" for i, review in enumerate(reviews, start=1)
    )
    # Uses a plain substring replace (not str.format) because the template
    # contains literal JSON braces in its output-format example.
    return template.replace("{reviews}", reviews_text)


class Summarizer(ABC):
    @abstractmethod
    async def summarize(self, reviews: list[Review]) -> SummaryResult:
        raise NotImplementedError
