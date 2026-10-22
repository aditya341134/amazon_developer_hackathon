# Debugging Guide

## Key invariant
Every diagnosis must reference:
- failing node_id
- at least one event_id with timestamp
- at least one device snapshot fact (state/timeOfSample/caps/health)

## Troubleshooting
- Replay mismatch: ensure all timestamps are scenario-time (base + offsets)
- Wrong F2 detection: enforce freshness_seconds checks using timeOfSample
- F3 false positives: compare declared_caps vs actual_caps and confirm directive failure