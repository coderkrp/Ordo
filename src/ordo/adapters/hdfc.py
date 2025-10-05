import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import httpx
from pydantic import BaseModel, ValidationError, SecretStr, Field

from ordo.adapters.base import IBrokerAdapter
from ordo.models.api.errors import ApiError, ApiException
from ordo.models.api.portfolio import Portfolio, Holding, Funds
from ordo.models.api.order import (
    Order,
    Trade,
    Position,
    OrderResponse,
    TransactionType,
    OrderType,
    ProductType,
    OrderStatus,
    ExchangeType,
    InstrumentSegmentType,
    ValidityType,
    OptionType,
)
from ordo.models.api.user import Profile
from ordo.security.session import SessionManager
from ordo.config import settings


class HDFCModifyOrderRequest(BaseModel):
    quantity: int
    order_type: str
    validity: str
    disclosed_quantity: int
    product: str
    price: float
    trigger_price: float
    amo: bool


class HDFCOrderActionResponseData(BaseModel):
    order_id: str


class HDFCOrderActionResponse(BaseModel):
    data: HDFCOrderActionResponseData


class HDFCOrderBookItem(BaseModel):
    order_id: str
    tradingsymbol: str
    status: str
    transaction_type: str
    product: str
    quantity: int
    price: float
    order_timestamp: str


class HDFCOrderBookResponse(BaseModel):
    data: List[HDFCOrderBookItem]


class HDFCTradeBookItem(BaseModel):
    client_id: str
    trade_id: str
    order_id: str
    exchange: str
    product: str
    average_price: float
    filled_quantity: int
    pending_quantity: int
    exchange_order_id: str
    transaction_type: str
    fill_timestamp: str
    security_id: str
    company_name: str
    underlying_symbol: str
    instrument_segment: str
    expiry_date: Optional[str]
    strike_price: Optional[float]
    option_type: Optional[str]
    isin: str
    status: str
    validity: str
    total_traded_value: float
    order_source: str
    order_type: str


class HDFCTradeBookResponse(BaseModel):
    data: List[HDFCTradeBookItem]


class HDFCProfileResponse(BaseModel):
    client_id: str
    name: str
    email: str


class HDFCHoldingResponse(BaseModel):
    symbol: str
    qty: int
    avg_price: float


class HDFCPositionItem(BaseModel):
    security_id: str
    net_qty: int
    product: str
    exchange: str
    instrument_segment: str
    realised_pl_overall_position: float


class HDFCPositionsData(BaseModel):
    net: List[HDFCPositionItem]


class HDFCPositionsResponse(BaseModel):
    data: HDFCPositionsData


class HDFCPlaceOrderRequest(BaseModel):
    exchange: ExchangeType
    security_id: str
    instrument_segment: InstrumentSegmentType
    transaction_type: TransactionType
    product: ProductType
    quantity: int
    order_type: OrderType
    price: Optional[float] = None
    trigger_price: Optional[float] = None
    disclosed_quantity: Optional[int] = None
    validity: ValidityType
    amo: Optional[bool] = None
    external_reference_number: Optional[int] = None
    expiry_date: Optional[str] = None
    strike_price: Optional[float] = None
    option_type: Optional[OptionType] = None
    underlying_symbol: Optional[str] = None


class HDFCLoginInitResponse(BaseModel):
    tokenId: str = Field(..., description="Unique token ID for login initiation.")


class HDFCLoginValidateRequest(BaseModel):
    tokenId: str = Field(..., description="Token ID obtained from login initiation.")
    userId: str = Field(..., description="User ID for validation.")
    password: SecretStr = Field(..., description="Password for validation.")


class HDFCLoginValidateResponse(BaseModel):
    recaptcha: bool = Field(..., description="Indicates if reCAPTCHA is required.")
    loginId: str = Field(..., description="Login ID for the user.")
    twofa: Dict[str, Any] = Field(
        ..., description="Details for two-factor authentication."
    )
    twoFAEnabled: bool = Field(
        ..., description="Indicates if two-factor authentication is enabled."
    )


class HDFC2FARequest(BaseModel):
    answer: str = Field(
        ...,
        description="Six-digit OTP for 2FA validation.",
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        json_schema_extra={"example": "123456"},
    )


