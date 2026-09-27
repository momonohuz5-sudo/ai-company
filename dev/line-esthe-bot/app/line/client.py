import httpx

from app.config import get_settings

LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"


async def reply_text(reply_token: str, text: str) -> None:
    settings = get_settings()
    headers = {
        "Authorization": f"Bearer {settings.line_channel_access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}],
    }
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(LINE_REPLY_URL, headers=headers, json=payload)
        response.raise_for_status()


async def push_text(user_id: str, text: str) -> None:
    settings = get_settings()
    headers = {
        "Authorization": f"Bearer {settings.line_channel_access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": text}],
    }
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(LINE_PUSH_URL, headers=headers, json=payload)
        response.raise_for_status()
