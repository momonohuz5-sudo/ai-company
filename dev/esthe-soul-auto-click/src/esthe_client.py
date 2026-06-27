import asyncio
import logging
from playwright.async_api import async_playwright

from src.config import (
    ESTHE_LOGIN_URL, ESTHE_ID, ESTHE_PASSWORD,
    ESTHE_URL_APPEAL, ESTHE_URL_REALTIME, AREAS,
)

logger = logging.getLogger(__name__)


class EstheClient:
    def __init__(self):
        self._pw = None
        self.browser = None
        self.page = None

    async def start(self):
        self._pw = await async_playwright().start()
        self.browser = await self._pw.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        await self._login()

    async def _login(self):
        await self.page.goto(ESTHE_LOGIN_URL)
        await self.page.wait_for_load_state("networkidle")

        # ID/パスワード入力（セレクタは実際のHTMLに合わせて調整が必要）
        await self.page.fill('input[type="text"]', ESTHE_ID)
        await self.page.fill('input[type="password"]', ESTHE_PASSWORD)
        await self.page.click('button[type="submit"], input[type="submit"]')
        await self.page.wait_for_load_state("networkidle")
        logger.info("エステ魂 ログイン完了")

    async def execute_pochi(self, area_key: str) -> bool:
        cfg = AREAS.get(area_key)
        if not cfg or not cfg.get("esthe_page_url"):
            logger.warning(f"{area_key}: URLが未設定")
            return False

        try:
            # ① ポチ（推しセラする）
            await self.page.goto(cfg["esthe_page_url"])
            await self.page.wait_for_load_state("networkidle")
            await self._click_pochi_buttons()

            # ② 集客ワンクリックアピール
            if ESTHE_URL_APPEAL:
                await self._click_appeal()

            # ③ リアルタイム集客
            if ESTHE_URL_REALTIME:
                await self._click_realtime()

            logger.info(f"{cfg['name']}: ポチ3点セット完了")
            return True

        except Exception as e:
            logger.error(f"{cfg['name']}: ポチエラー - {e}")
            return False

    async def _click_pochi_buttons(self):
        # まとめて推しセラする（0回消費ボタン）
        bulk = self.page.locator("button:has-text('まとめて推しセラする')")
        if await bulk.count() > 0 and await bulk.is_enabled():
            await bulk.click()
            await asyncio.sleep(0.8)

        # 個別の 推しセラする ボタン（チェックボックス付きセラピスト）
        btns = self.page.locator("button:has-text('推しセラする'), a:has-text('推しセラする')")
        count = await btns.count()
        for i in range(count):
            btn = btns.nth(i)
            if await btn.is_visible() and await btn.is_enabled():
                await btn.click()
                await asyncio.sleep(0.5)

    async def _click_appeal(self):
        await self.page.goto(ESTHE_URL_APPEAL)
        await self.page.wait_for_load_state("networkidle")
        # セレクタは実際のページに合わせて調整してください
        btn = self.page.locator("button:has-text('集客ワンクリックアピール'), button:has-text('アピール')")
        if await btn.count() > 0:
            await btn.first.click()
            await asyncio.sleep(0.5)

    async def _click_realtime(self):
        await self.page.goto(ESTHE_URL_REALTIME)
        await self.page.wait_for_load_state("networkidle")
        # セレクタは実際のページに合わせて調整してください
        btn = self.page.locator("button:has-text('リアルタイム集客'), button:has-text('リアルタイム')")
        if await btn.count() > 0:
            await btn.first.click()
            await asyncio.sleep(0.5)

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self._pw:
            await self._pw.stop()
