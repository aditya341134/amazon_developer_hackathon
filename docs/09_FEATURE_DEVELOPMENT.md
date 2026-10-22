# Feature Development Details

## Feature: Workflow graph
- Compile RoutineSpec -> WorkflowGraph per run
- Record node statuses:
  - SUCCESS / FAILED / SKIPPED
- Map failures to node_id and event_id

## Feature: Evidence model
Evidence items must include:
- device_id
- property
- actual vs reported values
- timeOfSample
- event_id and timestamps

## Feature: Fix patches
### Routine patch examples
- Add retry wrapper to action node
- Add “refresh state if stale” before condition evaluation
- Skip brightness node if not supported

### Integration guidance examples (simulated)
- Recommend implementing ChangeReport promptly
- Correct capability discovery list
- Ensure timeOfSample matches actual state measurement time