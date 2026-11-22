from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# The single .env lives at the repo root so docker-compose and the backend share it.
# Real environment variables (e.g. in CI or production) take precedence over the file.
ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, extra="ignore")

    database_url: str

    @field_validator("database_url")
    @classmethod
    def use_psycopg_driver(cls, url: str) -> str:
        """Hosting providers (Neon, Fly, Heroku…) hand out plain postgres[ql]:// URLs.
        SQLAlchemy needs the driver named explicitly, or it would look for psycopg2."""
        for prefix in ("postgresql://", "postgres://"):
            if url.startswith(prefix):
                return "postgresql+psycopg://" + url.removeprefix(prefix)
        return url


settings = Settings()
