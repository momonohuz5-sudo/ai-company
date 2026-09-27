import asyncio

from app.config import get_settings
from app.models.review import Review
from app.models.search_result import SearchResult
from app.scrapers.base import ReviewScraper
from app.scrapers.men_esthe import MenEstheScraper
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_scrapers() -> list[ReviewScraper]:
    return [MenEstheScraper()]


async def _search_one(
    scraper: ReviewScraper, shop_name: str, therapist_name: str, timeout: int
) -> list[Review]:
    try:
        return await asyncio.wait_for(
            scraper.search_reviews(shop_name, therapist_name), timeout=timeout
        )
    except TimeoutError:
        logger.warning("scraper %s timed out after %ss", scraper.source, timeout)
        return []
    except Exception:
        logger.exception("scraper %s raised unexpectedly", scraper.source)
        return []


async def search_all(shop_name: str, therapist_name: str) -> SearchResult:
    settings = get_settings()
    scrapers = get_scrapers()

    results = await asyncio.gather(
        *(
            _search_one(scraper, shop_name, therapist_name, settings.scraper_timeout_seconds)
            for scraper in scrapers
        )
    )

    reviews = [review for site_reviews in results for review in site_reviews]
    return SearchResult(
        shop_name=shop_name, therapist_name=therapist_name, reviews=reviews
    )
