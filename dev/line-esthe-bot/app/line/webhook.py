import base64
import hashlib
import hmac

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from app.config import get_settings
from app.line.client import reply_text
from app.services.parser_service import ParseStatus, parse_query
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

MISSING_SHOP_MESSAGE = "店舗名も一緒に送ってね！"
UNPARSEABLE_MESSAGE = (
    "店舗名とセラピスト名を一緒に送ってね！\n"
    "例：\n"
    "ABC新宿 あい"
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


async def handle_text_message(reply_token: str, text: str) -> None:
    result = parse_query(text)

    if result.status == ParseStatus.UNPARSEABLE:
        await reply_text(reply_token, UNPARSEABLE_MESSAGE)
        return

    if result.status == ParseStatus.MISSING_SHOP:
        await reply_text(reply_token, MISSING_SHOP_MESSAGE)
        return

    # Phase 2: parsing only. Search/scrape/summary land in later phases.
    query = result.query
    assert query is not None
    await reply_text(
        reply_token,
        f"店舗名：{query.shop_name}\nセラピスト名：{query.therapist_name}\nで検索するね！",
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
        if reply_token:
            background_tasks.add_task(handle_text_message, reply_token, text)

    return {"status": "ok"}
