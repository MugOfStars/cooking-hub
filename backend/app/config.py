from pathlib import Path

from argon2 import extract_parameters
from argon2.exceptions import InvalidHashError
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# The single .env lives at the repo root so docker-compose and the backend share it.
# Real environment variables (e.g. in CI or production) take precedence over the file.
ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, extra="ignore")

    database_url: str

    # Auth is on by default, so a deployment is only open if it opts out explicitly.
    auth_enabled: bool = True
    auth_password_hash: str | None = None  # Argon2 hash from `python -m app.hash_password`
    session_secret: str | None = None  # signs the session cookie; rotate to log out everywhere
    cookie_secure: bool = True  # only send the cookie over HTTPS; false for local http dev

    @field_validator("database_url")
    @classmethod
    def use_psycopg_driver(cls, url: str) -> str:
        """Hosting providers (Neon, Fly, Heroku…) hand out plain postgres[ql]:// URLs.
        SQLAlchemy needs the driver named explicitly, or it would look for psycopg2."""
        for prefix in ("postgresql://", "postgres://"):
            if url.startswith(prefix):
                return "postgresql+psycopg://" + url.removeprefix(prefix)
        return url

    @model_validator(mode="after")
    def auth_configured_when_enabled(self) -> Settings:
        """Fail closed: with auth on but no way to check a password, refuse to start
        rather than run with a broken (or accidentally open) login."""
        if not self.auth_enabled:
            return self
        if not self.auth_password_hash:
            raise ValueError("AUTH_PASSWORD_HASH is required when AUTH_ENABLED is true")
        try:
            extract_parameters(self.auth_password_hash)
        except InvalidHashError:
            raise ValueError("AUTH_PASSWORD_HASH is not a valid Argon2 hash") from None
        if not self.session_secret or len(self.session_secret) < 32:
            raise ValueError("SESSION_SECRET of at least 32 characters is required")
        return self


settings = Settings()
