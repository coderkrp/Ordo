"""
Unified response models for multi-broker orchestrator operations.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from uuid import uuid4


class BrokerResult(BaseModel):
    """
    Represents the result from a single broker operation.

    Attributes:
        broker_id: Unique identifier for the broker (e.g., "fyers", "hdfc")
        status: Operation status for this broker
        code: Standardized error/success code (e.g., "INSUFFICIENT_FUNDS", "TIMEOUT")
        message: Human-readable message describing the result
        payload: Broker-specific response data (order ID, portfolio data, etc.)
        latency_ms: Time taken for this broker's operation in milliseconds
    """
    broker_id: str = Field(..., description="Broker identifier")
    status: Literal["success", "failed", "pending"]
    code: Optional[str] = Field(None, description="Standardized result code")
    message: Optional[str] = Field(None, description="Human-readable message")
    payload: Optional[dict] = Field(None, description="Broker-specific data")
    latency_ms: Optional[int] = Field(None, description="Operation latency")


class UnifiedResponse(BaseModel):
    """
    Aggregates results from multiple broker operations into a single response.

    Attributes:
        overall_status: Computed status across all brokers
            - "success": All broker operations succeeded
            - "partial_success": At least one success and at least one failure
            - "failure": All broker operations failed
        results: Individual results from each targeted broker
        correlation_id: UUID for request tracking and debugging
        elapsed_ms: Total time for the entire multi-broker operation
        errors: Aggregated errors if any occurred
    """
    overall_status: Literal["success", "partial_success", "failure"]
    results: List[BrokerResult] = Field(default_factory=list)
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    elapsed_ms: int
    errors: Optional[List[dict]] = None  # ApiError schema
