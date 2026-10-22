# Auth dependency stub.
# When AUTH_ENABLED=1, enforce Bearer token here for /mcp.
from fastapi import Header, HTTPException
from app.settings import settings


def require_bearer_token(authorization: str | None = Header(default=None)):
    if not settings.auth_enabled:
        return None
    if not authorization or not authorization.lower().startswith("bearer "):
        # Alexa+ QuickStart: 401 WITHOUT WWW-Authenticate header
        raise HTTPException(status_code=401, detail="Unauthorized", headers={})
    return authorization