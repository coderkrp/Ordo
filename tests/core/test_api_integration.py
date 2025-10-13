"""
Integration tests for orchestrator API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from ordo.main import app
from ordo.core.orchestrator import SessionCheckResult
from ordo.models.api.portfolio import Portfolio, Holding, Funds


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_valid_session():
    """Mock SessionManager that returns valid sessions."""
    with patch("ordo.main.get_session_manager") as mock_get_session:
        mock_session_manager = Mock()
        mock_session_manager.ensure_valid_session = AsyncMock(
            return_value=SessionCheckResult(status="valid", message="Session is valid")
        )
        mock_get_session.return_value = mock_session_manager
        yield mock_session_manager


@pytest.fixture
def mock_portfolio_data():
    """Sample portfolio data for testing."""
    return Portfolio(
        holdings=[
            Holding(
                symbol="TCS",
                quantity=5,
                ltp=3500.0,
                avg_price=3400.0,
                pnl=500.0,
                day_pnl=50.0,
                value=17500.0,
            ),
            Holding(
                symbol="INFY",
                quantity=10,
                ltp=1500.0,
                avg_price=1450.0,
                pnl=500.0,
                day_pnl=100.0,
                value=15000.0,
            ),
        ],
        funds=Funds(
            available_balance=100000.0, margin_used=20000.0, total_balance=120000.0
        ),
        total_pnl=1000.0,
        total_day_pnl=150.0,
        total_value=32500.0,
    )


@pytest.mark.integration
def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.integration
def test_portfolio_endpoint_missing_brokers(client, mock_valid_session):
    """Test portfolio endpoint with missing brokers parameter."""
    # Need to provide auth token
    headers = {"Authorization": "Bearer test_token"}

    with patch("ordo.config.settings.ORDO_API_TOKEN", "test_token"):
        response = client.get("/api/v1/portfolio", headers=headers)

    assert response.status_code == 422  # Validation error


@pytest.mark.integration
def test_portfolio_endpoint_empty_brokers(client, mock_valid_session):
    """Test portfolio endpoint with empty brokers list."""
    headers = {"Authorization": "Bearer test_token"}

    with patch("ordo.config.settings.ORDO_API_TOKEN", "test_token"):
        response = client.get(
            "/api/v1/portfolio", params={"brokers": []}, headers=headers
        )

    # Empty list should trigger validation error or 400
    assert response.status_code in [400, 422]


@pytest.mark.integration
def test_portfolio_endpoint_single_broker_success(
    client, mock_valid_session, mock_portfolio_data
):
    """Test portfolio endpoint with single broker returning success."""
    headers = {"Authorization": "Bearer test_token"}

    # Mock the adapter to return portfolio data
    with patch("ordo.config.settings.ORDO_API_TOKEN", "test_token"):
        with patch("ordo.adapters.mock.MockAdapter.get_portfolio") as mock_get_portfolio:
            mock_get_portfolio.return_value = mock_portfolio_data

            response = client.get(
                "/api/v1/portfolio", params={"brokers": ["mock"]}, headers=headers
            )

    assert response.status_code == 200
    data = response.json()

    # Verify UnifiedResponse structure
    assert "overall_status" in data
    assert "results" in data
    assert "correlation_id" in data
    assert "elapsed_ms" in data

    # Verify results
    assert data["overall_status"] == "success"
    assert len(data["results"]) == 1
    assert data["results"][0]["broker_id"] == "mock"
    assert data["results"][0]["status"] == "success"
    assert data["results"][0]["payload"] is not None


@pytest.mark.integration
def test_portfolio_endpoint_multiple_brokers(
    client, mock_valid_session, mock_portfolio_data
):
    """Test portfolio endpoint with multiple brokers."""
    headers = {"Authorization": "Bearer test_token"}

    with patch("ordo.config.settings.ORDO_API_TOKEN", "test_token"):
        with patch("ordo.adapters.mock.MockAdapter.get_portfolio") as mock_get_portfolio:
            mock_get_portfolio.return_value = mock_portfolio_data

            response = client.get(
                "/api/v1/portfolio",
                params={"brokers": ["mock", "mock", "mock"]},
                headers=headers,
            )

    assert response.status_code == 200
    data = response.json()

    assert data["overall_status"] == "success"
    assert len(data["results"]) == 3


@pytest.mark.integration
def test_portfolio_endpoint_invalid_broker(client, mock_valid_session):
    """Test portfolio endpoint with invalid broker ID."""
    headers = {"Authorization": "Bearer test_token"}

    with patch("ordo.config.settings.ORDO_API_TOKEN", "test_token"):
        response = client.get(
            "/api/v1/portfolio",
            params={"brokers": ["invalid_broker"]},
            headers=headers,
        )

    assert response.status_code == 200  # Returns 200 with failure in results
    data = response.json()

    assert data["overall_status"] == "failure"
    assert len(data["results"]) == 1
    assert data["results"][0]["status"] == "failed"
    assert data["results"][0]["code"] == "INVALID_BROKER"


@pytest.mark.integration
def test_portfolio_endpoint_without_auth(client):
    """Test portfolio endpoint without authentication."""
    response = client.get("/api/v1/portfolio", params={"brokers": ["mock"]})

    assert response.status_code == 401  # Unauthorized


@pytest.mark.integration
def test_orders_endpoint_missing_brokers(client, mock_valid_session):
    """Test orders endpoint with missing brokers parameter."""
    headers = {"Authorization": "Bearer test_token"}

    with patch("ordo.config.settings.ORDO_API_TOKEN", "test_token"):
        response = client.post(
            "/api/v1/orders", json={"symbol": "RELIANCE"}, headers=headers
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.integration
def test_orders_endpoint_missing_order_data(client, mock_valid_session):
    """Test orders endpoint with missing order data."""
    headers = {"Authorization": "Bearer test_token"}

    with patch("ordo.config.settings.ORDO_API_TOKEN", "test_token"):
        response = client.post(
            "/api/v1/orders", params={"brokers": ["mock"]}, headers=headers
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.integration
def test_orders_endpoint_success(client, mock_valid_session):
    """Test orders endpoint with valid request."""
    headers = {"Authorization": "Bearer test_token"}
    order_data = {
        "symbol": "RELIANCE",
        "quantity": 10,
        "transaction_type": "BUY",
        "order_type": "LIMIT",
        "price": 2500.0,
    }

    with patch("ordo.config.settings.ORDO_API_TOKEN", "test_token"):
        response = client.post(
            "/api/v1/orders",
            json=order_data,
            params={"brokers": ["mock"]},
            headers=headers,
        )

    assert response.status_code == 200
    data = response.json()

    # Verify UnifiedResponse structure
    assert "overall_status" in data
    assert "results" in data
    assert "correlation_id" in data
    assert "elapsed_ms" in data

    # Verify results
    assert len(data["results"]) == 1
    assert data["results"][0]["broker_id"] == "mock"


@pytest.mark.integration
def test_orders_endpoint_empty_brokers(client, mock_valid_session):
    """Test orders endpoint with empty brokers list."""
    headers = {"Authorization": "Bearer test_token"}
    order_data = {"symbol": "RELIANCE", "quantity": 10}

    with patch("ordo.config.settings.ORDO_API_TOKEN", "test_token"):
        response = client.post(
            "/api/v1/orders",
            json=order_data,
            params={"brokers": []},
            headers=headers,
        )

    # Empty list should trigger 400 or validation error
    assert response.status_code in [400, 422]


@pytest.mark.integration
def test_orders_endpoint_without_auth(client):
    """Test orders endpoint without authentication."""
    order_data = {"symbol": "RELIANCE", "quantity": 10}

    response = client.post(
        "/api/v1/orders", json=order_data, params={"brokers": ["mock"]}
    )

    assert response.status_code == 401  # Unauthorized


@pytest.mark.integration
def test_unified_response_structure(client, mock_valid_session, mock_portfolio_data):
    """Test that UnifiedResponse follows the correct schema."""
    headers = {"Authorization": "Bearer test_token"}

    with patch("ordo.config.settings.ORDO_API_TOKEN", "test_token"):
        with patch("ordo.adapters.mock.MockAdapter.get_portfolio") as mock_get_portfolio:
            mock_get_portfolio.return_value = mock_portfolio_data

            response = client.get(
                "/api/v1/portfolio", params={"brokers": ["mock"]}, headers=headers
            )

    assert response.status_code == 200
    data = response.json()

    # Verify all required fields are present
    required_fields = ["overall_status", "results", "correlation_id", "elapsed_ms"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Verify overall_status is one of the allowed values
    assert data["overall_status"] in ["success", "partial_success", "failure"]

    # Verify results structure
    assert isinstance(data["results"], list)
    if data["results"]:
        result = data["results"][0]
        required_result_fields = ["broker_id", "status", "code", "message", "payload"]
        for field in required_result_fields:
            assert field in result, f"Missing required result field: {field}"

        # Verify status is one of allowed values
        assert result["status"] in ["success", "failed", "pending"]

    # Verify correlation_id is a non-empty string
    assert isinstance(data["correlation_id"], str)
    assert len(data["correlation_id"]) > 0

    # Verify elapsed_ms is a positive integer
    assert isinstance(data["elapsed_ms"], int)
    assert data["elapsed_ms"] >= 0
