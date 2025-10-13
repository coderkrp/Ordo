"""
Unit tests for RequestOrchestrator.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from ordo.core.orchestrator import RequestOrchestrator, SessionCheckResult
from ordo.models.api.unified import BrokerResult, UnifiedResponse
from ordo.models.api.portfolio import Portfolio, Holding, Funds
from ordo.models.api.order import OrderResponse
from ordo.security.session import SessionManager
from ordo.adapters.base import IBrokerAdapter


# Test Fixtures


@pytest.fixture
def mock_session_manager():
    """SessionManager that always returns valid sessions."""
    manager = Mock(spec=SessionManager)
    manager.ensure_valid_session = AsyncMock(
        return_value=SessionCheckResult(status="valid", message="Session is valid")
    )
    return manager


@pytest.fixture
def mock_adapter_success():
    """Adapter that returns successful portfolio data."""

    class MockSuccessAdapter:
        async def get_portfolio(self, session_data):
            return Portfolio(
                holdings=[
                    Holding(
                        symbol="RELIANCE",
                        quantity=10,
                        ltp=2500.0,
                        avg_price=2400.0,
                        pnl=1000.0,
                        day_pnl=100.0,
                        value=25000.0,
                    )
                ],
                funds=Funds(
                    available_balance=50000.0, margin_used=10000.0, total_balance=60000.0
                ),
                total_pnl=1000.0,
                total_day_pnl=100.0,
                total_value=25000.0,
            )

    return MockSuccessAdapter


@pytest.fixture
def mock_adapter_failure():
    """Adapter that raises an exception."""

    class MockFailureAdapter:
        async def get_portfolio(self, session_data):
            raise Exception("Broker API unavailable")

    return MockFailureAdapter


@pytest.fixture
def mock_adapter_timeout():
    """Adapter that times out."""

    class MockTimeoutAdapter:
        async def get_portfolio(self, session_data):
            await asyncio.sleep(10)  # Longer than default timeout
            return Portfolio(
                holdings=[],
                funds=Funds(
                    available_balance=0.0, margin_used=0.0, total_balance=0.0
                ),
                total_pnl=0.0,
                total_day_pnl=0.0,
                total_value=0.0,
            )

    return MockTimeoutAdapter


@pytest.fixture
def orchestrator_with_adapters(mock_session_manager, mock_adapter_success):
    """Orchestrator with mock adapters."""
    adapter_registry = {
        "mock_success": mock_adapter_success,
    }
    return RequestOrchestrator(
        session_manager=mock_session_manager,
        adapter_registry=adapter_registry,
        per_broker_timeout=2,
        global_timeout=5,
    )


# Unit Tests


def test_orchestrator_initialization(mock_session_manager):
    """Test orchestrator initializes correctly."""
    adapter_registry = {"mock": Mock}
    orchestrator = RequestOrchestrator(mock_session_manager, adapter_registry)

    assert orchestrator.session_manager == mock_session_manager
    assert orchestrator.adapter_registry == adapter_registry
    assert orchestrator.per_broker_timeout == 8
    assert orchestrator.global_timeout == 12


def test_compute_overall_status_all_success():
    """Test overall status computation when all brokers succeed."""
    results = [
        BrokerResult(broker_id="mock1", status="success", code="SUCCESS", message="OK"),
        BrokerResult(broker_id="mock2", status="success", code="SUCCESS", message="OK"),
        BrokerResult(broker_id="mock3", status="success", code="SUCCESS", message="OK"),
    ]

    orchestrator = RequestOrchestrator(Mock(), {})
    overall_status = orchestrator._compute_overall_status(results)

    assert overall_status == "success"


def test_compute_overall_status_all_failure():
    """Test overall status computation when all brokers fail."""
    results = [
        BrokerResult(
            broker_id="mock1", status="failed", code="TIMEOUT", message="Timeout"
        ),
        BrokerResult(
            broker_id="mock2", status="failed", code="ERROR", message="Error"
        ),
    ]

    orchestrator = RequestOrchestrator(Mock(), {})
    overall_status = orchestrator._compute_overall_status(results)

    assert overall_status == "failure"


def test_compute_overall_status_partial_success():
    """Test overall status computation with mixed results."""
    results = [
        BrokerResult(broker_id="mock1", status="success", code="SUCCESS", message="OK"),
        BrokerResult(
            broker_id="mock2", status="failed", code="TIMEOUT", message="Timeout"
        ),
        BrokerResult(broker_id="mock3", status="success", code="SUCCESS", message="OK"),
    ]

    orchestrator = RequestOrchestrator(Mock(), {})
    overall_status = orchestrator._compute_overall_status(results)

    assert overall_status == "partial_success"


def test_compute_overall_status_empty_results():
    """Test overall status computation with no results."""
    results = []

    orchestrator = RequestOrchestrator(Mock(), {})
    overall_status = orchestrator._compute_overall_status(results)

    assert overall_status == "failure"


@pytest.mark.asyncio
async def test_get_portfolio_single_broker_success(
    mock_session_manager, mock_adapter_success
):
    """Test get_portfolio with single broker returning success."""
    adapter_registry = {"mock": mock_adapter_success}
    orchestrator = RequestOrchestrator(mock_session_manager, adapter_registry)

    context = {"account_id": "test_account", "session_data": {"mock": {}}}
    response = await orchestrator.get_portfolio(["mock"], context)

    assert isinstance(response, UnifiedResponse)
    assert response.overall_status == "success"
    assert len(response.results) == 1
    assert response.results[0].broker_id == "mock"
    assert response.results[0].status == "success"
    assert response.results[0].payload is not None
    assert response.errors is None


@pytest.mark.asyncio
async def test_get_portfolio_multiple_brokers_all_success(
    mock_session_manager, mock_adapter_success
):
    """Test get_portfolio with multiple brokers all succeeding."""
    adapter_registry = {
        "mock1": mock_adapter_success,
        "mock2": mock_adapter_success,
        "mock3": mock_adapter_success,
    }
    orchestrator = RequestOrchestrator(mock_session_manager, adapter_registry)

    context = {
        "account_id": "test_account",
        "session_data": {"mock1": {}, "mock2": {}, "mock3": {}},
    }
    response = await orchestrator.get_portfolio(["mock1", "mock2", "mock3"], context)

    assert response.overall_status == "success"
    assert len(response.results) == 3
    assert all(r.status == "success" for r in response.results)
    assert response.errors is None


@pytest.mark.asyncio
async def test_get_portfolio_partial_success(
    mock_session_manager, mock_adapter_success, mock_adapter_failure
):
    """Test get_portfolio with partial success (some succeed, some fail)."""
    adapter_registry = {
        "mock_success_1": mock_adapter_success,
        "mock_failure": mock_adapter_failure,
        "mock_success_2": mock_adapter_success,
    }
    orchestrator = RequestOrchestrator(mock_session_manager, adapter_registry)

    context = {
        "account_id": "test_account",
        "session_data": {
            "mock_success_1": {},
            "mock_failure": {},
            "mock_success_2": {},
        },
    }
    response = await orchestrator.get_portfolio(
        ["mock_success_1", "mock_failure", "mock_success_2"], context
    )

    assert response.overall_status == "partial_success"
    assert len(response.results) == 3

    # Check successes
    success_results = [r for r in response.results if r.status == "success"]
    assert len(success_results) == 2

    # Check failures
    failed_results = [r for r in response.results if r.status == "failed"]
    assert len(failed_results) == 1
    assert failed_results[0].broker_id == "mock_failure"

    # Check errors list
    assert response.errors is not None
    assert len(response.errors) == 1


@pytest.mark.asyncio
async def test_get_portfolio_all_failures(
    mock_session_manager, mock_adapter_failure
):
    """Test get_portfolio when all brokers fail."""
    adapter_registry = {
        "mock_fail_1": mock_adapter_failure,
        "mock_fail_2": mock_adapter_failure,
    }
    orchestrator = RequestOrchestrator(mock_session_manager, adapter_registry)

    context = {
        "account_id": "test_account",
        "session_data": {"mock_fail_1": {}, "mock_fail_2": {}},
    }
    response = await orchestrator.get_portfolio(["mock_fail_1", "mock_fail_2"], context)

    assert response.overall_status == "failure"
    assert len(response.results) == 2
    assert all(r.status == "failed" for r in response.results)
    assert response.errors is not None
    assert len(response.errors) == 2


@pytest.mark.asyncio
async def test_place_order_with_timeout(mock_session_manager, mock_adapter_timeout):
    """Test place_order with broker that times out."""
    adapter_registry = {"mock_timeout": mock_adapter_timeout}
    orchestrator = RequestOrchestrator(
        mock_session_manager, adapter_registry, per_broker_timeout=1
    )

    context = {"account_id": "test_account", "session_data": {"mock_timeout": {}}}
    order_data = {"symbol": "RELIANCE", "quantity": 10}

    response = await orchestrator.place_order(order_data, ["mock_timeout"], context)

    assert response.overall_status == "failure"
    assert len(response.results) == 1
    assert response.results[0].status == "failed"
    assert response.results[0].code == "TIMEOUT"
    assert "timed out" in response.results[0].message.lower()


@pytest.mark.asyncio
async def test_session_validation_before_call(mock_adapter_success):
    """Test orchestrator validates session before calling adapter."""
    # Session manager that returns expired status
    session_manager = Mock(spec=SessionManager)
    session_manager.ensure_valid_session = AsyncMock(
        return_value=SessionCheckResult(status="expired", message="Session expired")
    )

    adapter_registry = {"mock": mock_adapter_success}
    orchestrator = RequestOrchestrator(session_manager, adapter_registry)

    context = {"account_id": "test_account", "session_data": {"mock": {}}}
    response = await orchestrator.get_portfolio(["mock"], context)

    assert response.overall_status == "failure"
    assert response.results[0].status == "failed"
    assert response.results[0].code == "INVALID_SESSION"
    assert "Session validation failed" in response.results[0].message


@pytest.mark.asyncio
async def test_concurrent_execution(mock_session_manager):
    """Test that multiple broker calls execute concurrently."""
    # Create adapters with artificial delays
    class DelayedAdapter:
        def __init__(self, delay):
            self.delay = delay

        async def get_portfolio(self, session_data):
            await asyncio.sleep(self.delay)
            return Portfolio(
                holdings=[],
                funds=Funds(
                    available_balance=0.0, margin_used=0.0, total_balance=0.0
                ),
                total_pnl=0.0,
                total_day_pnl=0.0,
                total_value=0.0,
            )

    adapter_registry = {
        "broker1": DelayedAdapter,
        "broker2": DelayedAdapter,
        "broker3": DelayedAdapter,
    }
    orchestrator = RequestOrchestrator(mock_session_manager, adapter_registry)

    # Each adapter has 0.5s delay
    # If sequential: 1.5s total
    # If concurrent: ~0.5s total
    context = {
        "account_id": "test_account",
        "session_data": {"broker1": {}, "broker2": {}, "broker3": {}},
    }

    import time

    start = time.time()
    response = await orchestrator.get_portfolio(
        ["broker1", "broker2", "broker3"], context
    )
    elapsed = time.time() - start

    # Verify concurrent execution (total time should be close to max delay, not sum)
    assert elapsed < 1.5  # Should be much less than 1.5s if concurrent
    assert response.overall_status == "success"
    assert len(response.results) == 3

    # Verify latency tracking
    for result in response.results:
        assert result.latency_ms is not None
        assert result.latency_ms > 0


@pytest.mark.asyncio
async def test_invalid_broker_id(mock_session_manager):
    """Test orchestrator handles invalid broker ID gracefully."""
    adapter_registry = {"valid_broker": Mock}
    orchestrator = RequestOrchestrator(mock_session_manager, adapter_registry)

    context = {"account_id": "test_account", "session_data": {}}
    response = await orchestrator.get_portfolio(["invalid_broker"], context)

    assert response.overall_status == "failure"
    assert response.results[0].status == "failed"
    assert response.results[0].code == "INVALID_BROKER"
    assert "Unknown broker" in response.results[0].message


@pytest.mark.asyncio
async def test_correlation_id_generated():
    """Test that UnifiedResponse includes a correlation_id."""
    session_manager = Mock(spec=SessionManager)
    session_manager.ensure_valid_session = AsyncMock(
        return_value=SessionCheckResult(status="valid")
    )

    adapter_registry = {}
    orchestrator = RequestOrchestrator(session_manager, adapter_registry)

    context = {"account_id": "test_account", "session_data": {}}
    response = await orchestrator.get_portfolio(["invalid_broker"], context)

    assert response.correlation_id is not None
    assert isinstance(response.correlation_id, str)
    assert len(response.correlation_id) > 0


@pytest.mark.asyncio
async def test_elapsed_time_tracking(mock_session_manager, mock_adapter_success):
    """Test that elapsed time is tracked correctly."""
    adapter_registry = {"mock": mock_adapter_success}
    orchestrator = RequestOrchestrator(mock_session_manager, adapter_registry)

    context = {"account_id": "test_account", "session_data": {"mock": {}}}
    response = await orchestrator.get_portfolio(["mock"], context)

    assert response.elapsed_ms is not None
    assert isinstance(response.elapsed_ms, int)
    assert response.elapsed_ms >= 0


@pytest.mark.asyncio
async def test_latency_per_broker(mock_session_manager, mock_adapter_success):
    """Test that latency is tracked per broker."""
    adapter_registry = {"mock": mock_adapter_success}
    orchestrator = RequestOrchestrator(mock_session_manager, adapter_registry)

    context = {"account_id": "test_account", "session_data": {"mock": {}}}
    response = await orchestrator.get_portfolio(["mock"], context)

    assert len(response.results) == 1
    assert response.results[0].latency_ms is not None
    assert isinstance(response.results[0].latency_ms, int)
    assert response.results[0].latency_ms >= 0
