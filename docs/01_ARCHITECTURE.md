# Architecture

## Overview
Frontend (React) <-> Backend (FastAPI)
Backend provides:
- MCP Server endpoint (JSON-RPC 2.0 over Streamable HTTP)
- OAuth 2.1 + PKCE endpoints + well-known docs (Amazon-aligned server shape)
- Deterministic simulator + routine engine + diagnostics + fixes
- SQLite persistence (runs, events, snapshots, fixes)

## Components
### Frontend
- HomeownerView: explanation card + friendly timeline
- DeveloperView: workflow graph + trace/evidence drawer + fix actions
- ChatBox: maps to deterministic backend tool calls (no reliance on LLM)

### Backend (FastAPI)
- /mcp (Streamable HTTP JSON-RPC 2.0 endpoint)
- /.well-known/oauth-protected-resource (PRM)
- /.well-known/oauth-authorization-server (auth server metadata)
- /authorize + /token (OAuth 2.1 Authorization Code + PKCE S256)
- Domain logic:
  - simulator: devices, state, fault injection (F1/F2/F3)
  - routine engine: execute routine -> event log
  - diagnostics: classify failure + evidence
  - fixes: propose/apply fix + replay

### Storage (SQLite)
- scenarios and routine specs
- runs + events (timeline)
- device snapshots (actual vs reported + timeOfSample)
- fixes and replay lineage

## Determinism
- Scenario = (seed, base_time, scripted events, injected faults)
- Engine uses only scripted inputs + seed-derived pseudo-randomness (if any)
- Replay reuses same scenario inputs + applied patches

## “Amazon-real” MCP shape
Even though we don’t onboard via CLI during hackathon, the server includes:
- Streamable HTTP JSON-RPC 2.0 handler
- required well-known metadata endpoints
- OAuth 2.1 PKCE flow endpoints
So the codebase resembles what a real add-on server would look like.