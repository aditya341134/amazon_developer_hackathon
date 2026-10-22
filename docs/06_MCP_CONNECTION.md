# MCP Connection (Alexa+ QuickStart-aligned)

## Transport & Protocol
- Streamable HTTP
- JSON-RPC 2.0

## MCP Endpoint
POST /mcp
- Requires Authorization: Bearer <token> (when auth enabled)
- If unauthenticated: return 401 WITHOUT WWW-Authenticate header (per guide)

## MCP Core methods (minimum to support tool usage)
Your server should support the MCP-required introspection patterns per spec.
At minimum for our simulator:
- tools/list
- tools/call
Optionally:
- resources/list
- resources/read

(Exact method names/shape should match the MCP spec and the SDK you choose; do not hand-roll inconsistently.)

## Tool catalog (MVP)
- list_routines
- list_scenarios
- run_scenario
- get_timeline
- get_workflow_graph
- explain_failure
- propose_fixes
- apply_fix
- replay_run

## Auth (OAuth 2.1 PKCE S256)
### 1) PRM (RFC 9728)
Host protected resource metadata at:
- /.well-known/oauth-protected-resource

Must describe:
- resource (canonical base URL for this MCP server)
- authorization_servers (issuer URLs)

### 2) Auth server metadata
Host at:
- /.well-known/oauth-authorization-server

Must include:
- authorization_endpoint
- token_endpoint
- code_challenge_methods_supported includes ["S256"]  (required)

### 3) Authorization Code flow + PKCE
- /authorize issues an authorization code
- /token exchanges code + code_verifier for access token
Token requests must include:
- resource parameter (canonical MCP server URI)
- code_verifier (PKCE)

### 4) Token usage
- Every authenticated request uses:
  Authorization: Bearer <token>
- Never send token in query string

## Local development vs “remote URL”
Alexa+ requires a remote URL. For hackathon:
- run locally for UI demo
- optionally expose via tunnel for realism:
  - cloudflared tunnel --url http://localhost:8000
Then set the PRM resource and canonical URI to the tunneled HTTPS URL.

## Performance
Keep tool handlers fast (<500ms locally).
Avoid long streaming responses; our payloads are small.