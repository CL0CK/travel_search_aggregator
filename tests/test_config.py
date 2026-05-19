import pytest

from app.core.config import Settings


def test_settings_no_db():
    settings = Settings()
    assert not settings.has_db


def test_settings_with_db():
    settings = Settings(database_url="postgresql+asyncpg://user:pass@host:5432/db")
    assert settings.has_db


def test_settings_has_db_empty():
    settings = Settings(database_url="")
    assert not settings.has_db


def test_settings_default_redis_url():
    settings = Settings()
    assert "redis" in settings.redis_url


def test_settings_default_cache_ttl():
    settings = Settings()
    assert settings.cache_ttl == 60


def test_settings_default_rate_limit():
    settings = Settings()
    assert settings.rate_limit_max_requests == 5
    assert settings.rate_limit_window_seconds == 30
