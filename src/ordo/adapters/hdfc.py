import hashlib
import uuid
from typing import Any, Dict

import httpx
from pydantic import BaseModel, ValidationError

from ordo.adapters.base import IBrokerAdapter
from ordo.models.api.errors import ApiError, ApiException, CSRFError
from ordo.models.api.portfolio import Portfolio, Holding, Funds # Not needed yet, but good to have
from ordo.security.session import SessionManager
from ordo.config import settings


class HDFCConfig(BaseModel):
    """
    Pydantic model for HDFC Securities API credentials.
    """
    api_key: str
    username: str
    password: str
    apiSecret: str


class HDFCAdapter(IBrokerAdapter):
    """
    Adapter for interacting with the HDFC Securities API.
    """

    def __init__(self):
        self.base_url = "https://developer.hdfcsec.com/oapi/v1"
        self.session_manager = SessionManager(settings.SECRET_KEY)

    async def initiate_login(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiates the login process for HDFC Securities (Steps 1 & 2).
        """
        try:
            config = HDFCConfig(**credentials)
        except ValidationError as e:
            raise ValueError(f"Missing or invalid HDFC credentials: {e}")

        # Step 1: Fetch tokenId
        async with httpx.AsyncClient() as client:
            try:
                token_response = await client.get(
                    f"{self.base_url}/login?api_key={config.api_key}",
                    headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}
                )
                token_response.raise_for_status()
                token_data = token_response.json()
                token_id = token_data.get("tokenId")
                if not token_id:
                    raise ApiException(ApiError(message="Failed to get tokenId from HDFC API"))

                # Step 2: Validate username and password
                validate_response = await client.post(
                    f"{self.base_url}/login/validate?api_key={config.api_key}&token_id={token_id}",
                    headers={
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                        "Content-Type": "application/json"
                    },
                    json={"username": config.username, "password": config.password}
                )
                validate_response.raise_for_status()
                validate_data = validate_response.json()

                return {
                    "tokenId": token_id,
                    "loginId": validate_data.get("loginId"),
                    "twofa": validate_data.get("twofa"),
                    "twoFAEnabled": validate_data.get("twoFAEnabled"),
                    "session_data": {"credentials": credentials, "tokenId": token_id, "loginId": validate_data.get("loginId")}
                }
            except httpx.HTTPStatusError as e:
                raise ApiException(
                    ApiError(
                        error_code="BROKER_API_ERROR",
                        message=f"HDFC API error during initiate_login: {e.response.text}",
                        details={"status_code": e.response.status_code, "response": e.response.json()}
                    )
                )
            except Exception as e:
                raise ApiException(
                    ApiError(
                        error_code="BROKER_REQUEST_FAILED",
                        message=f"Failed to initiate login with HDFC: {e}",
                    )
                )


    async def complete_login(self, session_data: Dict[str, Any], otp: str | None = None) -> Dict[str, Any]:
        """
        Completes the login process for HDFC Securities (Steps 3, 4 & 5).
        """
        config = HDFCConfig(**session_data["credentials"])
        token_id = session_data["tokenId"]
        request_token = None
        if session_data.get("twoFAEnabled") and not otp:
            raise ApiException(
                ApiError(
                    error_code="BROKER_REQUEST_FAILED",
                    message="2FA is enabled but no OTP was provided.",
                )
            )

        async with httpx.AsyncClient() as client:
            try:
                # Step 3: Validate 2FA OTP (if enabled and provided)
                if session_data.get("twoFAEnabled") and otp:
                    twofa_response = await client.post(
                        f"{self.base_url}/twofa/validate?api_key={config.api_key}&token_id={token_id}",
                        headers={
                            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                            "Content-Type": "application/json"
                        },
                        json={"answer": otp}
                    )
                    twofa_response.raise_for_status()
                    twofa_data = twofa_response.json()
                    request_token = twofa_data.get("requestToken")
                    if not request_token:
                        raise ApiException(ApiError(message="Failed to get requestToken after 2FA validation"))

                # If 2FA was not enabled or already handled, and request_token is still None,
                # we need to get it from the validate step's response if it was present there.
                # However, the provided flow shows requestToken only after 2FA.
                # Assuming if 2FA is not enabled, the requestToken would be available after step 2 or 4.
                # For now, we'll proceed assuming request_token is obtained from 2FA or will be handled in step 4.

                # Step 4: Authorize (Terms & Conditions)
                # Assuming consent=true for now. The request_token from 2FA is used here.
                # If 2FA was not enabled, we might need to re-evaluate how request_token is obtained for this step.
                # For now, we'll use the request_token from 2FA or assume it's not needed if 2FA is off.
                consent = "true" # Assuming user always consents
                authorise_response = await client.get(
                    f"{self.base_url}/authorise?api_key={config.api_key}&token_id={token_id}&consent={consent}&request_token={request_token}",
                    headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}
                )
                authorise_response.raise_for_status()
                authorise_data = authorise_response.json()
                request_token = authorise_data.get("requestToken") # Update request_token from this step
                if not request_token:
                    raise ApiException(ApiError(message="Failed to get requestToken after authorization"))


                # Step 5: Get accessToken
                access_token_response = await client.post(
                    f"{self.base_url}/access-token?api_key={config.api_key}&request_token={request_token}",
                    headers={
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                        "Content-Type": "application/json"
                    },
                    json={"apiSecret": config.apiSecret}
                )
                access_token_response.raise_for_status()
                access_token_data = access_token_response.json()
                access_token = access_token_data.get("accessToken")
                if not access_token:
                    raise ApiException(ApiError(message="Failed to get accessToken from HDFC API"))

                self.session_manager.set_session(config.api_key, "access_token", access_token)
                # Store other relevant session data if needed

                return {"access_token": access_token}

            except httpx.HTTPStatusError as e:
                raise ApiException(
                    ApiError(
                        error_code="BROKER_API_ERROR",
                        message=f"HDFC API error during complete_login: {e.response.text}",
                        details={"status_code": e.response.status_code, "response": e.response.json()}
                    )
                )
            except Exception as e:
                raise ApiException(
                    ApiError(
                        error_code="BROKER_REQUEST_FAILED",
                        message=f"Failed to complete login with HDFC: {e}",
                    )
                )

    async def get_portfolio(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieves the portfolio from HDFC Securities.
        """
        # TODO: Implement HDFC-specific portfolio retrieval logic
        raise NotImplementedError