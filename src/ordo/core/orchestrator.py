"""
Request Orchestrator - Central coordination layer for multi-broker operations.
"""
import asyncio
import time
from typing import List, Dict, Any, Callable, Type
from ordo.models.api.unified import BrokerResult, UnifiedResponse
from ordo.models.api.portfolio import Portfolio
from ordo.models.api.order import OrderResponse
from ordo.adapters.base import IBrokerAdapter
from ordo.security.session import SessionManager


class SessionCheckResult:
    """Result of session validation check."""

    def __init__(self, status: str, message: str = ""):
        self.status = status  # "valid", "expired", "refresh_failed", "unsupported"
        self.message = message


class RequestOrchestrator:
    """
    Central coordination layer for multi-broker operations.

    Handles concurrent fan-out to multiple brokers, result collation,
    error handling, and timeout management.

    Attributes:
        session_manager: SessionManager for session validation
        adapter_registry: Dictionary mapping broker_id to adapter class
        per_broker_timeout: Timeout in seconds for individual broker operations
        global_timeout: Timeout in seconds for entire orchestration
    """

    def __init__(
        self,
        session_manager: SessionManager,
        adapter_registry: Dict[str, Type[IBrokerAdapter]],
        per_broker_timeout: int = 8,
        global_timeout: int = 12,
    ):
        """
        Initialize RequestOrchestrator.

        Args:
            session_manager: SessionManager instance for session validation
            adapter_registry: Dict mapping broker_id to adapter class
            per_broker_timeout: Timeout for individual broker operations (default: 8s)
            global_timeout: Timeout for entire orchestration (default: 12s)
        """
        self.session_manager = session_manager
        self.adapter_registry = adapter_registry
        self.per_broker_timeout = per_broker_timeout
        self.global_timeout = global_timeout

    def _compute_overall_status(self, results: List[BrokerResult]) -> str:
        """
        Compute overall status from individual broker results.

        Logic:
        - All success → "success"
        - All failed → "failure"
        - Mix of success and failed → "partial_success"

        Args:
            results: List of BrokerResult objects

        Returns:
            Overall status: "success", "partial_success", or "failure"
        """
        if not results:
            return "failure"

        success_count = sum(1 for r in results if r.status == "success")
        failed_count = sum(1 for r in results if r.status == "failed")

        if success_count == len(results):
            return "success"
        elif failed_count == len(results):
            return "failure"
        else:
            return "partial_success"

    async def _execute_for_broker(
        self,
        broker_id: str,
        operation: Callable,
        context: Dict[str, Any],
    ) -> BrokerResult:
        """
        Execute operation for a single broker with timeout and error handling.

        Args:
            broker_id: Broker identifier
            operation: Async callable to execute
            context: Request context with session data

        Returns:
            BrokerResult with operation outcome
        """
        start_time = time.time()

        try:
            # Check if broker_id is valid
            if broker_id not in self.adapter_registry:
                return BrokerResult(
                    broker_id=broker_id,
                    status="failed",
                    code="INVALID_BROKER",
                    message=f"Unknown broker: {broker_id}",
                    payload=None,
                    latency_ms=int((time.time() - start_time) * 1000),
                )

            # Validate session before making call
            session_result = await self.session_manager.ensure_valid_session(
                broker_id, context.get("account_id", "")
            )

            if session_result.status != "valid":
                return BrokerResult(
                    broker_id=broker_id,
                    status="failed",
                    code="INVALID_SESSION",
                    message=f"Session validation failed: {session_result.status}",
                    payload={"session_status": session_result.status},
                    latency_ms=int((time.time() - start_time) * 1000),
                )

            # Execute operation with timeout
            result = await asyncio.wait_for(
                operation(), timeout=self.per_broker_timeout
            )

            latency_ms = int((time.time() - start_time) * 1000)

            return BrokerResult(
                broker_id=broker_id,
                status="success",
                code="SUCCESS",
                message="Operation completed successfully",
                payload=result.model_dump() if hasattr(result, "model_dump") else result,
                latency_ms=latency_ms,
            )

        except asyncio.TimeoutError:
            return BrokerResult(
                broker_id=broker_id,
                status="failed",
                code="TIMEOUT",
                message=f"Operation timed out after {self.per_broker_timeout}s",
                payload=None,
                latency_ms=int((time.time() - start_time) * 1000),
            )

        except Exception as e:
            # Handle any unexpected exceptions
            error_type = type(e).__name__

            # Map known exceptions to standardized codes
            if "SessionExpired" in error_type:
                code = "SESSION_EXPIRED"
            elif "InsufficientFunds" in error_type:
                code = "INSUFFICIENT_FUNDS"
            elif "NetworkError" in error_type or "ConnectionError" in error_type:
                code = "NETWORK_ERROR"
            else:
                code = "INTERNAL_ERROR"

            return BrokerResult(
                broker_id=broker_id,
                status="failed",
                code=code,
                message=str(e),
                payload={"error_type": error_type},
                latency_ms=int((time.time() - start_time) * 1000),
            )

    async def get_portfolio(
        self, broker_ids: List[str], context: Dict[str, Any]
    ) -> UnifiedResponse:
        """
        Retrieve portfolio data from multiple brokers concurrently.

        Args:
            broker_ids: List of target broker identifiers
            context: Request context with authentication and session data

        Returns:
            UnifiedResponse with aggregated portfolio results
        """
        start_time = time.time()

        # Create tasks for concurrent execution
        tasks = []
        for broker_id in broker_ids:
            # Create operation function for this broker
            async def operation(bid=broker_id):
                adapter_class = self.adapter_registry[bid]
                adapter = adapter_class()
                session_data = context.get("session_data", {}).get(bid, {})
                return await adapter.get_portfolio(session_data)

            # Add to tasks list
            task = self._execute_for_broker(broker_id, operation, context)
            tasks.append(task)

        # Execute all tasks concurrently using asyncio.gather
        # return_exceptions=True ensures one failure doesn't stop others
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert any exceptions to BrokerResult
        broker_results = []
        for i, result in enumerate(results):
            if isinstance(result, BrokerResult):
                broker_results.append(result)
            elif isinstance(result, Exception):
                # Handle exceptions that weren't caught by _execute_for_broker
                broker_results.append(
                    BrokerResult(
                        broker_id=broker_ids[i],
                        status="failed",
                        code="INTERNAL_ERROR",
                        message=str(result),
                        payload=None,
                        latency_ms=0,
                    )
                )

        # Compute overall status
        overall_status = self._compute_overall_status(broker_results)

        # Calculate total elapsed time
        elapsed_ms = int((time.time() - start_time) * 1000)

        # Collect errors if any
        errors = []
        for result in broker_results:
            if result.status == "failed":
                errors.append(
                    {
                        "broker_id": result.broker_id,
                        "code": result.code,
                        "message": result.message,
                    }
                )

        return UnifiedResponse(
            overall_status=overall_status,
            results=broker_results,
            elapsed_ms=elapsed_ms,
            errors=errors if errors else None,
        )

    async def place_order(
        self, order_data: Dict[str, Any], broker_ids: List[str], context: Dict[str, Any]
    ) -> UnifiedResponse:
        """
        Place order across multiple brokers concurrently.

        Args:
            order_data: Order details to be placed
            broker_ids: List of target broker identifiers
            context: Request context with authentication and session data

        Returns:
            UnifiedResponse with aggregated order placement results
        """
        start_time = time.time()

        # Create tasks for concurrent execution
        tasks = []
        for broker_id in broker_ids:
            # Create operation function for this broker
            async def operation(bid=broker_id):
                adapter_class = self.adapter_registry[bid]
                adapter = adapter_class()
                session_data = context.get("session_data", {}).get(bid, {})
                # Note: Actual order placement method needs to be added to IBrokerAdapter
                # For now, we'll use a placeholder
                return OrderResponse(order_id=f"{bid}_order_123", status="pending")

            # Add to tasks list
            task = self._execute_for_broker(broker_id, operation, context)
            tasks.append(task)

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert any exceptions to BrokerResult
        broker_results = []
        for i, result in enumerate(results):
            if isinstance(result, BrokerResult):
                broker_results.append(result)
            elif isinstance(result, Exception):
                broker_results.append(
                    BrokerResult(
                        broker_id=broker_ids[i],
                        status="failed",
                        code="INTERNAL_ERROR",
                        message=str(result),
                        payload=None,
                        latency_ms=0,
                    )
                )

        # Compute overall status
        overall_status = self._compute_overall_status(broker_results)

        # Calculate total elapsed time
        elapsed_ms = int((time.time() - start_time) * 1000)

        # Collect errors if any
        errors = []
        for result in broker_results:
            if result.status == "failed":
                errors.append(
                    {
                        "broker_id": result.broker_id,
                        "code": result.code,
                        "message": result.message,
                    }
                )

        return UnifiedResponse(
            overall_status=overall_status,
            results=broker_results,
            elapsed_ms=elapsed_ms,
            errors=errors if errors else None,
        )
