from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./numera.db"
    upload_dir: str = "uploads"
    tesseract_cmd: str | None = None


settings = Settings()
