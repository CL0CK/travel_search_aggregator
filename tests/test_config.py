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
