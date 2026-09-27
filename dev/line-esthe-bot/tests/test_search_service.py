import asyncio

import pytest

from app.models.review import Review
from app.scrapers.base import ReviewScraper
from app.services import search_service


@pytest.fixture(autouse=True)
def reset_scrape_semaphore(monkeypatch):
    monkeypatch.setattr(search_service, "_scrape_semaphore", None)


class OkScraper(ReviewScraper):
    source = "ok-site"

    async def search_reviews(self, shop_name, therapist_name):
        return [
            Review(
                source=self.source,
                shop_name=shop_name,
                therapist_name=therapist_name,
                text="話しやすかった",
                url=None,
                date=None,
            )
        ]


class EmptyScraper(ReviewScraper):
    source = "empty-site"

    async def search_reviews(self, shop_name, therapist_name):
        return []


class SlowScraper(ReviewScraper):
    source = "slow-site"

    async def search_reviews(self, shop_name, therapist_name):
        await asyncio.sleep(10)
        return [
            Review(
                source=self.source,
                shop_name=shop_name,
                therapist_name=therapist_name,
                text="never arrives",
                url=None,
                date=None,
            )
        ]


class FailingScraper(ReviewScraper):
    source = "failing-site"

    async def search_reviews(self, shop_name, therapist_name):
        raise RuntimeError("site down")


@pytest.mark.asyncio
async def test_search_all_aggregates_results(monkeypatch):
    monkeypatch.setattr(
        search_service, "get_scrapers", lambda: [OkScraper(), EmptyScraper()]
    )
    result = await search_service.search_all("ABC新宿", "あい")
    assert result.total_reviews == 1
    assert result.sources == ["ok-site"]


@pytest.mark.asyncio
async def test_search_all_skips_timed_out_site(monkeypatch):
    settings = search_service.get_settings()
    monkeypatch.setattr(settings, "scraper_timeout_seconds", 0.05)
    monkeypatch.setattr(
        search_service, "get_scrapers", lambda: [OkScraper(), SlowScraper()]
    )
    result = await search_service.search_all("ABC新宿", "あい")
    assert result.total_reviews == 1
    assert result.sources == ["ok-site"]


@pytest.mark.asyncio
async def test_search_all_skips_failing_site(monkeypatch):
    monkeypatch.setattr(
        search_service, "get_scrapers", lambda: [OkScraper(), FailingScraper()]
    )
    result = await search_service.search_all("ABC新宿", "あい")
    assert result.total_reviews == 1


@pytest.mark.asyncio
async def test_search_all_returns_empty_when_nothing_found(monkeypatch):
    monkeypatch.setattr(search_service, "get_scrapers", lambda: [EmptyScraper()])
    result = await search_service.search_all("ABC新宿", "あい")
    assert result.total_reviews == 0


class DuplicateScraper(ReviewScraper):
    def __init__(self, source: str):
        self.source = source

    async def search_reviews(self, shop_name, therapist_name):
        return [
            Review(
                source=self.source,
                shop_name=shop_name,
                therapist_name=therapist_name,
                text="話しやすかった！",
                url=None,
                date=None,
            )
        ]


@pytest.mark.asyncio
async def test_search_all_dedups_across_sites(monkeypatch):
    monkeypatch.setattr(
        search_service,
        "get_scrapers",
        lambda: [DuplicateScraper("site-a"), DuplicateScraper("site-b")],
    )
    result = await search_service.search_all("ABC新宿", "あい")
    assert result.total_reviews == 1


class ConcurrencyTrackingScraper(ReviewScraper):
    source = "tracked-site"

    def __init__(self, tracker: "dict"):
        self.tracker = tracker

    async def search_reviews(self, shop_name, therapist_name):
        self.tracker["current"] += 1
        self.tracker["peak"] = max(self.tracker["peak"], self.tracker["current"])
        await asyncio.sleep(0.05)
        self.tracker["current"] -= 1
        return []


@pytest.mark.asyncio
async def test_concurrent_scrapes_are_capped_by_semaphore(monkeypatch):
    settings = search_service.get_settings()
    monkeypatch.setattr(settings, "max_concurrent_scrapes", 2)

    tracker = {"current": 0, "peak": 0}
    monkeypatch.setattr(
        search_service,
        "get_scrapers",
        lambda: [ConcurrencyTrackingScraper(tracker)],
    )

    await asyncio.gather(
        *(search_service.search_all("ABC新宿", "あい") for _ in range(5))
    )

    assert tracker["peak"] <= 2
