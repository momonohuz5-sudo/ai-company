"""エステ魂 ポチ（リアルタイム集客）自動化の設定。

サイトの資格情報・カレンダーIDは未確定のため環境変数名だけ定義している。
実際の値は `.env` などで注入し、このリポジトリにはコミットしないこと。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Site:
    """外部媒体の管理画面にログインする単位（サイト＝店舗）。"""

    id: str
    name: str
    # 管理画面ログイン情報は環境変数から読む。値はコード・チャットに直書きしない。
    login_url_env: str
    username_env: str
    password_env: str


@dataclass(frozen=True)
class PokeUnit:
    """ポチの意思決定単位。1ユニット=1つの10回/日枠。

    sites: このユニットがポチ時にクリックするサイト（複数なら同時にクリックする）。
    calendar_ids_env: 空き状況判定に使うGoogleカレンダーID（環境変数名）。
    複数指定した場合は「いずれかが空いていれば空き」として扱う（OR判定）。
    """

    id: str
    label: str
    sites: tuple[str, ...]
    calendar_ids_env: tuple[str, ...]


SITES: dict[str, Site] = {
    "nobia_kanda": Site(
        id="nobia_kanda",
        name="ノビア神田",
        login_url_env="NOBIA_KANDA_LOGIN_URL",
        username_env="NOBIA_KANDA_USERNAME",
        password_env="NOBIA_KANDA_PASSWORD",
    ),
    "nobia_nihonbashi": Site(
        id="nobia_nihonbashi",
        name="ノビア日本橋",
        login_url_env="NOBIA_NIHONBASHI_LOGIN_URL",
        username_env="NOBIA_NIHONBASHI_USERNAME",
        password_env="NOBIA_NIHONBASHI_PASSWORD",
    ),
    "nobia_azabu": Site(
        id="nobia_azabu",
        name="ノビア麻布十番",
        login_url_env="NOBIA_AZABU_LOGIN_URL",
        username_env="NOBIA_AZABU_USERNAME",
        password_env="NOBIA_AZABU_PASSWORD",
    ),
    "nobia_omori": Site(
        id="nobia_omori",
        name="ノビア大森",
        login_url_env="NOBIA_OMORI_LOGIN_URL",
        username_env="NOBIA_OMORI_USERNAME",
        password_env="NOBIA_OMORI_PASSWORD",
    ),
    "cubell_tamachi": Site(
        id="cubell_tamachi",
        name="キューベル田町",
        login_url_env="CUBELL_TAMACHI_LOGIN_URL",
        username_env="CUBELL_TAMACHI_USERNAME",
        password_env="CUBELL_TAMACHI_PASSWORD",
    ),
    "cubell_hatchobori": Site(
        id="cubell_hatchobori",
        name="キューベル八丁堀",
        login_url_env="CUBELL_HATCHOBORI_LOGIN_URL",
        username_env="CUBELL_HATCHOBORI_USERNAME",
        password_env="CUBELL_HATCHOBORI_PASSWORD",
    ),
}

# 神田・日本橋: 同じエリア扱い（同時にポチ、枠も共通）。
# キューベル田町・八丁堀: カレンダーは共有だが、ポチの実行・枠は別々。
POKE_UNITS: tuple[PokeUnit, ...] = (
    PokeUnit(
        id="kanda_nihonbashi",
        label="神田・日本橋",
        sites=("nobia_kanda", "nobia_nihonbashi"),
        calendar_ids_env=("NOBIA_KANDA_CALENDAR_ID", "NOBIA_NIHONBASHI_CALENDAR_ID"),
    ),
    PokeUnit(
        id="azabu",
        label="麻布十番",
        sites=("nobia_azabu",),
        calendar_ids_env=("NOBIA_AZABU_CALENDAR_ID",),
    ),
    PokeUnit(
        id="omori",
        label="大森",
        sites=("nobia_omori",),
        calendar_ids_env=("NOBIA_OMORI_CALENDAR_ID",),
    ),
    PokeUnit(
        id="tamachi",
        label="田町",
        sites=("cubell_tamachi",),
        calendar_ids_env=("CUBELL_SHARED_CALENDAR_ID",),
    ),
    PokeUnit(
        id="hatchobori",
        label="八丁堀",
        sites=("cubell_hatchobori",),
        calendar_ids_env=("CUBELL_SHARED_CALENDAR_ID",),
    ),
)

# 実行環境の設定
CHECK_INTERVAL_MINUTES = 3  # 2〜3分おきにチェック
STATE_FILE_PATH_ENV = "ESTHE_POKE_STATE_FILE"  # 未設定ならデフォルトパスを使う

LINE_CHANNEL_ACCESS_TOKEN_ENV = "LINE_CHANNEL_ACCESS_TOKEN"
LINE_TARGET_ID_ENV = "LINE_TARGET_ID"  # 通知先のユーザーID or グループID
