import pytest
from ordo.adapters.base import IBrokerAdapter
from ordo.adapters.mock import MockAdapter

def test_ibroker_adapter_is_abstract():
    with pytest.raises(TypeError):
        IBrokerAdapter()

def test_mock_adapter_is_subclass_of_ibroker_adapter():
    assert issubclass(MockAdapter, IBrokerAdapter)

@pytest.mark.asyncio
async def test_mock_adapter_initiate_login():
    adapter = MockAdapter()
    response = await adapter.initiate_login({})
    assert response["status"] == "success"
    assert "session_id" in response

@pytest.mark.asyncio
async def test_mock_adapter_complete_login():
    adapter = MockAdapter()
    response = await adapter.complete_login({})
    assert response["status"] == "success"
    assert response["authenticated"] is True

@pytest.mark.asyncio
async def test_mock_adapter_get_portfolio_structure():
    adapter = MockAdapter()
    response = await adapter.get_portfolio({})
    assert response["status"] == "success"
    assert "portfolio" in response
    portfolio = response["portfolio"]
    assert "cash" in portfolio
    assert "holdings" in portfolio
    assert isinstance(portfolio["holdings"], list)

@pytest.mark.asyncio
async def test_mock_adapter_get_rich_portfolio_data():
    class RichMockAdapter(MockAdapter):
        async def get_portfolio(self, session_data):
            portfolio = await super().get_portfolio(session_data)
            portfolio["portfolio"]["holdings"].append(
                {
                    "symbol": "NIFTY25SEP2423000CE",
                    "exchange": "NFO",
                    "quantity": 50,
                    "average_price": 100.00,
                    "last_price": 120.00,
                    "pnl": 1000.00,
                    "day_pnl": 200.00,
                    "value": 6000.00,
                    "instrument_type": "OPTIDX"
                }
            )
            return portfolio

    adapter = RichMockAdapter()
    response = await adapter.get_portfolio({})
    holdings = response["portfolio"]["holdings"]
    assert any(h.get("instrument_type") == "OPTIDX" for h in holdings)

@pytest.mark.asyncio
async def test_mock_adapter_error_simulation():
    adapter = MockAdapter()
    # Override a method to simulate an error
    async def mock_get_portfolio_error(session_data):
        return {"status": "error", "message": "Broker unavailable"}
    adapter.get_portfolio = mock_get_portfolio_error
    response = await adapter.get_portfolio({})
    assert response["status"] == "error"
    assert response["message"] == "Broker unavailable"
