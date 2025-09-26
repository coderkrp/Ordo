import pytest
from ordo.config import get_adapter, settings
from ordo.adapters.mock import MockAdapter


def test_get_adapter_mock(monkeypatch):
    monkeypatch.setattr(settings, "BROKER_ADAPTER", "mock")
    adapter = get_adapter()
    assert isinstance(adapter, MockAdapter)


def test_get_adapter_unknown(monkeypatch):
    monkeypatch.setattr(settings, "BROKER_ADAPTER", "unknown")
    with pytest.raises(ValueError):
        get_adapter()
