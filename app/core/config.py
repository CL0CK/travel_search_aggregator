from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url = "postgresql+asyncpg://postgres:3030@127.0.0.1:5432/travel_aggregator?sslmode=disable"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()