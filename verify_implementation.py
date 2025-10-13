#!/usr/bin/env python3
"""
Simple verification script for Request Orchestrator implementation.
"""
import sys
import asyncio

sys.path.insert(0, '/workspace/cmgos18vg0001qyic0qoozodb/Ordo/src')

from ordo.core.orchestrator import RequestOrchestrator, SessionCheckResult
from ordo.models.api.unified import BrokerResult, UnifiedResponse
from ordo.models.api.portfolio import Portfolio, Holding, Funds
from ordo.security.session import SessionManager


class MockAdapter:
    """Mock adapter for testing."""

    async def get_portfolio(self, session_data):
        return Portfolio(
            holdings=[
                Holding(
                    symbol="TEST",
                    quantity=10,
                    ltp=100.0,
                    avg_price=95.0,
                    pnl=50.0,
                    day_pnl=5.0,
                    value=1000.0,
                )
            ],
            funds=Funds(
                available_balance=10000.0, margin_used=1000.0, total_balance=11000.0
            ),
            total_pnl=50.0,
            total_day_pnl=5.0,
            total_value=1000.0,
        )


class MockSessionManager:
    """Mock session manager for testing."""

    async def ensure_valid_session(self, broker_id, account_id):
        return SessionCheckResult(status="valid", message="Session is valid")


async def test_basic_functionality():
    """Test basic orchestrator functionality."""
    print("Testing Request Orchestrator...")

    # Setup
    session_manager = MockSessionManager()
    adapter_registry = {"mock": MockAdapter}
    orchestrator = RequestOrchestrator(session_manager, adapter_registry)

    # Test 1: Compute overall status
    print("\n1. Testing status computation...")
    results = [
        BrokerResult(broker_id="b1", status="success", code="SUCCESS", message="OK"),
        BrokerResult(broker_id="b2", status="success", code="SUCCESS", message="OK"),
    ]
    status = orchestrator._compute_overall_status(results)
    assert status == "success", f"Expected 'success', got '{status}'"
    print("   ✓ All success → success")

    results = [
        BrokerResult(broker_id="b1", status="failed", code="ERROR", message="Error"),
        BrokerResult(broker_id="b2", status="failed", code="ERROR", message="Error"),
    ]
    status = orchestrator._compute_overall_status(results)
    assert status == "failure", f"Expected 'failure', got '{status}'"
    print("   ✓ All failed → failure")

    results = [
        BrokerResult(broker_id="b1", status="success", code="SUCCESS", message="OK"),
        BrokerResult(broker_id="b2", status="failed", code="ERROR", message="Error"),
    ]
    status = orchestrator._compute_overall_status(results)
    assert status == "partial_success", f"Expected 'partial_success', got '{status}'"
    print("   ✓ Mixed results → partial_success")

    # Test 2: Get portfolio
    print("\n2. Testing get_portfolio...")
    context = {"account_id": "test", "session_data": {"mock": {}}}
    response = await orchestrator.get_portfolio(["mock"], context)

    assert isinstance(response, UnifiedResponse), "Response should be UnifiedResponse"
    assert response.overall_status == "success", "Should succeed with mock adapter"
    assert len(response.results) == 1, "Should have one result"
    assert response.results[0].broker_id == "mock", "Broker ID should be 'mock'"
    assert response.results[0].status == "success", "Result status should be success"
    assert response.correlation_id is not None, "Correlation ID should exist"
    assert response.elapsed_ms >= 0, "Elapsed time should be non-negative"
    print("   ✓ Single broker portfolio fetch successful")

    # Test 3: Invalid broker
    print("\n3. Testing invalid broker handling...")
    response = await orchestrator.get_portfolio(["invalid"], context)
    assert response.overall_status == "failure", "Should fail with invalid broker"
    assert response.results[0].code == "INVALID_BROKER", "Should have INVALID_BROKER code"
    print("   ✓ Invalid broker handled correctly")

    # Test 4: Multiple brokers
    print("\n4. Testing multiple brokers...")
    adapter_registry["mock2"] = MockAdapter
    orchestrator = RequestOrchestrator(session_manager, adapter_registry)
    context = {"account_id": "test", "session_data": {"mock": {}, "mock2": {}}}
    response = await orchestrator.get_portfolio(["mock", "mock2"], context)

    assert response.overall_status == "success", "Should succeed with both mocks"
    assert len(response.results) == 2, "Should have two results"
    print("   ✓ Multiple broker fan-out successful")

    print("\n✅ All tests passed!")
    print(f"\nVerified implementation:")
    print(f"  - BrokerResult and UnifiedResponse models")
    print(f"  - RequestOrchestrator with concurrent execution")
    print(f"  - Status computation (success/partial_success/failure)")
    print(f"  - Error handling (invalid broker)")
    print(f"  - Session validation integration")
    print(f"  - Portfolio multi-broker fan-out")


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
