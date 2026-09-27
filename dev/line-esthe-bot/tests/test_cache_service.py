import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.models import Base
from app.services import cache_service


@pytest.fixture(autouse=True)
async def in_memory_db(monkeypatch):
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(cache_service, "get_session_factory", lambda: session_factory)
    yield
    await engine.dispose()


@pytest.mark.asyncio
async def test_cache_miss_returns_none():
    result = await cache_service.get_cached_message("ABC新宿", "あい")
    assert result is None


@pytest.mark.asyncio
async def test_cache_hit_returns_saved_message():
    await cache_service.save_cache("ABC新宿", "あい", "こんな感じ！", review_count=2)
    result = await cache_service.get_cached_message("ABC新宿", "あい")
    assert result == "こんな感じ！"


@pytest.mark.asyncio
async def test_cache_does_not_leak_across_therapists():
    await cache_service.save_cache("ABC新宿", "あい", "あいの結果", review_count=2)
    result = await cache_service.get_cached_message("ABC新宿", "ゆき")
    assert result is None


@pytest.mark.asyncio
async def test_expired_cache_not_returned(monkeypatch):
    settings = cache_service.get_settings()
    monkeypatch.setattr(settings, "cache_ttl_seconds", -1)
    await cache_service.save_cache("ABC新宿", "あい", "古い結果", review_count=2)
    result = await cache_service.get_cached_message("ABC新宿", "あい")
    assert result is None
