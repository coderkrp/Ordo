from pydantic_settings import BaseSettings, SettingsConfigDict
from ordo.adapters.base import IBrokerAdapter
from ordo.adapters.mock import MockAdapter


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    ORDO_API_TOKEN: str
    BROKER_ADAPTER: str = "mock"


settings = Settings()

def get_adapter() -> IBrokerAdapter:
    if settings.BROKER_ADAPTER == "mock":
        return MockAdapter()
    # Add other adapters here as they are implemented
    raise ValueError(f"Unknown adapter: {settings.BROKER_ADAPTER}")
