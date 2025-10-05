from typing import Any, Dict

from ordo.models.api.portfolio import Portfolio, Holding, Funds

from .base import IBrokerAdapter


class MockAdapter(IBrokerAdapter):
    """
    Mock implementation of the IBrokerAdapter for testing purposes with Indian data.
    """

    async def initiate_login(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates a successful login initiation."""
        return {"status": "success", "session_id": "mock_session_123"}

    async def complete_login(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates a successful login completion."""
        return {"status": "success", "authenticated": True}

    async def get_portfolio(self, session_data: Dict[str, Any]) -> Portfolio:
        """Returns a hardcoded, valid portfolio with Indian assets."""
        holdings_data = [
            {
                "symbol": "RELIANCE-EQ",
                "exchange": "NSE",
                "quantity": 50,
                "average_price": 2500.00,
                "last_price": 2850.50,
                "pnl": 17525.00,
                "day_pnl": 250.00,
                "value": 142525.00,
                "instrument_type": "EQ",
            },
            {
                "symbol": "TCS-EQ",
                "exchange": "NSE",
                "quantity": 100,
                "average_price": 3500.00,
                "last_price": 3800.00,
                "pnl": 30000.00,
                "day_pnl": -1500.00,
                "value": 380000.00,
                "instrument_type": "EQ",
            },
            {
                "symbol": "HDFCBANK-EQ",
                "exchange": "NSE",
                "quantity": 200,
                "average_price": 1500.00,
                "last_price": 1450.00,
                "pnl": -10000.00,
                "day_pnl": -2000.00,
                "value": 290000.00,
                "instrument_type": "EQ",
            },
            {
                "symbol": "NIFTYBEES",
                "exchange": "NSE",
                "quantity": 500,
                "average_price": 200.00,
                "last_price": 225.00,
                "pnl": 12500.00,
                "day_pnl": 500.00,
                "value": 112500.00,
                "instrument_type": "ETF",
            },
        ]

        holdings = [
            Holding(
                symbol=h["symbol"],
                quantity=h["quantity"],
                ltp=h["last_price"],
                avg_price=h["average_price"],
                pnl=h["pnl"],
                day_pnl=h["day_pnl"],
                value=h["value"],
            )
            for h in holdings_data
        ]

        funds = Funds(
            available_balance=50000.00,
            margin_used=0.00,
            total_balance=50000.00,
        )

        total_pnl = sum(h["pnl"] for h in holdings_data)
        total_day_pnl = sum(h["day_pnl"] for h in holdings_data)
        total_value = sum(h["value"] for h in holdings_data)

        return Portfolio(
            holdings=holdings,
            funds=funds,
            total_pnl=total_pnl,
            total_day_pnl=total_day_pnl,
            total_value=total_value,
        )

    async def modify_order(
        self, session_data: Dict[str, Any], order_id: str, **kwargs
    ) -> Any:
        raise NotImplementedError

    async def cancel_order(self, session_data: Dict[str, Any], order_id: str) -> Any:
        raise NotImplementedError

    async def get_order_book(self, session_data: Dict[str, Any]) -> Any:
        raise NotImplementedError

    async def get_trade_book(self, session_data: Dict[str, Any]) -> Any:
        raise NotImplementedError

    async def get_profile(self, session_data: Dict[str, Any]) -> Any:
        raise NotImplementedError

    async def get_holdings(self, session_data: Dict[str, Any]) -> Any:
        raise NotImplementedError

    async def get_positions(self, session_data: Dict[str, Any]) -> Any:
        raise NotImplementedError
