"""補正済みの画像をGoogleドライブの指定フォルダにアップロードする。"""

import json

import config


def _get_credentials():
    from google.oauth2 import service_account

    info = json.loads(config.GOOGLE_DRIVE_CREDENTIALS_JSON)
    return service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/drive.file"]
    )


def upload(image_bytes: bytes, filename: str) -> str:
    """Google Drive APIで画像をアップロードし、ファイルIDを返す。"""
    if not config.GOOGLE_DRIVE_CREDENTIALS_JSON:
        raise RuntimeError("GOOGLE_DRIVE_CREDENTIALS_JSON が未設定です")
    if not config.DRIVE_FOLDER_ID:
        raise RuntimeError("config.DRIVE_FOLDER_ID が未設定です")
    # TODO: googleapiclient.discovery.build("drive", "v3", credentials=_get_credentials())
    # を使ったアップロード実装
    raise NotImplementedError
