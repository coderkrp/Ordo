import pytest
import respx
from httpx import Response
from unittest.mock import MagicMock, patch, call

from ordo.adapters.base import IBrokerAdapter
from ordo.adapters.hdfc import HDFCAdapter, HDFCConfig
from ordo.models.api.errors import ApiException, ApiError


@pytest.fixture
def mock_session_manager():
    """Fixture to mock the SessionManager."""
    with patch("ordo.adapters.hdfc.SessionManager") as mock_session_manager_class:
        mock_session_manager = MagicMock()
        mock_session_manager_class.return_value = mock_session_manager
        yield mock_session_manager


@pytest.fixture
def hdfc_credentials():
    """Fixture for HDFC credentials."""
    return {
        "api_key": "test_api_key",
        "username": "test_username",
        "password": "test_password",
        "apiSecret": "test_api_secret",
    }


@pytest.mark.unit
def test_hdfc_adapter_implements_interface():
    """
    Tests that HDFCAdapter is a valid subclass of IBrokerAdapter.
    """
    assert issubclass(HDFCAdapter, IBrokerAdapter)


@pytest.mark.asyncio
@pytest.mark.integration
@respx.mock
async def test_initiate_login_success_no_2fa(mock_session_manager, hdfc_credentials):
    """
    Tests the success case for initiate_login when 2FA is not enabled.
    """
    adapter = HDFCAdapter()

    # Mock Step 1: Fetch tokenId
    respx.get(f"{adapter.base_url}/login?api_key={hdfc_credentials['api_key']}").mock(
        return_value=Response(200, json={"tokenId": "test_token_id"})
    )

    # Mock Step 2: Validate username and password (no 2FA)
    respx.post(
        f"{adapter.base_url}/login/validate?api_key={hdfc_credentials['api_key']}&token_id=test_token_id"
    ).mock(
        return_value=Response(
            200,
            json={
                "recaptcha": False,
                "loginId": "test_login_id",
                "twofa": {},
                "twoFAEnabled": False,
            },
        )
    )

    result = await adapter.initiate_login(hdfc_credentials)

    assert result["tokenId"] == "test_token_id"
    assert result["loginId"] == "test_login_id"
    assert result["twoFAEnabled"] is False
    assert "session_data" in result
    assert result["session_data"]["tokenId"] == "test_token_id"


@pytest.mark.asyncio
@pytest.mark.integration
@respx.mock
async def test_initiate_login_success_with_2fa(mock_session_manager, hdfc_credentials):
    """
    Tests the success case for initiate_login when 2FA is enabled.
    """
    adapter = HDFCAdapter()

    # Mock Step 1: Fetch tokenId
    respx.get(f"{adapter.base_url}/login?api_key={hdfc_credentials['api_key']}").mock(
        return_value=Response(200, json={"tokenId": "test_token_id"})
    )

    # Mock Step 2: Validate username and password (with 2FA)
    respx.post(
        f"{adapter.base_url}/login/validate?api_key={hdfc_credentials['api_key']}&token_id=test_token_id"
    ).mock(
        return_value=Response(
            200,
            json={
                "recaptcha": False,
                "loginId": "test_login_id",
                "twofa": {"questions": [{"question": "Enter OTP"}]},
                "twoFAEnabled": True,
            },
        )
    )

    result = await adapter.initiate_login(hdfc_credentials)

    assert result["tokenId"] == "test_token_id"
    assert result["loginId"] == "test_login_id"
    assert result["twoFAEnabled"] is True
    assert result["twofa"]["questions"][0]["question"] == "Enter OTP"
    assert "session_data" in result


@pytest.mark.asyncio
@pytest.mark.integration
@respx.mock
async def test_initiate_login_api_error(mock_session_manager, hdfc_credentials):
    """
    Tests that initiate_login handles API errors.
    """
    adapter = HDFCAdapter()

    # Mock Step 1: Fetch tokenId (API error)
    respx.get(f"{adapter.base_url}/login?api_key={hdfc_credentials['api_key']}").mock(
        return_value=Response(400, json={"message": "Invalid API Key"})
    )

    with pytest.raises(ApiException) as excinfo:
        await adapter.initiate_login(hdfc_credentials)

    assert excinfo.value.error.error_code == "BROKER_API_ERROR"
    assert "Invalid API Key" in excinfo.value.error.message


