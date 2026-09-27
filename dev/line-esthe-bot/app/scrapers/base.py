from abc import ABC, abstractmethod

from app.models.review import Review


class ReviewScraper(ABC):
    """Common interface every site scraper implements (spec section 37).

    Adding a new site means adding one class here, not touching the bot core.
    """

    source: str

    @abstractmethod
    async def search_reviews(
        self, shop_name: str, therapist_name: str
    ) -> list[Review]:
        """Return reviews for shop_name/therapist_name, or [] if none found.

        Implementations must not raise for "no results" — only for genuine
        failures (network error, site unreachable), which callers time out
        and skip per spec section 29.
        """
        raise NotImplementedError
