import asyncio
import typer
import httpx
import urllib.parse
from typing import Dict, Any, Optional

from ordo.config import settings

app = typer.Typer()

ORDO_API_BASE_URL = "http://localhost:8000"  # Placeholder for Ordo API base URL


async def initiate_login_api(
    broker: str, credentials: Dict[str, Any]
) -> Dict[str, Any]:
    """Initiates login with the Ordo API."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ORDO_API_BASE_URL}/login/initiate",
            json={"broker": broker, "credentials": credentials},
        )
        response.raise_for_status()
        return response.json()


async def complete_login_api(
    broker: str, session_data: Dict[str, Any], auth_code: str, response_state: str
) -> Dict[str, Any]:
    """Completes login with the Ordo API."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ORDO_API_BASE_URL}/login/complete",
            json={
                "broker": broker,
                "session_data": session_data,
                "auth_code": auth_code,
                "response_state": response_state,
            },
        )
        response.raise_for_status()
        return response.json()


async def parse_redirect_url(redirect_url: str) -> Dict[str, str]:
    """Parses the redirect URL to extract auth_code and state."""
    try:
        parsed_url = urllib.parse.urlparse(redirect_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        auth_code = query_params.get("auth_code", [None])[0]
        response_state = query_params.get("state", [None])[0]

        if not auth_code or not response_state:
            raise ValueError(
                "Could not find 'auth_code' or 'state' in the provided URL."
            )
        return {"auth_code": auth_code, "response_state": response_state}
    except Exception as e:
        raise ValueError(f"Error parsing the URL: {e}")


@app.command()
def login(
    broker: str = typer.Option(..., help="The broker to log into"),
    app_id: Optional[str] = typer.Option(None, help="Fyers API App ID"),
    secret_id: Optional[str] = typer.Option(None, help="Fyers API Secret ID"),
    redirect_uri: Optional[str] = typer.Option(None, help="Fyers API Redirect URI"),
):
    """
    Initiates the login process for a specified broker and handles OTP entry.
    """

    async def run_login():
        typer.echo(f"Initiating login for broker: {broker}")

        # Prioritize CLI arguments, then .env settings
        fyers_app_id = app_id or settings.FYERS_APP_ID
        fyers_secret_id = secret_id or settings.FYERS_SECRET_ID
        fyers_redirect_uri = redirect_uri or settings.FYERS_REDIRECT_URI

        credentials = {}
        if broker == "fyers":
            if not fyers_app_id:
                typer.echo(
                    "Error: Fyers App ID is required. Provide via --app-id or FYERS_APP_ID in .env"
                )
                raise typer.Exit(code=1)
            if not fyers_secret_id:
                typer.echo(
                    "Error: Fyers Secret ID is required. Provide via --secret-id or FYERS_SECRET_ID in .env"
                )
                raise typer.Exit(code=1)
            if not fyers_redirect_uri:
                typer.echo(
                    "Error: Fyers Redirect URI is required. Provide via --redirect-uri or FYERS_REDIRECT_URI in .env"
                )
                raise typer.Exit(code=1)

            credentials["app_id"] = fyers_app_id
            credentials["secret_id"] = fyers_secret_id
            credentials["redirect_uri"] = fyers_redirect_uri

        try:
            # Step 1: Initiate login
            initiate_response = await initiate_login_api(broker, credentials)
            login_url = initiate_response.get("login_url", "N/A")
            session_data = initiate_response.get("session_data", {})

            typer.echo(f"Login initiated. Please visit: {login_url}")

            # Step 2: Prompt for the full redirect URL
            typer.echo(
                "After logging in with Fyers, you will be redirected to a URL. Please paste the full URL here."
            )
            redirect_url_from_user = typer.prompt("Enter the full redirect URL")

            # Step 3: Parse the URL to get auth_code and state
            parsed_data = await parse_redirect_url(redirect_url_from_user)
            auth_code = parsed_data["auth_code"]
            response_state = parsed_data["response_state"]

            # Step 4: Complete login
            complete_response = await complete_login_api(
                broker, session_data, auth_code, response_state
            )
            access_token = complete_response.get("access_token")

            typer.echo(f"Login complete: {complete_response.get('message', 'Success')}")
            if access_token:
                typer.echo(f"Access Token: {access_token}")

        except ValueError as e:
            typer.echo(f"Error: {e}")
            raise typer.Exit(code=1)
        except httpx.HTTPStatusError as e:
            typer.echo(f"API Error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 400:
                try:
                    typer.echo(
                        f"Details: {e.response.json().get('detail', 'No details provided.')}"
                    )
                except Exception:
                    typer.echo("Could not parse error details from JSON.")
        except httpx.RequestError as e:
            typer.echo(f"Network Error: {e}")
        except Exception as e:
            typer.echo(f"An unexpected error occurred: {e}")

    asyncio.run(run_login())


if __name__ == "__main__":
    app()
