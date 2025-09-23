from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from ordo.config import settings
from ordo.models.api.errors import ApiError

bearer_scheme = HTTPBearer(auto_error=False)


async def verify_api_token(request: Request):
    """
    Dependency that verifies the API token from the Authorization header.

    Returns HTTP 401 Unauthorized if the token is missing or invalid.
    """
    credentials: HTTPAuthorizationCredentials | None = await bearer_scheme(request)
    if (
        not credentials
        or credentials.scheme != "Bearer"
        or credentials.credentials != settings.ORDO_API_TOKEN
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ApiError(
                error_code="UNAUTHORIZED", message="Invalid or missing API token."
            ).model_dump(mode="json"),
        )
    return None  # Indicates success, request proceeds


async def authentication_middleware(request: Request, call_next):
    """
    A FastAPI middleware that checks for a static bearer token in the Authorization header
    for all routes except the documentation.
    """
    if request.url.path in ["/docs", "/openapi.json"]:
        return await call_next(request)

    response = await verify_api_token(request)
    if response:
        return response

    return await call_next(request)
