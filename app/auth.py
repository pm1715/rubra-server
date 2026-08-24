from __future__ import annotations

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings

_header = APIKeyHeader(name="X-Rubra-API-Key", auto_error=False)


async def require_api_key(key: str | None = Security(_header)) -> None:
    """
    Validate X-Rubra-API-Key header.
    If RUBRA_API_KEY is not configured the server runs in open dev mode
    and all requests are accepted.
    """
    if settings.rubra_api_key is None:
        return  # dev mode — no auth
    if key != settings.rubra_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Pass X-Rubra-API-Key header.",
        )
