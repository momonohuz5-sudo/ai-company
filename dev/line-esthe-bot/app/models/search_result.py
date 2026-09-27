from dataclasses import dataclass, field

from app.models.review import Review


@dataclass
class SearchResult:
    shop_name: str
    therapist_name: str
    reviews: list[Review] = field(default_factory=list)

    @property
    def total_reviews(self) -> int:
        return len(self.reviews)

    @property
    def sources(self) -> list[str]:
        seen: list[str] = []
        for review in self.reviews:
            if review.source not in seen:
                seen.append(review.source)
        return seen
