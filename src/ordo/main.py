from fastapi import FastAPI, APIRouter, HTTPException, status, Body, Depends, Query
from typing import List, Dict, Any
from ordo.security.authentication import authentication_middleware
from ordo.config import get_adapter, settings
from ordo.models.api.login import (
    LoginInitiateRequest,
    LoginInitiateResponse,
    LoginCompleteRequest,
    LoginCompleteResponse,
)
from ordo.models.api.errors import ApiError
from ordo.models.api.unified import UnifiedResponse
from ordo.core.orchestrator import RequestOrchestrator
from ordo.security.session import SessionManager
from ordo.adapters.mock import MockAdapter
from ordo.adapters.fyers import FyersAdapter
from ordo.adapters.hdfc import HDFCAdapter

app = FastAPI()

app.middleware("http")(authentication_middleware)


def get_session_manager() -> SessionManager:
    """Provide SessionManager instance."""
    return SessionManager(secret_key=settings.SECRET_KEY)


def get_orchestrator() -> RequestOrchestrator:
    """Provide RequestOrchestrator instance with dependencies."""
    session_manager = get_session_manager()
    adapter_registry = {
        "mock": MockAdapter,
        "fyers": FyersAdapter,
        "hdfc": HDFCAdapter,
    }
    return RequestOrchestrator(session_manager, adapter_registry)


def get_request_context() -> Dict[str, Any]:
    """
    Provide request context for orchestrator operations.
    
    In a real implementation, this would extract user/session data from the request.
    For now, returns a minimal context.
    """
    return {
        "account_id": "default_account",
        "session_data": {},
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/protected")
async def protected_route():
    return {"message": "You have accessed a protected route."}


# API v1 Router for orchestrated operations
api_v1_router = APIRouter(prefix="/api/v1", tags=["Multi-Broker Operations"])


@api_v1_router.get(
    "/portfolio",
    response_model=UnifiedResponse,
    summary="Get portfolio from multiple brokers",
    response_description="Unified portfolio data from all requested brokers",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ApiError,
            "description": "Invalid request - at least one broker required",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApiError,
            "description": "Internal server error",
        },
    },
)
async def get_portfolio(
    brokers: List[str] = Query(..., description="List of broker IDs to query"),
    orchestrator: RequestOrchestrator = Depends(get_orchestrator),
    context: Dict[str, Any] = Depends(get_request_context),
) -> UnifiedResponse:
    """
    Retrieve unified portfolio across multiple brokers.
    
    Returns aggregated holdings, positions, and funds from all specified brokers.
    Supports partial success - if one broker fails, others still return data.
    """
    if not brokers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one broker ID is required",
        )

    try:
        return await orchestrator.get_portfolio(brokers, context)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@api_v1_router.post(
    "/orders",
    response_model=UnifiedResponse,
    summary="Place order across multiple brokers",
    response_description="Unified order placement results from all requested brokers",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ApiError,
            "description": "Invalid request - order data or brokers missing",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApiError,
            "description": "Internal server error",
        },
    },
)
async def place_order(
    order_data: Dict[str, Any] = Body(..., description="Order details to place"),
    brokers: List[str] = Query(..., description="List of broker IDs to place order"),
    orchestrator: RequestOrchestrator = Depends(get_orchestrator),
    context: Dict[str, Any] = Depends(get_request_context),
) -> UnifiedResponse:
    """
    Place order across multiple brokers concurrently.
    
    Supports partial success scenarios - if one broker fails, others may still succeed.
    Returns unified response with per-broker results and overall status.
    """
    if not brokers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one broker ID is required",
        )

    if not order_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order data is required",
        )

    try:
        return await orchestrator.place_order(order_data, brokers, context)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


auth_router = APIRouter(prefix="/login", tags=["Authentication"])


@auth_router.post(
    "/initiate",
    response_model=LoginInitiateResponse,
    summary="Initiate login for a broker",
    response_description="Login initiation successful, returns login URL and session data",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ApiError,
            "description": "Invalid broker or credentials",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApiError,
            "description": "Internal server error",
        },
    },
)
async def initiate_login(
    request: LoginInitiateRequest = Body(..., description="Login initiation request"),
):

    try:
        adapter = get_adapter(request.broker)

        response_data = await adapter.initiate_login(request.credentials)
        return LoginInitiateResponse(
            login_url=response_data.get("login_url"),
            session_data=response_data.get("session_data", {}),
            message="Login initiation successful",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@auth_router.post(
    "/complete",
    response_model=LoginCompleteResponse,
    summary="Complete login for a broker",
    response_description="Login completion successful, returns access token",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ApiError,
            "description": "Invalid OTP or session data",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApiError,
            "description": "Internal server error",
        },
    },
)
async def complete_login(
    request: LoginCompleteRequest = Body(..., description="Login completion request"),
):
    try:
        adapter = get_adapter(request.broker)
        session_data = request.session_data
        session_data["auth_code"] = request.auth_code
        session_data["response_state"] = request.response_state
        response_data = await adapter.complete_login(session_data)
        return LoginCompleteResponse(
            access_token=response_data.get("access_token", ""),
            message="Login completion successful",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


app.include_router(api_v1_router)
app.include_router(auth_router)