@pytest.mark.asyncio
@pytest.mark.integration
@respx.mock
async def test_complete_login_success_no_2fa(mock_session_manager, hdfc_credentials):
    """
    Tests the success case for complete_login when 2FA is not enabled.
    """
    adapter = HDFCAdapter()
    session_data = {
        "credentials": hdfc_credentials,
        "tokenId": "test_token_id",
        "loginId": "test_login_id",
        "twoFAEnabled": False,
    }

    # Mock Step 4: Authorize (assuming request_token is obtained from previous step or not needed)
    respx.get(
        f"{adapter.base_url}/authorise?api_key={hdfc_credentials['api_key']}&token_id=test_token_id&consent=true&request_token=None"
    ).mock(return_value=Response(200, json={"requestToken": "test_request_token"}))

    # Mock Step 5: Get accessToken
    respx.post(
        f"{adapter.base_url}/access-token?api_key={hdfc_credentials['api_key']}&request_token=test_request_token"
    ).mock(return_value=Response(200, json={"accessToken": "final_access_token"}))

    result = await adapter.complete_login(session_data, otp=None)

    assert result["access_token"] == "final_access_token"
    mock_session_manager.set_session.assert_called_once_with(
        hdfc_credentials["api_key"], "access_token", "final_access_token"
    )


@pytest.mark.asyncio
@pytest.mark.integration
@respx.mock
async def test_complete_login_success_with_2fa(mock_session_manager, hdfc_credentials):
    """
    Tests the success case for complete_login when 2FA is enabled and OTP is provided.
    """
    adapter = HDFCAdapter()
    session_data = {
        "credentials": hdfc_credentials,
        "tokenId": "test_token_id",
        "loginId": "test_login_id",
        "twoFAEnabled": True,
        "otp": "123456",
    }

    # Mock Step 3: Validate 2FA OTP
    respx.post(
        f"{adapter.base_url}/twofa/validate?api_key={hdfc_credentials['api_key']}&token_id=test_token_id"
    ).mock(return_value=Response(200, json={"requestToken": "2fa_request_token"}))

    # Mock Step 4: Authorize
    respx.get(
        f"{adapter.base_url}/authorise?api_key={hdfc_credentials['api_key']}&token_id=test_token_id&consent=true&request_token=2fa_request_token"
    ).mock(return_value=Response(200, json={"requestToken": "final_request_token"}))

    # Mock Step 5: Get accessToken
    respx.post(
        f"{adapter.base_url}/access-token?api_key={hdfc_credentials['api_key']}&request_token=final_request_token"
    ).mock(return_value=Response(200, json={"accessToken": "final_access_token"}))

    result = await adapter.complete_login(session_data, otp="123456")

    assert result["access_token"] == "final_access_token"
    mock_session_manager.set_session.assert_called_once_with(
        hdfc_credentials["api_key"], "access_token", "final_access_token"
    )


@pytest.mark.asyncio
@pytest.mark.integration
@respx.mock
async def test_complete_login_api_error(mock_session_manager, hdfc_credentials):
    """
    Tests that complete_login handles API errors during any step.
    """
    adapter = HDFCAdapter()
    session_data = {
        "credentials": hdfc_credentials,
        "tokenId": "test_token_id",
        "loginId": "test_login_id",
        "twoFAEnabled": True,
        "otp": "123456",
    }

    # Mock Step 3: Validate 2FA OTP (API error)
    respx.post(
        f"{adapter.base_url}/twofa/validate?api_key={hdfc_credentials['api_key']}&token_id=test_token_id"
    ).mock(return_value=Response(400, json={"message": "Invalid OTP"}))

    with pytest.raises(ApiException) as excinfo:
        await adapter.complete_login(session_data, otp="123456")

    assert excinfo.value.error.error_code == "BROKER_API_ERROR"
    assert "Invalid OTP" in excinfo.value.error.message


