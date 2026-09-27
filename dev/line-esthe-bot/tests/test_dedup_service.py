from app.models.review import Review
from app.services.dedup_service import dedup_reviews


def _review(text: str, source: str = "site-a") -> Review:
    return Review(
        source=source,
        shop_name="ABC新宿",
        therapist_name="あい",
        text=text,
        url=None,
        date=None,
    )


def test_exact_duplicate_removed():
    reviews = [_review("話しやすかった"), _review("話しやすかった")]
    result = dedup_reviews(reviews)
    assert len(result) == 1


def test_whitespace_and_newline_variant_removed():
    reviews = [
        _review("話しやすかった"),
        _review("  話しやすかった\n\n"),
    ]
    result = dedup_reviews(reviews)
    assert len(result) == 1


def test_symbol_variant_removed():
    reviews = [
        _review("話しやすかった！"),
        _review("話しやすかった。"),
    ]
    result = dedup_reviews(reviews)
    assert len(result) == 1


def test_distinct_reviews_kept():
    reviews = [_review("話しやすかった"), _review("施術が丁寧だった")]
    result = dedup_reviews(reviews)
    assert len(result) == 2


def test_cross_source_duplicate_removed():
    reviews = [_review("話しやすかった", source="site-a"), _review("話しやすかった", source="site-b")]
    result = dedup_reviews(reviews)
    assert len(result) == 1


def test_empty_text_dropped():
    reviews = [_review("   ")]
    result = dedup_reviews(reviews)
    assert result == []
