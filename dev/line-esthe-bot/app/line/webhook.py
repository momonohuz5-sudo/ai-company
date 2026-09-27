import base64
import hashlib
import hmac

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from app.config import get_settings
from app.line.client import reply_text
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


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
    # Phase 1: fixed reply only. Parsing/search/summary land in later phases.
    await reply_text(reply_token, f"メッセージを受け取ったよ！\n「{text}」")


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
