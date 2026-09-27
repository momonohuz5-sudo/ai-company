from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SearchCacheRecord(Base):
    """Spec section 21: search_cache table."""

    __tablename__ = "search_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_name: Mapped[str] = mapped_column(String, index=True)
    therapist_name: Mapped[str] = mapped_column(String, index=True)
    summary: Mapped[str] = mapped_column(Text)
    review_count: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)


class ReviewRecord(Base):
    """Spec section 21: reviews table (internal only, never shown to users)."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_name: Mapped[str] = mapped_column(String, index=True)
    therapist_name: Mapped[str] = mapped_column(String, index=True)
    source: Mapped[str] = mapped_column(String)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    review_text: Mapped[str] = mapped_column(Text)
    review_date: Mapped[str | None] = mapped_column(String, nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime)