@pytest.mark.asyncio
@pytest.mark.integration
async def test_complete_login_missing_otp_with_2fa_enabled(
    mock_session_manager, hdfc_credentials
):
    """
    Tests that complete_login raises an error if 2FA is enabled but no OTP is provided.
    """
    adapter = HDFCAdapter()
    session_data = {
        "credentials": hdfc_credentials,
        "tokenId": "test_token_id",
        "loginId": "test_login_id",
        "twoFAEnabled": True,
        # "otp": "123456", # OTP is missing
    }

    # No API calls should be made if OTP is missing when 2FA is enabled
    with pytest.raises(ApiException) as excinfo:
        await adapter.complete_login(session_data, otp=None)

    assert excinfo.value.error.error_code == "BROKER_REQUEST_FAILED"

@pytest.mark.asyncio
@pytest.mark.integration
@respx.mock
async def test_get_portfolio_success(mock_session_manager, hdfc_credentials):
    """
    Tests the success case for get_portfolio.
    """
    adapter = HDFCAdapter()
    holdings_url = f"{adapter.base_url}/holdings"
    portfolio_url = f"{adapter.base_url}/portfolio"

    mock_session_manager.get_session.return_value = "test_access_token"

    holdings_response_data = {
        "holdings": [
            {
                "isin": "INE000A01025",
                "symbol": "HDFC",
                "quantity": 10,
                "averagePrice": 1500.0,
                "currentPrice": 1600.0,
                "totalValue": 16000.0,
                "profitLoss": 1000.0,
            }
        ]
    }

    portfolio_summary_response_data = {
        "availableBalance": 50000.0,
        "marginUsed": 10000.0,
        "totalBalance": 60000.0,
        "overallProfitLoss": 1000.0,
        "overallValue": 16000.0,
    }

    respx.get(holdings_url).mock(return_value=Response(200, json=holdings_response_data))
    respx.get(portfolio_url).mock(return_value=Response(200, json=portfolio_summary_response_data))

    session_data = {
        "credentials": hdfc_credentials,
        "tokenId": "test_token_id",
        "loginId": "test_login_id",
        "twoFAEnabled": False,
    }

    result = await adapter.get_portfolio(session_data)

    assert result["total_pnl"] == 1000.0
    assert result["total_value"] == 16000.0
    assert result["funds"]["available_balance"] == 50000.0
    assert result["funds"]["margin_used"] == 10000.0
    assert result["funds"]["total_balance"] == 60000.0
    assert len(result["holdings"]) == 1
    assert result["holdings"][0]["symbol"] == "HDFC"
    assert result["holdings"][0]["quantity"] == 10
    assert result["holdings"][0]["ltp"] == 1600.0
    assert result["holdings"][0]["avg_price"] == 1500.0
    assert result["holdings"][0]["pnl"] == 1000.0
    assert result["holdings"][0]["value"] == 16000.0

@pytest.mark.asyncio
@pytest.mark.integration
@respx.mock
async def test_get_portfolio_api_error(mock_session_manager, hdfc_credentials):
    """
    Tests that get_portfolio handles API errors.
    """
    adapter = HDFCAdapter()
    holdings_url = f"{adapter.base_url}/holdings"

    mock_session_manager.get_session.return_value = "test_access_token"

    respx.get(holdings_url).mock(return_value=Response(400, json={"message": "Invalid request"}))

    session_data = {
        "credentials": hdfc_credentials,
        "tokenId": "test_token_id",
        "loginId": "test_login_id",
        "twoFAEnabled": False,
    }

    with pytest.raises(ApiException) as excinfo:
        await adapter.get_portfolio(session_data)

    assert excinfo.value.error.error_code == "BROKER_API_ERROR"
    assert "Invalid request" in excinfo.value.error.message

