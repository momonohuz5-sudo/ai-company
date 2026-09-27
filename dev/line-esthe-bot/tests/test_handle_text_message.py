import pytest

from app.line import webhook
from app.models.review import Review
from app.models.search_result import SearchResult


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
async def test_results_found_pushes_count(monkeypatch):
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

    async def fake_push_text(user_id, text):
        pushed["text"] = text

    monkeypatch.setattr(webhook, "search_all", fake_search_all)
    monkeypatch.setattr(webhook, "push_text", fake_push_text)

    await webhook.handle_text_message("token-1", "user-1", "ABC新宿 あい")

    assert "1件見つかったよ" in pushed["text"]


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
