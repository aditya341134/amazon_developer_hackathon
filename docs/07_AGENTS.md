# Agents (Deterministic, evidence-based)

We intentionally avoid LLM dependency for core correctness.

## Agents (internal orchestrators)
### Run Orchestrator
- Executes routine on scenario
- Writes event log + snapshots

### Diagnosis Agent
- Classifies F1/F2/F3 with evidence pointers:
  - F1: EndpointHealth unreachable -> directive failure
  - F2: reported state stale/incorrect vs actual; timeOfSample too old
  - F3: declared capabilities differ from actual; directive fails as unsupported

### Fix Agent
- Produces:
  - routine-level patch (graph/routine changes: retry, refresh state, degrade gracefully)
  - integration-level guidance patch (scenario/integration config: reporting cadence, capability declaration)

### Narrative Formatter
- Converts diagnosis into:
  - homeowner explanation (plain)
  - developer explanation (trace + evidence)