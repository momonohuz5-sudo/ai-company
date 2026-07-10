"""補正済みの画像をGoogleドライブの指定フォルダにアップロードする。"""

import config


def _get_credentials():
    from google.oauth2.credentials import Credentials

    return Credentials(
        token=None,
        refresh_token=config.GOOGLE_DRIVE_REFRESH_TOKEN,
        client_id=config.GOOGLE_DRIVE_CLIENT_ID,
        client_secret=config.GOOGLE_DRIVE_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/drive.file"],
    )


def upload(image_bytes: bytes, filename: str) -> str:
    """Google Drive APIで画像をアップロードし、ファイルIDを返す。"""
    if not (
        config.GOOGLE_DRIVE_CLIENT_ID
        and config.GOOGLE_DRIVE_CLIENT_SECRET
        and config.GOOGLE_DRIVE_REFRESH_TOKEN
    ):
        raise RuntimeError(
            "GOOGLE_DRIVE_CLIENT_ID / GOOGLE_DRIVE_CLIENT_SECRET / "
            "GOOGLE_DRIVE_REFRESH_TOKEN のいずれかが未設定です"
        )
    if not config.DRIVE_FOLDER_ID:
        raise RuntimeError("config.DRIVE_FOLDER_ID が未設定です")
    # TODO: googleapiclient.discovery.build("drive", "v3", credentials=_get_credentials())
    # と MediaIoBaseUpload を使ったアップロード実装
    raise NotImplementedError
