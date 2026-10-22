def init_schema(conn) -> None:
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS routines (
      routine_id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      description TEXT,
      spec_json TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scenarios (
      scenario_id TEXT PRIMARY KEY,
      routine_id TEXT NOT NULL,
      name TEXT NOT NULL,
      description TEXT,
      seed INTEGER NOT NULL,
      definition_json TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS runs (
      run_id TEXT PRIMARY KEY,
      routine_id TEXT NOT NULL,
      scenario_id TEXT NOT NULL,
      started_at TEXT NOT NULL,
      status TEXT NOT NULL,
      primary_failure_type TEXT,
      graph_json TEXT,
      explain_json TEXT,
      applied_patches_json TEXT NOT NULL DEFAULT '[]',
      created_from_run_id TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
      event_id TEXT PRIMARY KEY,
      run_id TEXT NOT NULL,
      ts TEXT NOT NULL,
      kind TEXT NOT NULL,
      summary TEXT NOT NULL,
      payload_json TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS device_snapshots (
      snapshot_id TEXT PRIMARY KEY,
      run_id TEXT NOT NULL,
      ts TEXT NOT NULL,
      device_id TEXT NOT NULL,
      endpoint_health TEXT NOT NULL,
      actual_state_json TEXT NOT NULL,
      reported_state_json TEXT NOT NULL,
      time_of_sample TEXT,
      declared_caps_json TEXT NOT NULL,
      actual_caps_json TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS fixes (
      fix_id TEXT PRIMARY KEY,
      run_id TEXT NOT NULL,
      mode TEXT NOT NULL,
      title TEXT NOT NULL,
      why_it_works TEXT NOT NULL,
      patch_json TEXT NOT NULL,
      auto_apply_ok INTEGER NOT NULL,
      applied INTEGER NOT NULL DEFAULT 0
    )
    """)

    # Performance and lookup indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_events_run_ts ON events(run_id, ts)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_run_ts ON device_snapshots(run_id, ts)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fixes_run ON fixes(run_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_runs_created ON runs(created_from_run_id)")

    conn.commit()