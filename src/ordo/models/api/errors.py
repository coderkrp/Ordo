from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
import uuid
from ordo.exceptions import OrdoError


class ApiError(BaseModel):
    error_code: str = Field(
        ..., description="A standardized, machine-readable error code."
    )
    message: str = Field(
        ..., description="A human-readable message explaining the error."
    )
    details: Optional[Dict[str, Any]] = Field(
        None, description="Optional structured details about the error."
    )
    correlation_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="A unique ID for tracing the request."
    )


class ApiException(OrdoError):
    def __init__(self, error: ApiError):
        self.error = error
        super().__init__(error.message)


class SecurityException(OrdoError):
    """Base exception for security-related errors."""

    pass


class CSRFError(SecurityException):
    """Raised when a CSRF check fails."""

    pass
