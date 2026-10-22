# TRD — Technical Requirements

## Protocol / Alexa+ alignment (from Alexa+ MCP QuickStart)
- Transport: Streamable HTTP
- Protocol: JSON-RPC 2.0
- Spec: MCP 2025-11-25+ behavior expectations
- Remote URL readiness: must be tunnelable (cloudflared/ngrok) without code changes

## Auth requirements (implemented for correctness)
- Unauthenticated MCP requests return 401 Unauthorized **without** WWW-Authenticate header
- PRM document at: /.well-known/oauth-protected-resource  (RFC 9728)
- Auth server metadata at: /.well-known/oauth-authorization-server
- OAuth 2.1 Authorization Code + PKCE (S256)
- Token usage: Bearer token in Authorization header only (no querystring)

Note: for hackathon demo, we can include a “dev mode” that mints tokens locally, but the endpoints exist and behave correctly.

## Performance
- Target < 500ms round-trip per tool call locally (aligns with quickstart guidance)

## Stack
- Frontend: React + TypeScript + React Flow
- Backend: FastAPI + Pydantic
- DB: SQLite