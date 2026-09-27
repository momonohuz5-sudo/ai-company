import pytest

from app.line import webhook
from app.models.review import Review
from app.models.search_result import SearchResult
from app.models.summary import SummaryResult


@pytest.fixture(autouse=True)
def no_op_cache(monkeypatch):
    async def fake_get_cached_message(shop_name, therapist_name):
        return None

    async def fake_save_cache(shop_name, therapist_name, message, review_count):
        pass

    async def fake_save_reviews(shop_name, therapist_name, reviews):
        pass

    monkeypatch.setattr(webhook, "get_cached_message", fake_get_cached_message)
    monkeypatch.setattr(webhook, "save_cache", fake_save_cache)
    monkeypatch.setattr(webhook, "save_reviews", fake_save_reviews)


@pytest.mark.asyncio
async def test_missing_shop_replies_with_reply_token(monkeypatch):
    sent = {}

    async def fake_reply_text(reply_token, text):
        sent["reply_token"] = reply_token
        sent["text"] = text

    monkeypatch.setattr(webhook, "reply_text", fake_reply_text)

    await webhook.handle_text_message("token-1", "user-1", "あい")

    assert sent["reply_token"] == "token-1"
    assert sent["text"] == webhook.MISSING_SHOP_MESSAGE


@pytest.mark.asyncio
async def test_unparseable_replies_with_example(monkeypatch):
    sent = {}

    async def fake_reply_text(reply_token, text):
        sent["text"] = text

    monkeypatch.setattr(webhook, "reply_text", fake_reply_text)

    await webhook.handle_text_message("token-1", "user-1", "   ")

    assert sent["text"] == webhook.UNPARSEABLE_MESSAGE


@pytest.mark.asyncio
async def test_no_results_pushes_not_found_message(monkeypatch):
    pushed = {}

    async def fake_search_all(shop_name, therapist_name):
        return SearchResult(shop_name=shop_name, therapist_name=therapist_name, reviews=[])

    async def fake_push_text(user_id, text):
        pushed["user_id"] = user_id
        pushed["text"] = text

    monkeypatch.setattr(webhook, "search_all", fake_search_all)
    monkeypatch.setattr(webhook, "push_text", fake_push_text)

    await webhook.handle_text_message("token-1", "user-1", "ABC新宿 あい")

    assert pushed["user_id"] == "user-1"
    assert "見つけられなかった" in pushed["text"]


@pytest.mark.asyncio
async def test_results_found_pushes_summary(monkeypatch):
    pushed = {}

    async def fake_search_all(shop_name, therapist_name):
        return SearchResult(
            shop_name=shop_name,
            therapist_name=therapist_name,
            reviews=[
                Review(
                    source="ok-site",
                    shop_name=shop_name,
                    therapist_name=therapist_name,
                    text="話しやすかった",
                    url=None,
                    date=None,
                )
            ],
        )

    async def fake_summarize(reviews):
        return SummaryResult(
            review_count=1,
            summary_points=["話しやすいという口コミがある"],
            mixed_opinion=False,
        )

    async def fake_push_text(user_id, text):
        pushed["text"] = text

    monkeypatch.setattr(webhook, "search_all", fake_search_all)
    monkeypatch.setattr(webhook.summarizer, "summarize", fake_summarize)
    monkeypatch.setattr(webhook, "push_text", fake_push_text)

    await webhook.handle_text_message("token-1", "user-1", "ABC新宿 あい")

    assert "あいさんのレビューはこんな感じ！" in pushed["text"]
    assert "話しやすいという口コミがある" in pushed["text"]


@pytest.mark.asyncio
async def test_summarize_failure_pushes_generic_error(monkeypatch):
    pushed = {}

    async def fake_search_all(shop_name, therapist_name):
        return SearchResult(
            shop_name=shop_name,
            therapist_name=therapist_name,
            reviews=[
                Review(
                    source="ok-site",
                    shop_name=shop_name,
                    therapist_name=therapist_name,
                    text="話しやすかった",
                    url=None,
                    date=None,
                )
            ],
        )

    async def fake_summarize(reviews):
        raise RuntimeError("boom")

    async def fake_push_text(user_id, text):
        pushed["text"] = text

    monkeypatch.setattr(webhook, "search_all", fake_search_all)
    monkeypatch.setattr(webhook.summarizer, "summarize", fake_summarize)
    monkeypatch.setattr(webhook, "push_text", fake_push_text)

    await webhook.handle_text_message("token-1", "user-1", "ABC新宿 あい")

    assert pushed["text"] == webhook.SEARCH_FAILED_MESSAGE


@pytest.mark.asyncio
async def test_search_failure_pushes_generic_error(monkeypatch):
    pushed = {}

    async def fake_search_all(shop_name, therapist_name):
        raise RuntimeError("boom")

    async def fake_push_text(user_id, text):
        pushed["text"] = text

    monkeypatch.setattr(webhook, "search_all", fake_search_all)
    monkeypatch.setattr(webhook, "push_text", fake_push_text)

    await webhook.handle_text_message("token-1", "user-1", "ABC新宿 あい")

    assert pushed["text"] == webhook.SEARCH_FAILED_MESSAGE


@pytest.mark.asyncio
async def test_cache_hit_skips_search_and_pushes_cached_message(monkeypatch):
    pushed = {}
    calls = {"search_all": 0}

    async def fake_get_cached_message(shop_name, therapist_name):
        return "キャッシュされた結果だよ！"

    async def fake_search_all(shop_name, therapist_name):
        calls["search_all"] += 1
        return SearchResult(shop_name=shop_name, therapist_name=therapist_name, reviews=[])

    async def fake_push_text(user_id, text):
        pushed["text"] = text

    monkeypatch.setattr(webhook, "get_cached_message", fake_get_cached_message)
    monkeypatch.setattr(webhook, "search_all", fake_search_all)
    monkeypatch.setattr(webhook, "push_text", fake_push_text)

    await webhook.handle_text_message("token-1", "user-1", "ABC新宿 あい")

    assert pushed["text"] == "キャッシュされた結果だよ！"
    assert calls["search_all"] == 0
