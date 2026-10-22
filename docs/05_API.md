# API (Non-MCP)

Primary integration is via MCP JSON-RPC tools.
We keep REST minimal.

## REST
GET /health
-> { "ok": true }

## Well-known (Auth discovery)
GET /.well-known/oauth-protected-resource
GET /.well-known/oauth-authorization-server

## OAuth endpoints
GET /authorize
POST /token

(Used by Alexa+ onboarding in real deployments; included here for correctness and future readiness.)