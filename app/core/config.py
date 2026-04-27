from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/travel_aggregator"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()