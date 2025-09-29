"""Tests for the SessionManager."""

import pytest
from unittest.mock import patch
from cryptography.fernet import Fernet

from ordo.security.session import SessionManager

# Generate a key for testing
TEST_SECRET_KEY = Fernet.generate_key().decode()


@pytest.fixture
def mock_settings():
    """Fixture to mock the settings."""
    with patch("ordo.security.session.settings") as mock_settings:
        mock_settings.SECRET_KEY = TEST_SECRET_KEY
        yield mock_settings


def test_session_manager_init(mock_settings):
    """Test that the SessionManager initializes correctly."""
    manager = SessionManager()
    assert manager._fernet is not None


def test_session_manager_init_no_key():
    """Test that SessionManager raises an error if SECRET_KEY is not set."""
    with patch("ordo.security.session.settings") as mock_settings:
        mock_settings.SECRET_KEY = None
        with pytest.raises(
            ValueError, match="SECRET_KEY must be set for session management."
        ):
            SessionManager()


def test_set_and_get_session(mock_settings):
    """Test setting and getting a session value."""
    manager = SessionManager()
    broker_id = "fyers"
    key = "access_token"
    value = "my_secret_token"

    manager.set_session(broker_id, key, value)
    retrieved_value = manager.get_session(broker_id, key)

    assert retrieved_value == value


def test_get_session_non_existent(mock_settings):
    """Test getting a non-existent session value."""
    manager = SessionManager()
    broker_id = "fyers"
    key = "non_existent_key"

    retrieved_value = manager.get_session(broker_id, key)

    assert retrieved_value is None


def test_session_namespacing(mock_settings):
    """Test that session keys are namespaced by broker_id."""
    manager = SessionManager()
    broker_id_1 = "fyers"
    broker_id_2 = "zerodha"
    key = "access_token"
    value_1 = "fyers_token"
    value_2 = "zerodha_token"

    manager.set_session(broker_id_1, key, value_1)
    manager.set_session(broker_id_2, key, value_2)

    retrieved_value_1 = manager.get_session(broker_id_1, key)
    retrieved_value_2 = manager.get_session(broker_id_2, key)

    assert retrieved_value_1 == value_1
    assert retrieved_value_2 == value_2
    assert retrieved_value_1 != retrieved_value_2
