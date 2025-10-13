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
    broker: str, session_data: Dict[str, Any], auth_code: Optional[str] = None, response_state: Optional[str] = None
) -> Dict[str, Any]:
    """Completes login with the Ordo API."""
    async with httpx.AsyncClient() as client:
        request_body = {
            "broker": broker,
            "session_data": session_data,
        }
        if auth_code is not None:
            request_body["auth_code"] = auth_code
        if response_state is not None:
            request_body["response_state"] = response_state
        
        response = await client.post(
            f"{ORDO_API_BASE_URL}/login/complete",
            json=request_body,
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
    api_key: Optional[str] = typer.Option(None, help="HDFC API Key"),
    username: Optional[str] = typer.Option(None, help="HDFC Username"),
    password: Optional[str] = typer.Option(None, help="HDFC Password"),
    api_secret: Optional[str] = typer.Option(None, help="HDFC API Secret"),
):
    """
    Initiates the login process for a specified broker and handles OTP entry.
    """

    async def run_login():
        typer.echo(f"Initiating login for broker: {broker}")

        # Build credentials based on broker type
        credentials = {}
        
        if broker == "fyers":
            # Prioritize CLI arguments, then .env settings
            fyers_app_id = app_id or settings.FYERS_APP_ID
            fyers_secret_id = secret_id or settings.FYERS_SECRET_ID
            fyers_redirect_uri = redirect_uri or settings.FYERS_REDIRECT_URI
            
            # Validate all three required
            missing_fields = []
            if not fyers_app_id:
                missing_fields.append("app_id")
            if not fyers_secret_id:
                missing_fields.append("secret_id")
            if not fyers_redirect_uri:
                missing_fields.append("redirect_uri")
            
            if missing_fields:
                typer.echo(
                    f"Missing required Fyers credentials: {', '.join(missing_fields)}. Provide via CLI options or .env file."
                )
                raise typer.Exit(code=1)
            
            credentials = {
                "app_id": fyers_app_id,
                "secret_id": fyers_secret_id,
                "redirect_uri": fyers_redirect_uri
            }
        
        elif broker == "hdfc":
            # Prioritize CLI arguments, then .env settings
            hdfc_api_key = api_key or settings.HDFC_API_KEY
            hdfc_username = username or settings.HDFC_USERNAME
            hdfc_password = password or settings.HDFC_PASSWORD
            hdfc_api_secret = api_secret or settings.HDFC_API_SECRET
            
            # Validate all four required
            missing_fields = []
            if not hdfc_api_key:
                missing_fields.append("api_key")
            if not hdfc_username:
                missing_fields.append("username")
            if not hdfc_password:
                missing_fields.append("password")
            if not hdfc_api_secret:
                missing_fields.append("api_secret")
            
            if missing_fields:
                typer.echo(
                    f"Missing required HDFC credentials: {', '.join(missing_fields)}. Provide via CLI options or .env file."
                )
                raise typer.Exit(code=1)
            
            credentials = {
                "api_key": hdfc_api_key,
                "username": hdfc_username,
                "password": hdfc_password,
                "apiSecret": hdfc_api_secret
            }
        
        elif broker == "mock":
            # No credentials needed for mock broker
            credentials = {}
        
        else:
            # Unknown broker - warn but let server validate
            typer.echo(f"Warning: broker '{broker}' not recognized locally; letting server validate.")
            credentials = {}

        try:
            # Step 1: Initiate login
            initiate_response = await initiate_login_api(broker, credentials)
            session_data = initiate_response.get("session_data", {})

            # Step 2: Broker-specific interaction patterns
            if broker == "fyers":
                login_url = initiate_response.get("login_url", "N/A")
                typer.echo(f"Login initiated. Please visit: {login_url}")
                typer.echo("After logging in with Fyers, you will be redirected to a URL. Please paste the full URL here.")
                redirect_url_from_user = typer.prompt("Enter the full redirect URL")
                
                # Parse the URL to get auth_code and state
                parsed_data = await parse_redirect_url(redirect_url_from_user)
                auth_code = parsed_data["auth_code"]
                response_state = parsed_data["response_state"]
                
                # Complete login with OAuth parameters
                complete_response = await complete_login_api(
                    broker, session_data, auth_code, response_state
                )
            
            elif broker == "hdfc":
                typer.echo("Credentials validated. Please enter OTP sent to your registered device.")
                otp = typer.prompt("Enter OTP")
                session_data["otp"] = otp
                
                # Complete login with OTP in session_data
                complete_response = await complete_login_api(
                    broker, session_data, None, None
                )
            
            elif broker == "mock":
                typer.echo("Mock authentication - no OTP required.")
                
                # Complete login immediately with no additional data
                complete_response = await complete_login_api(
                    broker, session_data, None, None
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
