import json
import re

import httpx

from app.config import get_settings
from app.models.review import Review
from app.models.summary import SummaryResult
from app.services.summarizer import Summarizer, build_prompt
from app.utils.logger import get_logger

logger = get_logger(__name__)

GEMINI_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)

# Gemini sometimes wraps JSON in a ```json ... ``` fence despite instructions
# not to add extra text; strip that before parsing.
_FENCE_PATTERN = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


class GeminiSummarizer(Summarizer):
    async def summarize(self, reviews: list[Review]) -> SummaryResult:
        settings = get_settings()
        prompt = build_prompt(reviews)
        url = GEMINI_URL_TEMPLATE.format(model=settings.gemini_model)

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                url,
                params={"key": settings.gemini_api_key},
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            response.raise_for_status()

        payload = response.json()
        raw_text = payload["candidates"][0]["content"]["parts"][0]["text"]
        return _parse_summary(raw_text, fallback_count=len(reviews))


def _parse_summary(raw_text: str, fallback_count: int) -> SummaryResult:
    cleaned = _FENCE_PATTERN.sub("", raw_text).strip()
    data = json.loads(cleaned)
    return SummaryResult(
        review_count=int(data.get("review_count", fallback_count)),
        summary_points=list(data.get("summary_points", [])),
        mixed_opinion=bool(data.get("mixed_opinion", False)),
    )
