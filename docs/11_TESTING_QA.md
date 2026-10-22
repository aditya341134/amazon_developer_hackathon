# Testing & QA

## Backend unit tests
- tools/list returns tool catalog
- tools/call executes each tool end-to-end
- replay is deterministic pre-fix
- apply_fix changes outcome (FAIL -> PASS)
- F1/F2/F3 classification correctness

## “Amazon shape” tests (important)
- unauthenticated /mcp returns 401 WITHOUT WWW-Authenticate
- PRM endpoint exists and is valid JSON
- auth server metadata endpoint exists and includes S256 in code_challenge_methods_supported

## Frontend QA checklist
- Run scenario -> timeline populates
- Developer graph highlights failure node
- Propose fix -> apply -> replay -> pass