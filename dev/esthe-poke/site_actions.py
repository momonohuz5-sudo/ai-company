"""管理画面へのログイン、および「リアルタイム集客(ポチ)」「集客ワンクリックアピール」の
クリックを行うモジュール。

TODO: 実際の管理画面URL・HTML構造が未共有のため、SELECTORS は仮のプレースホルダー。
URLと画面が分かり次第、サイトごとに以下を埋める:
  - login_url / username_selector / password_selector / submit_selector
  - realtime_button_selector (ポチ=リアルタイム集客ボタン)
  - appeal_button_selector (集客ワンクリックアピールボタン)

ログインID/パスワードは config.py で定義した環境変数から読む
(NOBIA_KANDA_USERNAME 等)。平文でコードに書かない。
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from playwright.sync_api import sync_playwright

from config import SITES


@dataclass(frozen=True)
class SiteSelectors:
    login_url: str
    username_selector: str
    password_selector: str
    submit_selector: str
    realtime_button_selector: str  # ポチ(リアルタイム集客)
    appeal_button_selector: str  # 集客ワンクリックアピール


# TODO: 各サイトのURL・セレクタが判明次第、ここを実値に差し替える。
SELECTORS: dict[str, SiteSelectors] = {
    site_id: SiteSelectors(
        login_url="TODO",
        username_selector="TODO",
        password_selector="TODO",
        submit_selector="TODO",
        realtime_button_selector="TODO",
        appeal_button_selector="TODO",
    )
    for site_id in SITES
}


def poke_site(site_id: str) -> None:
    """指定サイトにログインし、ポチ(リアルタイム集客)と集客ワンクリックアピールを
    セットでクリックする。"""
    site = SITES[site_id]
    selectors = SELECTORS[site_id]

    if selectors.login_url == "TODO":
        raise NotImplementedError(
            f"{site.name} のログインURL/セレクタが未設定です。site_actions.SELECTORS を埋めてください。"
        )

    username = os.environ[site.username_env]
    password = os.environ[site.password_env]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(selectors.login_url)
        page.fill(selectors.username_selector, username)
        page.fill(selectors.password_selector, password)
        page.click(selectors.submit_selector)
        page.wait_for_load_state("networkidle")

        page.click(selectors.realtime_button_selector)
        page.click(selectors.appeal_button_selector)

        browser.close()
