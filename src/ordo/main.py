from fastapi import FastAPI, APIRouter, HTTPException, status, Body
from ordo.security.authentication import authentication_middleware
from ordo.config import get_adapter
from ordo.models.api.login import (
    LoginInitiateRequest,
    LoginInitiateResponse,
    LoginCompleteRequest,
    LoginCompleteResponse,
)
from ordo.models.api.errors import ApiError

app = FastAPI()

app.middleware("http")(authentication_middleware)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/protected")
async def protected_route():
    return {"message": "You have accessed a protected route."}


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


app.include_router(auth_router)
