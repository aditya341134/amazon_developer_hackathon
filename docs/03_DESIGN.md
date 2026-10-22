# Design (UX)

## Top-level layout
- Routine selector
- Scenario selector
- Run button
- Tabs: Homeowner | Developer
- Right side: Chat box (optional assist)

## Homeowner tab (plain language)
- Card: What broke / when / why / what to do
- Timeline: friendly summaries, minimal jargon

## Developer tab (debugger)
- Workflow graph:
  - nodes: Trigger / Condition / Action / Assert
  - colors: success / failed / skipped
- Node detail drawer:
  - directive payload
  - response payload (ErrorResponse classification)
  - device snapshot:
    - actual state vs reported state
    - timeOfSample
    - endpoint health
    - declared vs actual capabilities
- Fix panel:
  - propose fixes
  - apply fix
  - replay run
  - diff summary (FAIL->PASS evidence)

## Chat box behavior (deterministic)
Chat is not “free-form AI.”
It maps user prompts to tool calls:
- “why failed” -> explain_failure
- “suggest fix” -> propose_fixes
- “apply fix #1” -> apply_fix
- “replay” -> replay_run