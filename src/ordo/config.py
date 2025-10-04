from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from ordo.adapters.base import IBrokerAdapter
from ordo.adapters.mock import MockAdapter


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    ORDO_API_TOKEN: str
    BROKER_ADAPTER: str = "mock"
    SECRET_KEY: str

    FYERS_APP_ID: Optional[str] = None
    FYERS_SECRET_ID: Optional[str] = None
    FYERS_REDIRECT_URI: Optional[str] = None

    HDFC_API_KEY: Optional[str] = None
    HDFC_USERNAME: Optional[str] = None
    HDFC_PASSWORD: Optional[str] = None
    HDFC_API_SECRET: Optional[str] = None


settings = Settings()


def get_adapter(broker: Optional[str] = None) -> IBrokerAdapter:
    adapter_name = broker or settings.BROKER_ADAPTER
    if adapter_name == "mock":
        return MockAdapter()
    if adapter_name == "fyers":
        from ordo.adapters.fyers import (
            FyersAdapter,
        )  # Local import to break circular dependency

        return FyersAdapter()
    if adapter_name == "hdfc":
        from ordo.adapters.hdfc import (
            HDFCAdapter,
        )  # Local import to break circular dependency

        return HDFCAdapter()
    # Add other adapters here as they are implemented
    raise ValueError(f"Unknown adapter: {adapter_name}")
