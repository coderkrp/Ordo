from typing import Any, Dict

import httpx
from pydantic import BaseModel, ValidationError

from ordo.adapters.base import IBrokerAdapter
from ordo.models.api.errors import ApiError, ApiException
from ordo.models.api.portfolio import Portfolio, Holding, Funds # Not needed yet, but good to have
from ordo.security.session import SessionManager
from ordo.config import settings


class HDFCPlaceOrderRequest(BaseModel):
    orderType: str
    exchange: str
    segment: str
    productType: str
    instrumentToken: str
    quantity: int
    price: float | None = None
    triggerPrice: float | None = None
    disclosedQuantity: int | None = None
    validity: str = "DAY"
    tag: str | None = None
    orderSource: str = "API"
    orderVariety: str = "REGULAR"


class HDFCLoginInitResponse(BaseModel):
    tokenId: str

class HDFCLoginValidateResponse(BaseModel):
    recaptcha: bool
    loginId: str
    twofa: Dict[str, Any]
    twoFAEnabled: bool

class HDFC2FAResponse(BaseModel):
    requestToken: str
    termsAndConditions: Dict[str, Any]
    authorised: bool

class HDFCAuthoriseResponse(BaseModel):
    callbackUrl: str
    requestToken: str

class HDFCAccessTokenResponse(BaseModel):
    accessToken: str

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

