from fastapi import Request
from fastapi.responses import ORJSONResponse
from .config import settings


async def api_key_middleware(request: Request, call_next):
    """
    Simple API key authentication middleware.

    - Skips health/docs for monitoring and tooling.
    - In dev environment, localhost calls are allowed without API key.
    - In non-dev environments, a valid X-API-Key (or api_key query param) is required.
    """
    # Health, docs, and Static Frontend files should always be accessible
    path = request.url.path
    if path in {"/", "/docs", "/openapi.json", "/api/v1/health", "/health"} or path.startswith(("/static", "/js", "/css")):
        return await call_next(request)

    client_host = request.client.host if request.client else None

    # Localhost convenience only in dev environment
    if settings.ENV == "dev" and client_host in {"127.0.0.1", "localhost", "::1"}:
        return await call_next(request)

    api_key = request.headers.get("X-API-Key")
    if not api_key:
        api_key = request.query_params.get("api_key")

    if not api_key or api_key != settings.API_KEY:
        return ORJSONResponse(
            status_code=403,
            content={"code": "FORBIDDEN", "message": "Invalid or missing API Key"},
        )

    return await call_next(request)
