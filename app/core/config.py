from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = Field(default="127.0.0.1")
    db_port: int = Field(default=5432)
    db_name: str = Field(default="travel_aggregator")
    db_user: str = Field(default="postgres")
    db_password: str = Field(default="")
    redis_url: str = Field(default="redis://localhost:6379")
    cache_ttl: int = Field(default=60)
    rate_limit_max_requests: int = Field(default=5)
    rate_limit_window_seconds: int = Field(default=30)
    rapidapi_key: str = Field(default="")

    model_config = {
        "env_file": ".env",
    }

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()

