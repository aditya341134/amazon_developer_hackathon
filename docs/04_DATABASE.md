# Database (SQLite)

## Tables
### routines
- routine_id TEXT PK
- name TEXT
- spec_json TEXT

### scenarios
- scenario_id TEXT PK
- name TEXT
- description TEXT
- seed INTEGER
- definition_json TEXT

### runs
- run_id TEXT PK
- routine_id TEXT
- scenario_id TEXT
- started_at TEXT
- status TEXT (PASS/FAIL)
- primary_failure_type TEXT NULL
- created_from_run_id TEXT NULL

### events
- event_id TEXT PK
- run_id TEXT
- ts TEXT
- kind TEXT
- summary TEXT
- payload_json TEXT

### device_snapshots
- snapshot_id TEXT PK
- run_id TEXT
- ts TEXT
- device_id TEXT
- endpoint_health TEXT
- actual_state_json TEXT
- reported_state_json TEXT
- time_of_sample TEXT NULL
- declared_caps_json TEXT
- actual_caps_json TEXT

### fixes
- fix_id TEXT PK
- run_id TEXT
- fix_mode TEXT (routine/integration)
- title TEXT
- patch_json TEXT
- applied INTEGER

## Indexes
- events(run_id, ts)
- device_snapshots(run_id, ts)