import httpx
import asyncio
from typer.testing import CliRunner

from scripts.otp_cli import app, ORDO_API_BASE_URL, login

runner = CliRunner()


def test_app_exists():
    """Verify that the Typer app instance exists."""
    assert app is not None


def test_login_command_exists():
    """Verify that the 'login' command is registered with the app."""
    # This test still uses CliRunner as it's a basic command existence check
    result = runner.invoke(app, ["--help"])
    assert "login" in result.stdout


def test_login_command_broker_option(mocker):
    """Verify that the 'login' command has a '--broker' option and handles API calls."""
    # Mock initiate_login_api
    mock_initiate_login = mocker.patch("scripts.otp_cli.initiate_login_api")
    mock_initiate_login.return_value = {
        "login_url": "http://example.com/login",
        "session_data": {"state": "test_state"},
    }

    # Mock complete_login_api
    mock_complete_login = mocker.patch("scripts.otp_cli.complete_login_api")
    mock_complete_login.return_value = {
        "message": "Login successful",
        "access_token": "test_token",
    }

    # Mock typer.echo and typer.prompt
    mock_echo = mocker.patch("typer.echo")
    mock_prompt = mocker.patch(
        "typer.prompt",
        return_value="http://localhost:8000/callback?auth_code=test_auth_code&state=test_state",
    )

    # Mock asyncio.run to directly await the coroutine
    mock_asyncio_run = mocker.patch("asyncio.run")
    mock_asyncio_run.side_effect = (
        lambda coro: asyncio.get_event_loop().run_until_complete(coro)
    )

    login(
        broker="fyers",
        app_id="test_app_id",
        secret_id="test_secret_id",
        redirect_uri="http://localhost:8000/callback",
    )

    # Assertions
    mock_initiate_login.assert_called_once_with(
        "fyers",
        {
            "app_id": "test_app_id",
            "secret_id": "test_secret_id",
            "redirect_uri": "http://localhost:8000/callback",
        },
    )
    mock_echo.assert_any_call("Initiating login for broker: fyers")
    mock_echo.assert_any_call("Login initiated. Please visit: http://example.com/login")
    mock_echo.assert_any_call(
        "After logging in with Fyers, you will be redirected to a URL. Please paste the full URL here."
    )
    mock_prompt.assert_called_once_with("Enter the full redirect URL")
    mock_complete_login.assert_called_once_with(
        "fyers",
        {"state": "test_state"},
        "test_auth_code",
        "test_state",
    )
    mock_echo.assert_any_call("Login complete: Login successful")
    mock_echo.assert_any_call("Access Token: test_token")


def test_login_command_api_error(mocker):
    """Verify that the 'login' command handles API errors gracefully."""
    # Mock initiate_login_api to return an error
    mock_initiate_login = mocker.patch("scripts.otp_cli.initiate_login_api")
    mock_initiate_login.side_effect = httpx.HTTPStatusError(
        message="Client Error",
        request=httpx.Request("POST", f"{ORDO_API_BASE_URL}/login/initiate"),
        response=httpx.Response(400, json={"detail": "Invalid broker"}),
    )

    # Mock typer.echo and typer.prompt
    mock_echo = mocker.patch("typer.echo")
    mock_prompt = mocker.patch("typer.prompt")

    # Mock asyncio.run to directly await the coroutine
    mock_asyncio_run = mocker.patch("asyncio.run")
    mock_asyncio_run.side_effect = (
        lambda coro: asyncio.get_event_loop().run_until_complete(coro)
    )

    login(broker="invalid_broker", app_id="test", secret_id="test", redirect_uri="test")

    # Assertions
    mock_echo.assert_any_call("Initiating login for broker: invalid_broker")
    mock_echo.assert_any_call('API Error: 400 - {"detail":"Invalid broker"}')
    mock_echo.assert_any_call("Details: Invalid broker")
    # prompt should not be called if initiate login fails
    mock_prompt.assert_not_called()