class HDFC2FAResponse(BaseModel):
    requestToken: str = Field(..., description="Request token after 2FA validation.")
    termsAndConditions: Dict[str, Any] = Field(
        ..., description="Terms and conditions details."
    )
    authorised: bool = Field(
        ..., description="Indicates if the user has accepted the terms and conditions."
    )


class HDFCAuthoriseResponse(BaseModel):
    callbackUrl: str = Field(..., description="Callback URL for authorization.")
    requestToken: str = Field(..., description="Request token after authorization.")


class HDFCAccessTokenResponse(BaseModel):
    accessToken: str = Field(
        ..., description="Access token for authenticated API requests."
    )


class HDFCHoldingItem(BaseModel):
    isin: str
    symbol: str
    quantity: int
    averagePrice: float
    currentPrice: float
    totalValue: float
    profitLoss: float


class HDFCHoldingsResponse(BaseModel):
    holdings: list[HDFCHoldingItem]


class HDFCPortfolioSummaryResponse(BaseModel):
    availableBalance: float
    marginUsed: float
    totalBalance: float
    overallProfitLoss: float
    overallValue: float


class HDFCPlaceOrderResponseData(BaseModel):
    order_id: str


class HDFCPlaceOrderResponse(BaseModel):
    status: str
    data: HDFCPlaceOrderResponseData


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
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }

    def _get_response_json_or_text(
        self, response: httpx.Response
    ) -> Union[Dict, str, None]:
        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text

    def _create_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(headers=self._headers)

    async def _get_login_token(self, config: HDFCConfig) -> str:
        """Fetches the initial login token."""
        async with self._create_client() as client:
            token_response = await client.get(
                f"{self.base_url}/login?api_key={config.api_key}"
            )
            token_response.raise_for_status()
            token_data = HDFCLoginInitResponse(**token_response.json())
            return token_data.tokenId

    async def _validate_user(
        self, config: HDFCConfig, token_id: str
    ) -> HDFCLoginValidateResponse:
        """Validates username and password."""
        async with self._create_client() as client:
            validate_response = await client.post(
                f"{self.base_url}/login/validate?api_key={config.api_key}&token_id={token_id}",
                json={"username": config.username, "password": config.password},
            )
            validate_response.raise_for_status()
            return HDFCLoginValidateResponse(**validate_response.json())

    async def initiate_login(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiates the login process for HDFC Securities (Steps 1 & 2).
        """
        try:
            config = HDFCConfig(**credentials)
        except ValidationError as e:
            raise ValueError(f"Missing or invalid HDFC credentials: {e}")

        try:
            token_id = await self._get_login_token(config)
            validate_data = await self._validate_user(config, token_id)

            return {
                "tokenId": token_id,
                "loginId": validate_data.loginId,
                "twofa": validate_data.twofa,
                "twoFAEnabled": validate_data.twoFAEnabled,
                "session_data": {
                    "credentials": credentials,
                    "tokenId": token_id,
                    "loginId": validate_data.loginId,
                },
            }
        except httpx.HTTPStatusError as e:
            raise ApiException(
                ApiError(
                    error_code="BROKER_API_ERROR",
                    message=f"HDFC API error during initiate_login: {e.response.text}",
                    details={
                        "status_code": e.response.status_code,
                        "response": e.response.json(),
                    },
                )
            )
        except Exception as e:
            raise ApiException(
                ApiError(
                    error_code="BROKER_REQUEST_FAILED",
                    message=f"Failed to initiate login with HDFC: {e}",
                )
            )

    async def _validate_2fa(
        self, client: httpx.AsyncClient, config: HDFCConfig, token_id: str, otp: str
    ) -> str:
        """Validates the 2FA OTP."""
        twofa_response = await client.post(
            f"{self.base_url}/twofa/validate?api_key={config.api_key}&token_id={token_id}",
            json={"answer": otp},
        )
        twofa_response.raise_for_status()
        twofa_data = HDFC2FAResponse(**twofa_response.json())
        if not twofa_data.requestToken:
            raise ApiException(
                ApiError(message="Failed to get requestToken after 2FA validation")
            )
        return twofa_data.requestToken

    async def _authorize_session(
        self,
        client: httpx.AsyncClient,
        config: HDFCConfig,
        token_id: str,
        request_token: str | None,
        consent: bool,
    ) -> str:
        """Authorizes the session (Terms & Conditions)."""
        consent_str = str(consent).lower()
        authorise_response = await client.get(
            f"{self.base_url}/authorise?api_key={config.api_key}&token_id={token_id}&consent={consent_str}&request_token={request_token}"
        )
        authorise_response.raise_for_status()
        authorise_data = HDFCAuthoriseResponse(**authorise_response.json())
        if not authorise_data.requestToken:
            raise ApiException(
                ApiError(message="Failed to get requestToken after authorization")
            )
        return authorise_data.requestToken

    async def _get_access_token(
        self, client: httpx.AsyncClient, config: HDFCConfig, request_token: str
    ) -> str:
        """Gets the final access token."""
        access_token_response = await client.post(
            f"{self.base_url}/access-token?api_key={config.api_key}&request_token={request_token}",
            json={"apiSecret": config.apiSecret},
        )
        access_token_response.raise_for_status()
        access_token_data = HDFCAccessTokenResponse(**access_token_response.json())
        if not access_token_data.accessToken:
            raise ApiException(
                ApiError(message="Failed to get accessToken from HDFC API")
            )
        return access_token_data.accessToken

    async def complete_login(
        self, session_data: Dict[str, Any], otp: str | None = None, consent: bool = True
    ) -> Dict[str, Any]:
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
                if session_data.get("twoFAEnabled") and otp:
                    request_token = await self._validate_2fa(
                        client, config, token_id, otp
                    )

                request_token = await self._authorize_session(
                    client, config, token_id, request_token, consent
                )
                access_token = await self._get_access_token(
                    client, config, request_token
                )

                self.session_manager.set_session(
                    config.api_key, "access_token", access_token
                )
                return {"access_token": access_token}

            except httpx.HTTPStatusError as e:
                response_content = self._get_response_json_or_text(e.response)
                raise ApiException(
                    ApiError(
                        error_code="BROKER_API_ERROR",
                        message=f"HDFC API error during complete_login: {e.response.text}",
                        details={
                            "status_code": e.response.status_code,
                            "response": response_content,
                        },
                    )
                )
            except Exception as e:
                raise ApiException(
                    ApiError(
                        error_code="BROKER_REQUEST_FAILED",
                        message=f"Failed to complete login with HDFC: {e}",
                    )
                )

    async def place_order(
        self, session_data: Dict[str, Any], order_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Places an order with HDFC Securities.
        """
        config = HDFCConfig(**session_data["credentials"])
        access_token = self.session_manager.get_session(config.api_key, "access_token")

        if not access_token:
            raise ApiException(ApiError(message="No access token found in session."))

        try:
            order_request = HDFCPlaceOrderRequest(**order_details)
        except ValidationError as e:
            raise ValueError(f"Invalid order details: {e}")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        async with self._create_client() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/orders/regular?api_key={config.api_key}",
                    headers=headers,
                    json=order_request.model_dump(exclude_none=True),
                )
                response.raise_for_status()
                response_data = HDFCPlaceOrderResponse(**response.json())

                order_id = response_data.data.order_id
                status = response_data.status

                if not order_id or not status:
                    raise ApiException(
                        ApiError(
                            message="Failed to place order: Missing order_id or status in response."
                        )
                    )

                return {"order_id": order_id, "status": status}

            except httpx.HTTPStatusError as e:
                response_content = self._get_response_json_or_text(e.response)
                raise ApiException(
                    ApiError(
                        error_code="BROKER_API_ERROR",
                        message=f"HDFC API error during order placement: {e.response.text}",
                        details={
                            "status_code": e.response.status_code,
                            "response": response_content,
                        },
                    )
                )
            except Exception as e:
                raise ApiException(
                    ApiError(
                        error_code="BROKER_REQUEST_FAILED",
                        message=f"Failed to place order with HDFC: {e}",
                    )
                )

    async def get_portfolio(self, session_data: Dict[str, Any]) -> Portfolio:
        """
        Retrieves the portfolio from HDFC Securities.
        """
        config = HDFCConfig(**session_data["credentials"])
        access_token = self.session_manager.get_session(config.api_key, "access_token")
        login_id = session_data.get("loginId")

        if not access_token:
            raise ApiException(ApiError(message="No access token found in session."))
        if not login_id:
            raise ApiException(ApiError(message="No login ID found in session."))

        headers = {"Authorization": f"Bearer {access_token}"}

        async with self._create_client() as client:
            try:
                # Retrieve Holdings
                holdings_response = await client.get(
                    f"{self.base_url}/holdings",
                    headers=headers,
                    params={
                        "clientId": login_id
                    },  # Assuming clientId is a query parameter
                )
                holdings_response.raise_for_status()
                holdings_data = HDFCHoldingsResponse(**holdings_response.json())

                # Retrieve Portfolio Summary
                portfolio_summary_response = await client.get(
                    f"{self.base_url}/portfolio",
                    headers=headers,
                    params={
                        "clientId": login_id
                    },  # Assuming clientId is a query parameter
                )
                portfolio_summary_response.raise_for_status()
                portfolio_summary_data = HDFCPortfolioSummaryResponse(
                    **portfolio_summary_response.json()
                )

            except httpx.HTTPStatusError as e:
                response_content = self._get_response_json_or_text(e.response)
                raise ApiException(
                    ApiError(
                        error_code="BROKER_API_ERROR",
                        message=f"HDFC API error during portfolio retrieval: {e.response.text}",
                        details={
                            "status_code": e.response.status_code,
                            "response": response_content,
                        },
                    )
                )
            except Exception as e:
                raise ApiException(
                    ApiError(
                        error_code="BROKER_REQUEST_FAILED",
                        message=f"Failed to retrieve portfolio from HDFC: {e}",
                    )
                )

        # --- Data Transformation ---
        holdings = [
            Holding(
                symbol=h.symbol,
                quantity=h.quantity,
                ltp=h.currentPrice,
                avg_price=h.averagePrice,
                pnl=h.profitLoss,
                # HDFC API does not provide day P&L in the holdings endpoint.
                # This is a known limitation of the API, and we are hardcoding it to 0.0
                # as per the current implementation.
                day_pnl=0.0,
                value=h.totalValue,
            )
            for h in holdings_data.holdings
        ]

        funds = Funds(
            available_balance=portfolio_summary_data.availableBalance,
            margin_used=portfolio_summary_data.marginUsed,
            total_balance=portfolio_summary_data.totalBalance,
        )

        portfolio = Portfolio(
            holdings=holdings,
            funds=funds,
            total_pnl=portfolio_summary_data.overallProfitLoss,
            # HDFC API does not provide total day P&L, so it is hardcoded to 0.0.
            # This should be documented as a limitation.
            total_day_pnl=0.0,
            total_value=portfolio_summary_data.overallValue,
        )

        return portfolio

    async def modify_order(
        self, session_data: Dict[str, Any], order_id: str, **kwargs
    ) -> OrderResponse:
        config = HDFCConfig(**session_data["credentials"])
        access_token = self.session_manager.get_session(config.api_key, "access_token")

        if not access_token:
            raise ApiException(ApiError(message="No access token found in session."))

        url = f"{self.base_url}/orders/regular/{order_id}?api_key={config.api_key}"
        payload = HDFCModifyOrderRequest(
            quantity=kwargs.get("new_quantity"),
            order_type=kwargs.get("order_type", "MARKET").upper(),
            validity=kwargs.get("validity", "DAY").upper(),
            disclosed_quantity=kwargs.get("disclosed_quantity", 0),
            product=kwargs.get("product", "DELIVERY").upper(),
            price=kwargs.get("new_price", 0.0),
            trigger_price=kwargs.get("trigger_price", 0.0),
            amo=kwargs.get("amo", False),
        )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        try:
            async with self._create_client() as client:
                response = await client.put(
                    url, json=payload.model_dump(), headers=headers
                )
                response.raise_for_status()
                data = HDFCOrderActionResponse(**response.json())
                return OrderResponse(order_id=data.data.order_id, status="success")
        except httpx.HTTPStatusError as e:
            response_content = self._get_response_json_or_text(e.response)
            raise ApiException(
                ApiError(
                    error_code="BROKER_API_ERROR",
                    message=f"HDFC API error during modify_order: {e.response.text}",
                    details={
                        "status_code": e.response.status_code,
                        "response": response_content,
                    },
                )
            )
        except Exception as e:
            raise ApiException(
                ApiError(
                    error_code="BROKER_REQUEST_FAILED",
                    message=f"Failed to modify order with HDFC: {e}",
                )
            )

    async def cancel_order(
        self, session_data: Dict[str, Any], order_id: str
    ) -> OrderResponse:
        config = HDFCConfig(**session_data["credentials"])
        access_token = self.session_manager.get_session(config.api_key, "access_token")

        if not access_token:
            raise ApiException(ApiError(message="No access token found in session."))

        url = f"{self.base_url}/orders/regular/{order_id}?api_key={config.api_key}"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        try:
            async with self._create_client() as client:
                response = await client.delete(url, headers=headers)
                response.raise_for_status()
                data = HDFCOrderActionResponse(**response.json())
                return OrderResponse(order_id=data.data.order_id, status="cancelled")
        except httpx.HTTPStatusError as e:
            response_content = self._get_response_json_or_text(e.response)
            raise ApiException(
                ApiError(
                    error_code="BROKER_API_ERROR",
                    message=f"HDFC API error during cancel_order: {e.response.text}",
                    details={
                        "status_code": e.response.status_code,
                        "response": response_content,
                    },
                )
            )
        except Exception as e:
            raise ApiException(
                ApiError(
                    error_code="BROKER_REQUEST_FAILED",
                    message=f"Failed to cancel order with HDFC: {e}",
                )
            )

    async def get_order_book(self, session_data: Dict[str, Any]) -> List[Order]:
        config = HDFCConfig(**session_data["credentials"])
        access_token = self.session_manager.get_session(config.api_key, "access_token")

        if not access_token:
            raise ApiException(ApiError(message="No access token found in session."))

        url = f"{self.base_url}/orders?api_key={config.api_key}"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        try:
            async with self._create_client() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = HDFCOrderBookResponse(**response.json())
                orders = []
            for item in data.data:
                orders.append(
                    Order(
                        order_id=item.order_id,
                        symbol=item.tradingsymbol,
                        status=OrderStatus(item.status.lower()),
                        transaction_type=TransactionType(item.transaction_type.lower()),
                        order_type=OrderType.MARKET,  # HDFC does not provide order type in order book
                        product_type=ProductType(item.product.lower()),
                        quantity=item.quantity,
                        price=item.price,
                        timestamp=datetime.fromisoformat(item.order_timestamp),
                    )
                )
            return orders
        except httpx.HTTPStatusError as e:
            response_content = self._get_response_json_or_text(e.response)
            raise ApiException(
                ApiError(
                    error_code="BROKER_API_ERROR",
                    message=f"HDFC API error during get_order_book: {e.response.text}",
                    details={
                        "status_code": e.response.status_code,
                        "response": response_content,
                    },
                )
            )
        except Exception as e:
            raise ApiException(
                ApiError(
                    error_code="BROKER_REQUEST_FAILED",
                    message=f"Failed to get order book from HDFC: {e}",
                )
            )

    async def get_trade_book(self, session_data: Dict[str, Any]) -> List[Trade]:
        config = HDFCConfig(**session_data["credentials"])
        access_token = self.session_manager.get_session(config.api_key, "access_token")

        if not access_token:
            raise ApiException(ApiError(message="No access token found in session."))

        url = f"{self.base_url}/trades?api_key={config.api_key}"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        try:
            async with self._create_client() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = HDFCTradeBookResponse(**response.json())
                trades = []
            for item in data.data:
                trades.append(
                    Trade(
                        trade_id=item.trade_id,
                        order_id=item.order_id,
                        exchange=item.exchange,
                        product=ProductType(item.product.lower()),
                        average_price=item.average_price,
                        filled_quantity=item.filled_quantity,
                        exchange_order_id=item.exchange_order_id,
                        transaction_type=TransactionType(item.transaction_type.lower()),
                        fill_timestamp=datetime.strptime(
                            item.fill_timestamp, "%d/%m/%Y %H:%M:%S"
                        ),
                        security_id=item.security_id,
                        company_name=item.company_name,
                    )
                )
            return trades
        except httpx.HTTPStatusError as e:
            response_content = self._get_response_json_or_text(e.response)
            raise ApiException(
                ApiError(
                    error_code="BROKER_API_ERROR",
                    message=f"HDFC API error during get_trade_book: {e.response.text}",
                    details={
                        "status_code": e.response.status_code,
                        "response": response_content,
                    },
                )
            )
        except Exception as e:
            raise ApiException(
                ApiError(
                    error_code="BROKER_REQUEST_FAILED",
                    message=f"Failed to get trade book from HDFC: {e}",
                )
            )

    async def get_profile(self, session_data: Dict[str, Any]) -> Profile:
        config = HDFCConfig(**session_data["credentials"])
        access_token = self.session_manager.get_session(config.api_key, "access_token")

        if not access_token:
            raise ApiException(ApiError(message="No access token found in session."))

        url = f"{self.base_url}/profile"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        try:
            async with self._create_client() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = HDFCProfileResponse(**response.json())
                return Profile(
                    client_id=data.client_id, name=data.name, email=data.email
                )
        except httpx.HTTPStatusError as e:
            response_content = self._get_response_json_or_text(e.response)
            raise ApiException(
                ApiError(
                    error_code="BROKER_API_ERROR",
                    message=f"HDFC API error during get_profile: {e.response.text}",
                    details={
                        "status_code": e.response.status_code,
                        "response": response_content,
                    },
                )
            )
        except Exception as e:
            raise ApiException(
                ApiError(
                    error_code="BROKER_REQUEST_FAILED",
                    message=f"Failed to get profile from HDFC: {e}",
                )
            )

    async def get_holdings(self, session_data: Dict[str, Any]) -> List[Holding]:
        config = HDFCConfig(**session_data["credentials"])
        access_token = self.session_manager.get_session(config.api_key, "access_token")

        if not access_token:
            raise ApiException(ApiError(message="No access token found in session."))

        login_id = session_data.get("loginId")

        if not login_id:
            raise ApiException(ApiError(message="No login ID found in session."))

        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            async with self._create_client() as client:
                # Retrieve Holdings
                holdings_response = await client.get(
                    f"{self.base_url}/holdings",
                    headers=headers,
                    params={
                        "clientId": login_id
                    },  # Assuming clientId is a query parameter
                )
                holdings_response.raise_for_status()
                holdings_data = HDFCHoldingsResponse(**holdings_response.json())

                return [
                    Holding(
                        symbol=h.symbol,
                        quantity=h.quantity,
                        ltp=h.currentPrice,
                        avg_price=h.averagePrice,
                        pnl=h.profitLoss,
                        day_pnl=0.0,  # HDFC API does not provide day P&L in the holdings endpoint.
                        value=h.totalValue,
                    )
                    for h in holdings_data.holdings
                ]
        except httpx.HTTPStatusError as e:
            response_content = self._get_response_json_or_text(e.response)
            raise ApiException(
                ApiError(
                    error_code="BROKER_API_ERROR",
                    message=f"HDFC API error during get_holdings: {e.response.text}",
                    details={
                        "status_code": e.response.status_code,
                        "response": response_content,
                    },
                )
            )
        except Exception as e:
            raise ApiException(
                ApiError(
                    error_code="BROKER_REQUEST_FAILED",
                    message=f"Failed to get holdings from HDFC: {e}",
                )
            )

    async def get_positions(self, session_data: Dict[str, Any]) -> List[Position]:
        config = HDFCConfig(**session_data["credentials"])
        access_token = self.session_manager.get_session(config.api_key, "access_token")

        if not access_token:
            raise ApiException(
                ApiError(
                    error_code="UNAUTHORIZED",
                    message="No access token found in session.",
                )
            )

        url = f"{self.base_url}/portfolio/overall_positions?api_key={config.api_key}"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        try:
            async with self._create_client() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                response_data = HDFCPositionsResponse(**response.json())
                positions = []
                for item in response_data.data.net:
                    positions.append(
                        Position(
                            symbol=item.security_id,
                            quantity=item.net_qty,
                            product_type=ProductType(item.product.lower()),
                            exchange=item.exchange,
                            instrument_type=item.instrument_segment,
                            realised_pnl=item.realised_pl_overall_position,
                        )
                    )
                return positions
        except httpx.HTTPStatusError as e:
            response_content = self._get_response_json_or_text(e.response)
            raise ApiException(
                ApiError(
                    error_code="BROKER_API_ERROR",
                    message=f"HDFC API error during get_positions: {e.response.text}",
                    details={
                        "status_code": e.response.status_code,
                        "response": response_content,
                    },
                )
            )
        except Exception as e:
            raise ApiException(
                ApiError(
                    error_code="BROKER_REQUEST_FAILED",
                    message=f"Failed to get positions from HDFC: {e}",
                )
            )
