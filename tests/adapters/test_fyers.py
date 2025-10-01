import pytest
import respx
from httpx import Response
from unittest.mock import MagicMock, patch, call

from ordo.adapters.base import IBrokerAdapter
from ordo.adapters.fyers import FyersAdapter
from ordo.models.api.errors import CSRFError


@pytest.fixture
def mock_session_manager():
    """Fixture to mock the SessionManager."""
    with patch("ordo.adapters.fyers.SessionManager") as mock_session_manager_class:
        mock_session_manager = MagicMock()
        mock_session_manager_class.return_value = mock_session_manager
        yield mock_session_manager


@pytest.mark.unit
def test_fyers_adapter_implements_interface():
    """
    Tests that FyersAdapter is a valid subclass of IBrokerAdapter.
    (Test 1.3-UNIT-001)
    """
    assert issubclass(FyersAdapter, IBrokerAdapter)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_initiate_login_constructs_correct_url(mock_session_manager):
    """
    Tests that initiate_login constructs the correct URL and saves the state.
    (Test 1.3-INT-001)
    """
    adapter = FyersAdapter()
    credentials = {
        "app_id": "test_app_id",
        "secret_id": "test_secret_id",
        "redirect_uri": "http://localhost:8000/callback",
    }
    result = await adapter.initiate_login(credentials)

    assert "login_url" in result
    assert adapter.base_url in result["login_url"]
    assert "test_app_id" in result["login_url"]
    assert "http://localhost:8000/callback" in result["login_url"]

    # Check that state was saved in the session
    mock_session_manager.set_session.assert_called_once()
    call_args = mock_session_manager.set_session.call_args[0]
    assert call_args[0] == "test_app_id"
    assert call_args[1] == "state"
    assert isinstance(call_args[2], str)


@pytest.mark.asyncio
@pytest.mark.integration
@respx.mock
async def test_complete_login_success(mock_session_manager):
    """
    Tests the success case for complete_login with the v3 API.
    (Test 1.3-INT-002)
    """
    adapter = FyersAdapter()
    url = f"{adapter.base_url}/validate-authcode"
    respx.post(url).mock(
        return_value=Response(
            200, json={"access_token": "test_token", "refresh_token": "test_refresh"}
        )
    )

    mock_session_manager.get_session.return_value = "test_state"

    session_data = {
        "auth_code": "test_auth_code",
        "credentials": {
            "app_id": "test_app_id",
            "secret_id": "test_secret_id",
            "redirect_uri": "http://localhost:8000/callback",
        },
        "response_state": "test_state",
    }

    result = await adapter.complete_login(session_data)
    assert result["access_token"] == "test_token"

    # Check that state was retrieved and tokens were saved
    mock_session_manager.get_session.assert_called_once_with("test_app_id", "state")
    mock_session_manager.set_session.assert_has_calls(
        [
            call("test_app_id", "access_token", "test_token"),
            call("test_app_id", "refresh_token", "test_refresh"),
        ],
        any_order=True,
    )


@pytest.mark.asyncio
@pytest.mark.integration
@respx.mock
async def test_refresh_access_token_success(mock_session_manager):
    """
    Tests the success case for refreshing an access token.
    """
    adapter = FyersAdapter()
    url = f"{adapter.base_url}/validate-refresh-token"
    respx.post(url).mock(
        return_value=Response(200, json={"access_token": "new_test_token"})
    )

    mock_session_manager.get_session.return_value = "test_refresh_token"

    session_data = {
        "credentials": {
            "app_id": "test_app_id",
            "secret_id": "test_secret_id",
            "redirect_uri": "http://localhost:8000/callback",
        }
    }

    result = await adapter.refresh_access_token(session_data, pin="1234")
    assert result["access_token"] == "new_test_token"

    # Check that refresh token was retrieved and new access token was saved
    mock_session_manager.get_session.assert_called_once_with(
        "test_app_id", "refresh_token"
    )
    mock_session_manager.set_session.assert_called_once_with(
        "test_app_id", "access_token", "new_test_token"
    )


@pytest.mark.asyncio
@pytest.mark.integration
@respx.mock
async def test_complete_login_api_error(mock_session_manager):
    """
    Tests that complete_login handles API errors.
    (Test 1.3-INT-003)
    """
    adapter = FyersAdapter()
    url = f"{adapter.base_url}/validate-authcode"
    respx.post(url).mock(
        return_value=Response(400, json={"message": "Invalid auth code"})
    )

    mock_session_manager.get_session.return_value = "test_state"

    session_data = {
        "auth_code": "invalid_code",
        "credentials": {
            "app_id": "test_app_id",
            "secret_id": "test_secret_id",
            "redirect_uri": "http://localhost:8000/callback",
        },
        "response_state": "test_state",
    }

    with pytest.raises(Exception):
        await adapter.complete_login(session_data)


@pytest.mark.asyncio
@pytest.mark.unit
@respx.mock
async def test_get_session_status_active(mock_session_manager):
    """
    Tests get_session_status when a session is active.
    (Test 1.3-UNIT-002)
    """
    adapter = FyersAdapter()
    mock_session_manager.get_session.return_value = "valid_token"
    profile_url = f"{adapter.base_url}/profile"
    respx.get(profile_url).mock(return_value=Response(200, json={"s": "ok"}))

    session_data = {
        "credentials": {
            "app_id": "test_app_id",
            "secret_id": "test_secret_id",
            "redirect_uri": "http://localhost:8000/callback",
        }
    }

    result = await adapter.get_session_status(session_data)
    assert result["status"] == "active"
    mock_session_manager.get_session.assert_called_once_with(
        "test_app_id", "access_token"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@respx.mock
async def test_get_session_status_inactive_no_token(mock_session_manager):
    """
    Tests get_session_status when there is no token in the session.
    (Test 1.3-UNIT-003)
    """
    adapter = FyersAdapter()
    mock_session_manager.get_session.return_value = None

    session_data = {
        "credentials": {
            "app_id": "test_app_id",
            "secret_id": "test_secret_id",
            "redirect_uri": "http://localhost:8000/callback",
        }
    }

    result = await adapter.get_session_status(session_data)
    assert result["status"] == "inactive"
    mock_session_manager.get_session.assert_called_once_with(
        "test_app_id", "access_token"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@respx.mock
async def test_get_session_status_inactive_api_error(mock_session_manager):
    """
    Tests get_session_status when the API returns an error.
    (Test 1.3-UNIT-004)
    """
    adapter = FyersAdapter()
    mock_session_manager.get_session.return_value = "invalid_token"
    profile_url = f"{adapter.base_url}/profile"
    respx.get(profile_url).mock(return_value=Response(401))

    session_data = {
        "credentials": {
            "app_id": "test_app_id",
            "secret_id": "test_secret_id",
            "redirect_uri": "http://localhost:8000/callback",
        }
    }

    result = await adapter.get_session_status(session_data)
    assert result["status"] == "inactive"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_complete_login_csrf_error(mock_session_manager):
    """
    Tests that complete_login raises an exception on state mismatch (CSRF).
    (Test 1.3-INT-004)
    """
    adapter = FyersAdapter()
    mock_session_manager.get_session.return_value = "correct_state"

    session_data = {
        "auth_code": "test_auth_code",
        "credentials": {
            "app_id": "test_app_id",
            "secret_id": "test_secret_id",
            "redirect_uri": "http://localhost:8000/callback",
        },
        "response_state": "tampered_state",  # Mismatched state
    }

    with pytest.raises(CSRFError, match="Invalid state"):
        await adapter.complete_login(session_data)
