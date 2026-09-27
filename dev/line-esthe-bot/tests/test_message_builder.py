from app.models.summary import SummaryResult
from app.services.message_builder import build_summary_message


def test_single_review_uses_soft_closing():
    summary = SummaryResult(review_count=1, summary_points=["話しやすいという口コミがある"])
    message = build_summary_message("あい", summary)
    assert message.startswith("あいさんのレビューはこんな感じ！")
    assert "・話しやすいという口コミがある" in message
    assert "こんな口コミがみられたよ！" in message
    assert "多くみられた" not in message


def test_few_reviews_uses_multiple_wording():
    summary = SummaryResult(review_count=3, summary_points=["丁寧という声がある"])
    message = build_summary_message("あい", summary)
    assert "複数の口コミで" in message


def test_many_reviews_uses_ooi_wording():
    summary = SummaryResult(review_count=10, summary_points=["丁寧という声がある"])
    message = build_summary_message("あい", summary)
    assert "多くみられたよ" in message


def test_mixed_opinion_notes_split_evaluation():
    summary = SummaryResult(
        review_count=5,
        summary_points=["話しやすいという声がある", "施術が雑という声もある"],
        mixed_opinion=True,
    )
    message = build_summary_message("あい", summary)
    assert "評価が分かれている" in message