class HDFCPlaceOrderAPIResponse(BaseModel):
    orderId: str
    status: str


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
        self.http_client = httpx.AsyncClient(headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        })

    async def _get_login_token(self, config: HDFCConfig) -> str:
        """Fetches the initial login token."""
        token_response = await self.http_client.get(f"{self.base_url}/login?api_key={config.api_key}")
        token_response.raise_for_status()
        token_data = HDFCLoginInitResponse(**token_response.json())
        return token_data.tokenId

    async def _validate_user(self, config: HDFCConfig, token_id: str) -> HDFCLoginValidateResponse:
        """Validates username and password."""
        validate_response = await self.http_client.post(
            f"{self.base_url}/login/validate?api_key={config.api_key}&token_id={token_id}",
            json={"username": config.username, "password": config.password}
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
                "session_data": {"credentials": credentials, "tokenId": token_id, "loginId": validate_data.loginId}
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

    async def _validate_2fa(self, client: httpx.AsyncClient, config: HDFCConfig, token_id: str, otp: str) -> str:
        """Validates the 2FA OTP."""
        twofa_response = await client.post(
            f"{self.base_url}/twofa/validate?api_key={config.api_key}&token_id={token_id}",
            json={"answer": otp}
        )
        twofa_response.raise_for_status()
        twofa_data = HDFC2FAResponse(**twofa_response.json())
        if not twofa_data.requestToken:
            raise ApiException(ApiError(message="Failed to get requestToken after 2FA validation"))
        return twofa_data.requestToken

    async def _authorize_session(self, client: httpx.AsyncClient, config: HDFCConfig, token_id: str, request_token: str | None, consent: bool) -> str:
        """Authorizes the session (Terms & Conditions)."""
        consent_str = str(consent).lower()
        authorise_response = await client.get(
            f"{self.base_url}/authorise?api_key={config.api_key}&token_id={token_id}&consent={consent_str}&request_token={request_token}"
        )
        authorise_response.raise_for_status()
        authorise_data = HDFCAuthoriseResponse(**authorise_response.json())
        if not authorise_data.requestToken:
            raise ApiException(ApiError(message="Failed to get requestToken after authorization"))
        return authorise_data.requestToken

    async def _get_access_token(self, client: httpx.AsyncClient, config: HDFCConfig, request_token: str) -> str:
        """Gets the final access token."""
        access_token_response = await client.post(
            f"{self.base_url}/access-token?api_key={config.api_key}&request_token={request_token}",
            json={"apiSecret": config.apiSecret}
        )
        access_token_response.raise_for_status()
        access_token_data = HDFCAccessTokenResponse(**access_token_response.json())
        if not access_token_data.accessToken:
            raise ApiException(ApiError(message="Failed to get accessToken from HDFC API"))
        return access_token_data.accessToken

    async def complete_login(self, session_data: Dict[str, Any], otp: str | None = None, consent: bool = True) -> Dict[str, Any]:
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
                    request_token = await self._validate_2fa(client, config, token_id, otp)

                request_token = await self._authorize_session(client, config, token_id, request_token, consent)
                access_token = await self._get_access_token(client, config, request_token)

                self.session_manager.set_session(config.api_key, "access_token", access_token)
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

    async def place_order(self, session_data: Dict[str, Any], order_details: Dict[str, Any]) -> Dict[str, Any]:
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
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/order/place",
                    headers=headers,
                    json=order_request.model_dump(exclude_none=True)
                )
                response.raise_for_status()
                response_data = HDFCPlaceOrderAPIResponse(**response.json())

                order_id = response_data.orderId
                status = response_data.status

                if not order_id or not status:
                    raise ApiException(ApiError(message="Failed to place order: Missing orderId or status in response."))

                return {"orderId": order_id, "status": status}

            except httpx.HTTPStatusError as e:
                raise ApiException(
                    ApiError(
                        error_code="BROKER_API_ERROR",
                        message=f"HDFC API error during order placement: {e.response.text}",
                        details={"status_code": e.response.status_code, "response": e.response.json()}
                    )
                )
            except Exception as e:
                raise ApiException(
                    ApiError(
                        error_code="BROKER_REQUEST_FAILED",
                        message=f"Failed to place order with HDFC: {e}",
                    )
                )

    async def get_portfolio(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
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

        async with httpx.AsyncClient() as client:
            try:
                # Retrieve Holdings
                holdings_response = await client.get(
                    f"{self.base_url}/holdings",
                    headers=headers,
                    params={"clientId": login_id} # Assuming clientId is a query parameter
                )
                holdings_response.raise_for_status()
                holdings_data = HDFCHoldingsResponse(**holdings_response.json())

                # Retrieve Portfolio Summary
                portfolio_summary_response = await client.get(
                    f"{self.base_url}/portfolio",
                    headers=headers,
                    params={"clientId": login_id} # Assuming clientId is a query parameter
                )
                portfolio_summary_response.raise_for_status()
                portfolio_summary_data = HDFCPortfolioSummaryResponse(**portfolio_summary_response.json())

            except httpx.HTTPStatusError as e:
                raise ApiException(
                    ApiError(
                        error_code="BROKER_API_ERROR",
                        message=f"HDFC API error during portfolio retrieval: {e.response.text}",
                        details={"status_code": e.response.status_code, "response": e.response.json()}
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

        return portfolio.model_dump()

def modify_order(self, order_id: str, **kwargs) -> OrderResponse:
        if not self.access_token:
            raise OrdoException("Not logged in. Please call login() first.")
        url = f"{self._BASE_URL}/orders/regular/{order_id}?api_key={self.api_key}"
        payload = HDFCModifyOrderRequest(
            quantity=kwargs.get('new_quantity'),
            order_type=kwargs.get('order_type', 'MARKET').upper(),
            validity=kwargs.get('validity', 'DAY').upper(),
            disclosed_quantity=kwargs.get('disclosed_quantity', 0),
            product=kwargs.get('product', 'DELIVERY').upper(),
            price=kwargs.get('new_price', 0.0),
            trigger_price=kwargs.get('trigger_price', 0.0),
            amo=kwargs.get('amo', False)
        )
        try:
            response = self.session.put(url, json=payload.dict())
            response.raise_for_status()
            data = HDFCOrderActionResponse(**response.json())
            return OrderResponse(order_id=data.data['order_id'], status="success")
        except requests.exceptions.RequestException as e:
            raise OrdoException(f"HDFC modify_order failed: {e}")

    def cancel_order(self, order_id: str) -> OrderResponse:
        if not self.access_token:
            raise OrdoException("Not logged in. Please call login() first.")
        url = f"{self._BASE_URL}/orders/regular/{order_id}?api_key={self.api_key}"
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            data = HDFCOrderActionResponse(**response.json())
            return OrderResponse(order_id=data.data['order_id'], status="cancelled")
        except requests.exceptions.RequestException as e:
            raise OrdoException(f"HDFC cancel_order failed: {e}")

    def get_order_book(self) -> List[Order]:
        if not self.access_token:
            raise OrdoException("Not logged in. Please call login().")
        url = f"{self._BASE_URL}/orders?api_key={self.api_key}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = HDFCOrderBookResponse(**response.json())
            orders = []
            for item in data.data:
                orders.append(Order(
                    order_id=item.order_id,
                    symbol=item.tradingsymbol,
                    status=item.status,
                    transaction_type=TransactionType(item.transaction_type.lower()),
                    order_type=OrderType.MARKET,
                    product_type=ProductType(item.product.lower()),
                    quantity=item.quantity,
                    price=item.price,
                    timestamp=item.order_timestamp
                ))
            return orders
        except requests.exceptions.RequestException as e:
            raise OrdoException(f"HDFC get_order_book failed: {e}")

    def get_trade_book(self) -> List[Trade]:
        if not self.access_token:
            raise OrdoException("Not logged in. Please call login().")
        url = f"{self._BASE_URL}/trades?api_key={self.api_key}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = HDFCTradeBookResponse(**response.json())
            trades = []
            for item in data.data:
                trades.append(Trade(
                    trade_id=item.trade_id,
                    order_id=item.order_id,
                    symbol=item.security_id,
                    transaction_type=TransactionType(item.transaction_type.lower()),
                    quantity=item.filled_quantity,
                    price=item.average_price,
                    timestamp=item.fill_timestamp
                ))
            return trades
        except requests.exceptions.RequestException as e:
            raise OrdoException(f"HDFC get_trade_book failed: {e}")

    def get_profile(self) -> Profile:
        if not self.access_token:
            raise OrdoException("Not logged in. Please call login().")
        url = f"{self._BASE_URL}/profile"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = HDFCProfileResponse(**response.json())
            return Profile(client_id=data.client_id, name=data.name, email=data.email)
        except requests.exceptions.RequestException as e:
            raise OrdoException(f"HDFC get_profile failed: {e}")

    def get_holdings(self) -> List[Holding]:
        if not self.access_token:
            raise OrdoException("Not logged in. Please call login().")
        url = f"{self._BASE_URL}/holdings"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            holdings_data = [HDFCHoldingResponse(**item) for item in response.json()]
            return [
                Holding(
                    symbol=item.symbol,
                    quantity=item.qty,
                    average_price=item.avg_price
                ) for item in holdings_data
            ]
        except requests.exceptions.RequestException as e:
            raise OrdoException(f"HDFC get_holdings failed: {e}")

    def get_positions(self) -> List[Position]:
        if not self.access_token:
            raise OrdoException("Not logged in. Please call login().")
        # NOTE: Documentation shows 'cumulative-positions' but curl example uses 'overall_positions'.
        # Using the one from the curl example as it's more likely to be the correct endpoint.
        url = f"{self._BASE_URL}/portfolio/overall_positions?api_key={self.api_key}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            response_data = HDFCPositionsResponse(**response.json())
            positions = []
            for item in response_data.data.net:
                positions.append(Position(
                    symbol=item.security_id,
                    quantity=item.net_qty,
                    product_type=ProductType(item.product.lower()),
                    exchange=item.exchange,
                    instrument_type=item.instrument_segment,
                    realised_pnl=item.realised_pl_overall_position
                ))
            return positions
        except requests.exceptions.RequestException as e:
            raise OrdoException(f"HDFC get_positions failed: {e}")
