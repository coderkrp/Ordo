from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class LoginInitiateRequest(BaseModel):
    broker: str = Field(
        ..., description="The name of the broker to initiate login for."
    )
    credentials: Optional[Dict[str, Any]] = Field(
        None, description="Optional credentials for login initiation."
    )


class LoginInitiateResponse(BaseModel):
    login_url: Optional[str] = Field(
        None, description="URL to complete the login process, if applicable."
    )
    session_data: Dict[str, Any] = Field(
        ..., description="Session data required for completing the login."
    )
    message: str = Field(..., description="Status message for login initiation.")


class LoginCompleteRequest(BaseModel):
    broker: str = Field(
        ..., description="The name of the broker to complete login for."
    )
    session_data: Dict[str, Any] = Field(
        ..., description="Session data obtained from the initiate login step."
    )
    auth_code: str = Field(
        ..., description="Authorization code from the broker's callback."
    )
    response_state: str = Field(
        ..., description="State from the broker's callback for CSRF protection."
    )


class LoginCompleteResponse(BaseModel):
    access_token: str = Field(..., description="Access token upon successful login.")
    message: str = Field(..., description="Status message for login completion.")
