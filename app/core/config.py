from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = Field(default="127.0.0.1")
    db_port: int = Field(default=5432)
    db_name: str = Field(default="travel_aggregator")
    db_user: str = Field(default="postgres")
    db_password: str = Field(default="")

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()


def build_database_url() -> str:
    return f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"