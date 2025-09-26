
from typing import Any, Dict

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

    async def get_portfolio(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Returns a hardcoded, valid portfolio with Indian assets."""
        return {
            "status": "success",
            "portfolio": {
                "cash": 50000.00,
                "holdings": [
                    {
                        "symbol": "RELIANCE-EQ",
                        "exchange": "NSE",
                        "quantity": 50,
                        "average_price": 2500.00,
                        "last_price": 2850.50,
                        "pnl": 17525.00,
                        "day_pnl": 250.00,
                        "value": 142525.00
                    },
                    {
                        "symbol": "TCS-EQ",
                        "exchange": "NSE",
                        "quantity": 100,
                        "average_price": 3500.00,
                        "last_price": 3800.00,
                        "pnl": 30000.00,
                        "day_pnl": -1500.00,
                        "value": 380000.00
                    },
                    {
                        "symbol": "HDFCBANK-EQ",
                        "exchange": "NSE",
                        "quantity": 200,
                        "average_price": 1500.00,
                        "last_price": 1450.00,
                        "pnl": -10000.00,
                        "day_pnl": -2000.00,
                        "value": 290000.00
                    },
                    {
                        "symbol": "NIFTYBEES",
                        "exchange": "NSE",
                        "quantity": 500,
                        "average_price": 200.00,
                        "last_price": 225.00,
                        "pnl": 12500.00,
                        "day_pnl": 500.00,
                        "value": 112500.00
                    }
                ]
            }
        }
