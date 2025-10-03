import hashlib
import uuid
from typing import Any, Dict

import httpx
from pydantic import BaseModel, ValidationError

from ordo.adapters.base import IBrokerAdapter
from ordo.models.api.errors import ApiError, ApiException, CSRFError
from ordo.models.api.portfolio import Portfolio, Holding, Funds
from ordo.security.session import SessionManager
from ordo.config import settings


class FyersConfig(BaseModel):
    """
    Pydantic model for Fyers API credentials.
    """

    app_id: str
    secret_id: str
    redirect_uri: str


class FyersAdapter(IBrokerAdapter):
    """
    Adapter for interacting with the Fyers API (v3).
    """

    def __init__(self):
        self.base_url = "https://api-t1.fyers.in/api/v3"
        self.session_manager = SessionManager(settings.SECRET_KEY)

    async def initiate_login(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates the Fyers login URL.
        """
        try:
            config = FyersConfig(**credentials)
        except ValidationError as e:
            raise ValueError(f"Missing or invalid Fyers credentials: {e}")

        state = uuid.uuid4().hex
        self.session_manager.set_session(config.app_id, "state", state)

        login_url = (
            f"{self.base_url}/generate-authcode?"
            f"client_id={config.app_id}&"
            f"redirect_uri={config.redirect_uri}&"
            f"response_type=code&"
            f"state={state}"
        )
        response = {
            "login_url": login_url,
            "session_data": {"credentials": credentials, "state": state},
        }
        return response

    async def complete_login(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exchanges the auth code for an access token.
        """
        auth_code = session_data["auth_code"]
        config = FyersConfig(**session_data["credentials"])

        state = self.session_manager.get_session(config.app_id, "state")

        # CSRF check
        if state != session_data["response_state"]:
            raise CSRFError("Invalid state")

        app_id_hash = hashlib.sha256(
            f"{config.app_id}:{config.secret_id}".encode()
        ).hexdigest()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/validate-authcode",
                json={
                    "grant_type": "authorization_code",
                    "appIdHash": app_id_hash,
                    "code": auth_code,
                },
            )
            response.raise_for_status()
            token_data = response.json()

        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        self.session_manager.set_session(config.app_id, "access_token", access_token)
        self.session_manager.set_session(config.app_id, "refresh_token", refresh_token)

        return {"access_token": access_token}

    async def refresh_access_token(
        self, session_data: Dict[str, Any], pin: str
    ) -> Dict[str, Any]:
        """
        Refreshes the access token using the refresh token and PIN.
        """
        config = FyersConfig(**session_data["credentials"])
        refresh_token = self.session_manager.get_session(config.app_id, "refresh_token")

        if not refresh_token:
            raise ValueError("No refresh token found in session.")

        app_id_hash = hashlib.sha256(
            f"{config.app_id}:{config.secret_id}".encode()
        ).hexdigest()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/validate-refresh-token",
                json={
                    "grant_type": "refresh_token",
                    "appIdHash": app_id_hash,
                    "refresh_token": refresh_token,
                    "pin": pin,
                },
            )
            response.raise_for_status()
            token_data = response.json()

        access_token = token_data["access_token"]
        self.session_manager.set_session(config.app_id, "access_token", access_token)

        return {"access_token": access_token}

    async def get_session_status(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Checks the validity of the current session by making a profile API call.
        """
        config = FyersConfig(**session_data["credentials"])
        access_token = self.session_manager.get_session(config.app_id, "access_token")

        if not access_token:
            return {"status": "inactive"}

        headers = {"Authorization": f"{config.app_id}:{access_token}"}
        profile_url = f"{self.base_url}/profile"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(profile_url, headers=headers)
                response.raise_for_status()
                response_data = response.json()
                if response_data.get("s") == "ok":
                    return {"status": "active"}
                else:
                    return {"status": "inactive"}
            except (httpx.HTTPStatusError, httpx.RequestError):
                return {"status": "inactive"}

    async def get_portfolio(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieves the portfolio from Fyers.
        """
        config = FyersConfig(**session_data["credentials"])
        access_token = self.session_manager.get_session(config.app_id, "access_token")

        if not access_token:
            raise ValueError("No access token found in session.")

        headers = {"Authorization": f"{config.app_id}:{access_token}"}
        holdings_url = f"{self.base_url}/holdings"
        funds_url = f"{self.base_url}/funds"

        async with httpx.AsyncClient() as client:
            try:
                holdings_response = await client.get(holdings_url, headers=headers)
                holdings_response.raise_for_status()
                holdings_data = holdings_response.json()
                if holdings_data.get("s") != "ok":
                    raise ApiException(
                        ApiError(
                            error_code="BROKER_API_ERROR",
                            message=f"Fyers holdings error: {holdings_data.get('message', 'Unknown error')}",
                            details={"response": holdings_data},
                        )
                    )

                funds_response = await client.get(funds_url, headers=headers)
                funds_response.raise_for_status()
                funds_data = funds_response.json()
                if funds_data.get("s") != "ok":
                    raise ApiException(
                        ApiError(
                            error_code="BROKER_API_ERROR",
                            message=f"Fyers funds error: {funds_data.get('message', 'Unknown error')}",
                            details={"response": funds_data},
                        )
                    )

            except httpx.HTTPStatusError as e:
                raise ApiException(
                    ApiError(
                        error_code="BROKER_API_ERROR",
                        message=f"Fyers API error: {e.response.text}",
                        details={"status_code": e.response.status_code},
                    )
                )
            except ApiException:
                raise
            except Exception as e:
                raise ApiException(
                    ApiError(
                        error_code="BROKER_REQUEST_FAILED",
                        message=f"Failed to retrieve portfolio from Fyers: {e}",
                    )
                )

        # Transform holdings
        holdings = [
            Holding(
                symbol=h["symbol"],
                quantity=h["quantity"],
                ltp=h["ltp"],
                avg_price=h["costPrice"],
                pnl=h["pl"],
                day_pnl=0,  # Not available in Fyers API
                value=h["marketVal"],
            )
            for h in holdings_data.get("holdings", [])
        ]

        # Transform funds
        funds_map = {item["title"]: item for item in funds_data.get("fund_limit", [])}
        funds = Funds(
            available_balance=funds_map.get("Available Balance", {}).get(
                "equityAmount", 0
            ),
            margin_used=funds_map.get("Utilized Amount", {}).get("equityAmount", 0),
            total_balance=funds_map.get("Total Balance", {}).get("equityAmount", 0),
        )

        # Create portfolio
        portfolio = Portfolio(
            holdings=holdings,
            funds=funds,
            total_pnl=holdings_data.get("overall", {}).get("total_pl", 0),
            total_day_pnl=0,  # Not available in Fyers API
            total_value=holdings_data.get("overall", {}).get("total_current_value", 0),
        )

        return portfolio.model_dump()
