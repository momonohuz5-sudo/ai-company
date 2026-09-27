from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.config import get_settings
from app.db.database import get_session_factory
from app.db.models import ReviewRecord, SearchCacheRecord
from app.models.review import Review


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def get_cached_message(shop_name: str, therapist_name: str) -> str | None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        stmt = (
            select(SearchCacheRecord)
            .where(
                SearchCacheRecord.shop_name == shop_name,
                SearchCacheRecord.therapist_name == therapist_name,
                SearchCacheRecord.expires_at > _now(),
            )
            .order_by(SearchCacheRecord.created_at.desc())
        )
        result = await session.execute(stmt)
        record = result.scalars().first()
        return record.summary if record else None


async def save_cache(
    shop_name: str, therapist_name: str, summary_message: str, review_count: int
) -> None:
    settings = get_settings()
    now = _now()
    session_factory = get_session_factory()
    async with session_factory() as session:
        session.add(
            SearchCacheRecord(
                shop_name=shop_name,
                therapist_name=therapist_name,
                summary=summary_message,
                review_count=review_count,
                created_at=now,
                expires_at=now + timedelta(seconds=settings.cache_ttl_seconds),
            )
        )
        await session.commit()


async def save_reviews(shop_name: str, therapist_name: str, reviews: list[Review]) -> None:
    """Persist raw review text/source for future audit/removal requests (spec 21, 34)."""
    now = _now()
    session_factory = get_session_factory()
    async with session_factory() as session:
        for review in reviews:
            session.add(
                ReviewRecord(
                    shop_name=shop_name,
                    therapist_name=therapist_name,
                    source=review.source,
                    source_url=review.url,
                    review_text=review.text,
                    review_date=review.date,
                    collected_at=now,
                )
            )
        await session.commit()
