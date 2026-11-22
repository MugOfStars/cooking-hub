from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The single .env lives at the repo root so docker-compose and the backend share it.
# Real environment variables (e.g. in CI or production) take precedence over the file.
ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, extra="ignore")

    database_url: str


settings = Settings()
