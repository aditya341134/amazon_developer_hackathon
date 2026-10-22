# PRD — Routine Doctor (Alexa+ MCP Add-on style) + Web Simulator

## Summary
Routine Doctor explains smart home failures in a way that both:
- Homeowners understand (what broke / when / why / what to do)
- Developers can fix (exact timestamps, traces, evidence, fixes, replay validation)

We deliver:
- React web simulator (the “experience”)
- FastAPI backend implementing an Alexa+ compatible MCP server shape:
  - MCP spec 2025-11-25+ expectations (JSON-RPC 2.0, Streamable HTTP)
  - OAuth 2.1 Auth Code + PKCE (S256) endpoints + well-known metadata
  - PRM document (RFC 9728) at the well-known URI

We do not use official Alexa tools during the hackathon; all device behavior is simulated deterministically.

## Users
### Homeowner (end user)
Needs:
- plain-language explanation
- quick next steps
- confidence that fixes work

### Smart home developer / integrator
Needs:
- workflow graph + node-level failure
- directive/response evidence
- state vs reported state + timeOfSample
- capability declaration vs runtime mismatch
- recommended fixes + replay

## Problem
Smart home routines fail due to:
- F1 Device unreachable
- F2 Stale/incorrect state (bad/outdated timeOfSample; missing change reporting)
- F3 Capability mismatch (declared capability not actually supported)

Existing assistants rarely provide deterministic, evidence-based debugging + replay.

## Goals (MVP)
1. Deterministic scenario runner
2. Timeline: what happened (user + dev)
3. Workflow graph (developer view)
4. Diagnose F1/F2/F3 with evidence pointers
5. Propose and apply fixes (routine-level + integration-level guidance)
6. Replay same scenario: FAIL → PASS

## Non-goals
- Real device control / production integrations
- Full Alexa certification workflow (we include add-on package shape, but do not deploy)
- Multi-user accounts or complex permissions

## Demo success criteria (< 3 min)
- Run a failing scenario
- Show homeowner explanation
- Show developer workflow graph + evidence
- Apply fix
- Replay passes, show diff summary