"""補正済みの画像をGoogleドライブの指定フォルダにアップロードする。"""

import config


def upload(image_bytes: bytes, filename: str) -> str:
    """Google Drive APIで画像をアップロードし、ファイルIDを返す。"""
    if not config.GOOGLE_DRIVE_CREDENTIALS_PATH:
        raise RuntimeError("GOOGLE_DRIVE_CREDENTIALS_PATH が未設定です")
    if not config.DRIVE_FOLDER_ID:
        raise RuntimeError("config.DRIVE_FOLDER_ID が未設定です")
    # TODO: google-api-python-client を使ったアップロード実装
    raise NotImplementedError
