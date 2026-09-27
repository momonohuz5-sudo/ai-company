import base64
import hashlib
import hmac

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from app.config import get_settings
from app.line.client import push_text, reply_text
from app.services.parser_service import ParseStatus, parse_query
from app.services.search_service import search_all
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

MISSING_SHOP_MESSAGE = "店舗名も一緒に送ってね！"
UNPARSEABLE_MESSAGE = (
    "店舗名とセラピスト名を一緒に送ってね！\n"
    "例：\n"
    "ABC新宿 あい"
)
NOT_FOUND_MESSAGE_TEMPLATE = (
    "{therapist_name}さんの口コミを探してみたけど、今回は見つけられなかったよ。\n"
    "店舗名や名前の表記を変えてもう一度検索してみてね！"
)
SEARCH_FAILED_MESSAGE = (
    "現在口コミを取得できませんでした。少し時間を空けてもう一度試してみてね。"
)


def verify_signature(body: bytes, signature: str | None) -> bool:
    settings = get_settings()
    if not signature or not settings.line_channel_secret:
        return False
    digest = hmac.new(
        settings.line_channel_secret.encode("utf-8"), body, hashlib.sha256
    ).digest()
    expected = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(expected, signature)


async def handle_text_message(reply_token: str, user_id: str | None, text: str) -> None:
    result = parse_query(text)

    if result.status == ParseStatus.UNPARSEABLE:
        await reply_text(reply_token, UNPARSEABLE_MESSAGE)
        return

    if result.status == ParseStatus.MISSING_SHOP:
        await reply_text(reply_token, MISSING_SHOP_MESSAGE)
        return

    query = result.query
    assert query is not None

    if not user_id:
        # No push target available; nothing more we can do for this event.
        logger.warning("no user_id on event; cannot push search results")
        return

    try:
        search_result = await search_all(query.shop_name, query.therapist_name)
    except Exception:
        logger.exception(
            "search_all failed for shop=%s therapist=%s",
            query.shop_name,
            query.therapist_name,
        )
        await push_text(user_id, SEARCH_FAILED_MESSAGE)
        return

    if search_result.total_reviews == 0:
        await push_text(
            user_id,
            NOT_FOUND_MESSAGE_TEMPLATE.format(therapist_name=query.therapist_name),
        )
        return

    # Phase 3: search/dedup only. AI summarization lands in Phase 5; for now
    # push back what was found so the pipeline is verifiable end-to-end.
    await push_text(
        user_id,
        f"{query.therapist_name}さんの口コミが{search_result.total_reviews}件見つかったよ！"
        "（要約は準備中）",
    )


@router.post("/webhook")
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_line_signature: str | None = Header(default=None),
):
    body = await request.body()

    if not verify_signature(body, x_line_signature):
        raise HTTPException(status_code=400, detail="invalid signature")

    payload = await request.json()
    for event in payload.get("events", []):
        if event.get("type") != "message":
            continue
        message = event.get("message", {})
        if message.get("type") != "text":
            continue
        reply_token = event.get("replyToken")
        text = message.get("text", "")
        user_id = event.get("source", {}).get("userId")
        if reply_token:
            background_tasks.add_task(
                handle_text_message, reply_token, user_id, text
            )

    return {"status": "ok"}
