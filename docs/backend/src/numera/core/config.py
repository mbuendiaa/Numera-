from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Numera"
    environment: str = "local"
    database_url: str = "sqlite:///./numera.db"


settings = Settings()
