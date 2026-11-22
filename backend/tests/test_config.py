import pytest

from app.config import Settings


@pytest.mark.parametrize(
    "given",
    [
        "postgresql://u:p@db.example.com/app?sslmode=require",
        "postgres://u:p@db.example.com/app?sslmode=require",
        "postgresql+psycopg://u:p@db.example.com/app?sslmode=require",
    ],
)
def test_database_url_always_uses_psycopg_driver(given):
    settings = Settings(database_url=given)
    assert settings.database_url == "postgresql+psycopg://u:p@db.example.com/app?sslmode=require"
