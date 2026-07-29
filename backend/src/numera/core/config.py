from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./numera.db"
    upload_dir: str = "uploads"
    tesseract_cmd: str | None = None
    jwt_secret_key: str = "CHANGE-ME-IN-PRODUCTION-USE-32-CHARS-MIN"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


settings = Settings()
