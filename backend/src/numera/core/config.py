from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = "sqlite:///./numera.db"
    upload_dir: str = "uploads"
    tesseract_cmd: str | None = None
    jwt_secret_key: str = "CHANGE-ME-IN-PRODUCTION-USE-32-CHARS-MIN"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def is_postgresql(self) -> bool:
        return self.database_url.startswith(("postgresql://", "postgresql+psycopg://"))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
