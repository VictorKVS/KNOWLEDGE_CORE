PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS trace_events (
    event_id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    span_id TEXT NOT NULL,
    parent_span_id TEXT,
    run_id TEXT,
    stream_id TEXT,
    worker_id TEXT,
    timestamp TEXT NOT NULL,
    stage TEXT NOT NULL,
    event TEXT,
    status TEXT NOT NULL CHECK(status IN ('START','OK','WARN','ERROR','BLOCKED','RETRY')),
    entity_type TEXT,
    entity_id TEXT,
    source_sha256 TEXT,
    fragment_sha256 TEXT,
    model TEXT,
    prompt_profile TEXT,
    elapsed_ms REAL,
    error_type TEXT,
    error_message TEXT,
    attributes_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_trace_events_trace ON trace_events(trace_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_trace_events_span ON trace_events(span_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_trace_events_stage_status ON trace_events(stage, status);
CREATE INDEX IF NOT EXISTS idx_trace_events_entity ON trace_events(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_trace_events_run ON trace_events(run_id, timestamp);

CREATE TABLE IF NOT EXISTS entity_trace_links (
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    span_id TEXT NOT NULL,
    relation TEXT NOT NULL DEFAULT 'CREATED_BY',
    linked_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    PRIMARY KEY(entity_type, entity_id, trace_id, span_id, relation)
);

CREATE INDEX IF NOT EXISTS idx_entity_trace_links_entity ON entity_trace_links(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_entity_trace_links_trace ON entity_trace_links(trace_id, span_id);

CREATE VIEW IF NOT EXISTS v_trace_errors AS
SELECT trace_id, span_id, parent_span_id, run_id, stream_id, worker_id,
       timestamp, stage, entity_type, entity_id, error_type, error_message, attributes_json
FROM trace_events
WHERE status IN ('ERROR','BLOCKED')
ORDER BY timestamp;
