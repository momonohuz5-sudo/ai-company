from playwright.async_api import async_playwright

from app.models.review import Review
from app.scrapers.base import ReviewScraper
from app.utils.logger import get_logger

logger = get_logger(__name__)

SEARCH_URL = "https://men-esthe.jp/"

# NOTE: These selectors are placeholders. men-esthe.jp's actual markup has
# not been inspected yet (no confirmed access/permission at implementation
# time per spec section 7). Verify and update against the real site before
# relying on this scraper for live results; until then it degrades to
# returning [] rather than raising, so it never breaks the overall search.
SEARCH_INPUT_SELECTOR = "input[type=search]"
RESULT_LINK_SELECTOR = "a.shop-result"
REVIEW_ITEM_SELECTOR = ".review-item"
REVIEW_TEXT_SELECTOR = ".review-text"
REVIEW_DATE_SELECTOR = ".review-date"


class MenEstheScraper(ReviewScraper):
    source = "men-esthe"

    async def search_reviews(
        self, shop_name: str, therapist_name: str
    ) -> list[Review]:
        try:
            return await self._search_reviews(shop_name, therapist_name)
        except Exception:
            logger.exception(
                "men-esthe scrape failed for shop=%s therapist=%s",
                shop_name,
                therapist_name,
            )
            return []

    async def _search_reviews(
        self, shop_name: str, therapist_name: str
    ) -> list[Review]:
        reviews: list[Review] = []
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.goto(SEARCH_URL)
                await page.fill(SEARCH_INPUT_SELECTOR, f"{shop_name} {therapist_name}")
                await page.keyboard.press("Enter")
                await page.wait_for_selector(RESULT_LINK_SELECTOR)
                await page.click(RESULT_LINK_SELECTOR)
                await page.wait_for_selector(REVIEW_ITEM_SELECTOR)

                items = await page.query_selector_all(REVIEW_ITEM_SELECTOR)
                for item in items:
                    text_el = await item.query_selector(REVIEW_TEXT_SELECTOR)
                    date_el = await item.query_selector(REVIEW_DATE_SELECTOR)
                    text = (await text_el.inner_text()).strip() if text_el else ""
                    if not text:
                        continue
                    date = (await date_el.inner_text()).strip() if date_el else None
                    reviews.append(
                        Review(
                            source=self.source,
                            shop_name=shop_name,
                            therapist_name=therapist_name,
                            text=text,
                            url=page.url,
                            date=date,
                        )
                    )
            finally:
                await browser.close()
        return reviews
