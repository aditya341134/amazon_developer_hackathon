from fastapi import APIRouter
from app.settings import settings

router = APIRouter()


@router.get("/.well-known/oauth-protected-resource")
def prm():
    # RFC 9728 Protected Resource Metadata (PRM)
    base = settings.public_base_url
    return {
        "resource": base,
        "authorization_servers": [base],
        "scopes_supported": ["mcp.tools"],
        "bearer_methods_supported": ["header"],
    }


@router.get("/.well-known/oauth-authorization-server")
def oauth_server_metadata():
    base = settings.public_base_url
    return {
        "issuer": base,
        "authorization_endpoint": f"{base}/authorize",
        "token_endpoint": f"{base}/token",
        "code_challenge_methods_supported": ["S256"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "token_endpoint_auth_methods_supported": ["none", "client_secret_post"],
    }