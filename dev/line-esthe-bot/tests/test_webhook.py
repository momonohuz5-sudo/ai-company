import base64
import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

client = TestClient(app)


def _sign(body: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_webhook_rejects_invalid_signature():
    body = json.dumps({"events": []}).encode("utf-8")
    response = client.post(
        "/webhook", content=body, headers={"X-Line-Signature": "bad"}
    )
    assert response.status_code == 400


def test_webhook_accepts_valid_signature(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "line_channel_secret", "testsecret")
    body = json.dumps({"events": []}).encode("utf-8")
    signature = _sign(body, "testsecret")
    response = client.post(
        "/webhook", content=body, headers={"X-Line-Signature": signature}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
