import json

from app.services.gemini_summarizer import _parse_summary
from app.services.summarizer import build_prompt
from app.models.review import Review


def test_parse_summary_plain_json():
    raw = json.dumps(
        {
            "review_count": 3,
            "summary_points": ["話しやすいという声がある", "丁寧という声がある"],
            "mixed_opinion": False,
        },
        ensure_ascii=False,
    )
    result = _parse_summary(raw, fallback_count=3)
    assert result.review_count == 3
    assert result.summary_points == ["話しやすいという声がある", "丁寧という声がある"]
    assert result.mixed_opinion is False


def test_parse_summary_strips_code_fence():
    raw = "```json\n" + json.dumps({"review_count": 1, "summary_points": ["a"]}) + "\n```"
    result = _parse_summary(raw, fallback_count=1)
    assert result.review_count == 1
    assert result.summary_points == ["a"]


def test_build_prompt_includes_reviews_and_handles_json_braces():
    reviews = [
        Review(
            source="site-a",
            shop_name="ABC新宿",
            therapist_name="あい",
            text="話しやすかった",
            url=None,
            date=None,
        )
    ]
    prompt = build_prompt(reviews)
    assert "話しやすかった" in prompt
    assert "review_count" in prompt
