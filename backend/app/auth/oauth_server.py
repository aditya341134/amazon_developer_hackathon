from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from app.auth.tokens import mint_token
from app.util.ids import new_id

router = APIRouter()

# In-memory store for pending PKCE authorization codes
_AUTH_CODES: dict[str, dict] = {}


class TokenRequest(BaseModel):
    grant_type: str = "authorization_code"
    code: Optional[str] = None
    redirect_uri: Optional[str] = None
    client_id: Optional[str] = None
    code_verifier: Optional[str] = None
    resource: Optional[str] = None


@router.get("/authorize")
def authorize(
    client_id: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    response_type: Optional[str] = "code",
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = "S256",
    state: Optional[str] = None,
):
    code = new_id("authcode")
    _AUTH_CODES[code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
    }

    return {
        "code": code,
        "state": state,
        "note": "Authorization code issued successfully. Use this code with PKCE code_verifier to obtain an access token.",
    }


@router.post("/token")
async def token(request: Request):
    # Accept both JSON body and application/x-www-form-urlencoded
    content_type = request.headers.get("content-type", "")
    code = None
    if "application/json" in content_type:
        try:
            body = await request.json()
            code = body.get("code")
        except Exception:
            pass
    elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        try:
            form = await request.form()
            code = form.get("code")
        except Exception:
            pass
    else:
        try:
            body = await request.json()
            code = body.get("code")
        except Exception:
            pass

    tok = mint_token()
    return {
        "access_token": tok.access_token,
        "token_type": tok.token_type,
        "expires_in": tok.expires_in,
        "scope": "mcp.tools",
    }