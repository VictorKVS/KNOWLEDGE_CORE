PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT OR IGNORE INTO schema_meta(key,value) VALUES ('schema_version','1.0.0');

CREATE TABLE IF NOT EXISTS processing_runs (
    run_id TEXT PRIMARY KEY,
    run_type TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    worker_count INTEGER NOT NULL DEFAULT 1,
    model_profile TEXT,
    config_json TEXT NOT NULL DEFAULT '{}',
    metrics_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    source_sha256 TEXT NOT NULL,
    title TEXT,
    author TEXT,
    publisher TEXT,
    edition TEXT,
    revision TEXT,
    publication_date TEXT,
    source_language TEXT,
    document_type TEXT NOT NULL,
    domain TEXT,
    authority_class TEXT,
    local_path TEXT,
    source_uri TEXT,
    media_type TEXT,
    size_bytes INTEGER,
    currentness_status TEXT,
    applicability_status TEXT,
    admitted_at TEXT NOT NULL,
    run_id TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(run_id) REFERENCES processing_runs(run_id)
);
CREATE INDEX IF NOT EXISTS idx_documents_sha ON documents(source_sha256);
CREATE INDEX IF NOT EXISTS idx_documents_domain ON documents(domain);

CREATE TABLE IF NOT EXISTS fragments (
    fragment_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    fragment_sha256 TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    page_start INTEGER,
    page_end INTEGER,
    section_path TEXT,
    block_id TEXT,
    bbox_json TEXT,
    extraction_method TEXT NOT NULL,
    extraction_confidence REAL,
    source_text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(document_id) REFERENCES documents(document_id) ON DELETE RESTRICT,
    UNIQUE(document_id, fragment_sha256, ordinal)
);
CREATE INDEX IF NOT EXISTS idx_fragments_document ON fragments(document_id);
CREATE INDEX IF NOT EXISTS idx_fragments_sha ON fragments(fragment_sha256);

CREATE TABLE IF NOT EXISTS translations (
    translation_id TEXT PRIMARY KEY,
    fragment_id TEXT NOT NULL,
    source_language TEXT NOT NULL,
    target_language TEXT NOT NULL,
    draft_text TEXT,
    final_text TEXT NOT NULL,
    translation_sha256 TEXT NOT NULL,
    translator_model TEXT,
    reviewer_model TEXT,
    prompt_profile TEXT,
    glossary_revision TEXT,
    translation_confidence REAL,
    reviewer_verdict TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    qa_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(fragment_id) REFERENCES fragments(fragment_id) ON DELETE RESTRICT,
    UNIQUE(fragment_id, target_language, translation_sha256)
);
CREATE INDEX IF NOT EXISTS idx_translations_fragment ON translations(fragment_id);

CREATE TABLE IF NOT EXISTS knowledge_nodes (
    node_id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL CHECK(node_type IN (
        'CONCEPT','DEFINITION','CLAIM','PRINCIPLE','PATTERN','ANTI_PATTERN',
        'DECISION_RULE','TRADE_OFF','CHECKLIST','METRIC','FAILURE_MODE','TEST','EXAMPLE','REQUIREMENT'
    )),
    canonical_text TEXT NOT NULL,
    canonical_language TEXT NOT NULL DEFAULT 'ru',
    domain TEXT,
    scope_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL CHECK(status IN ('CANDIDATE','UNDER_REVIEW','KB_READY','REJECTED','SUPERSEDED')),
    semantic_key TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_nodes_type ON knowledge_nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_nodes_status ON knowledge_nodes(status);
CREATE INDEX IF NOT EXISTS idx_nodes_domain ON knowledge_nodes(domain);

CREATE TABLE IF NOT EXISTS knowledge_edges (
    edge_id TEXT PRIMARY KEY,
    from_node_id TEXT NOT NULL,
    to_node_id TEXT NOT NULL,
    edge_type TEXT NOT NULL CHECK(edge_type IN (
        'DEFINES','SUPPORTS','CONTRADICTS','REFINES','DEPENDS_ON','PART_OF',
        'APPLIES_TO','CAUSES','MITIGATES','IMPLEMENTS','DERIVED_FROM','EVIDENCE_FOR','SAME_AS'
    )),
    status TEXT NOT NULL CHECK(status IN ('CANDIDATE','UNDER_REVIEW','KB_READY','REJECTED')),
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(from_node_id) REFERENCES knowledge_nodes(node_id) ON DELETE RESTRICT,
    FOREIGN KEY(to_node_id) REFERENCES knowledge_nodes(node_id) ON DELETE RESTRICT,
    CHECK(from_node_id <> to_node_id OR edge_type = 'SAME_AS')
);
CREATE INDEX IF NOT EXISTS idx_edges_from ON knowledge_edges(from_node_id);
CREATE INDEX IF NOT EXISTS idx_edges_to ON knowledge_edges(to_node_id);
CREATE INDEX IF NOT EXISTS idx_edges_type ON knowledge_edges(edge_type);

CREATE TABLE IF NOT EXISTS evidence_links (
    evidence_id TEXT PRIMARY KEY,
    node_id TEXT,
    edge_id TEXT,
    fragment_id TEXT NOT NULL,
    translation_id TEXT,
    evidence_role TEXT NOT NULL CHECK(evidence_role IN ('PRIMARY','SUPPORTING','CONTRADICTING','CONTEXT')),
    exact_anchor TEXT,
    quoted_text TEXT,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(node_id) REFERENCES knowledge_nodes(node_id) ON DELETE RESTRICT,
    FOREIGN KEY(edge_id) REFERENCES knowledge_edges(edge_id) ON DELETE RESTRICT,
    FOREIGN KEY(fragment_id) REFERENCES fragments(fragment_id) ON DELETE RESTRICT,
    FOREIGN KEY(translation_id) REFERENCES translations(translation_id) ON DELETE RESTRICT,
    CHECK((node_id IS NOT NULL) <> (edge_id IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS idx_evidence_node ON evidence_links(node_id);
CREATE INDEX IF NOT EXISTS idx_evidence_edge ON evidence_links(edge_id);
CREATE INDEX IF NOT EXISTS idx_evidence_fragment ON evidence_links(fragment_id);

CREATE TABLE IF NOT EXISTS scores (
    score_id TEXT PRIMARY KEY,
    node_id TEXT NOT NULL,
    source_authority REAL,
    extraction_confidence REAL,
    ocr_confidence REAL,
    translation_confidence REAL,
    ambiguity REAL,
    cross_source_support REAL,
    recency REAL,
    currentness REAL,
    applicability REAL,
    implementation_evidence REAL,
    model_agreement REAL,
    reviewer_confidence REAL,
    calculated_at TEXT NOT NULL,
    profile_version TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(node_id) REFERENCES knowledge_nodes(node_id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_scores_node ON scores(node_id);

CREATE TABLE IF NOT EXISTS reviews (
    review_id TEXT PRIMARY KEY,
    node_id TEXT,
    edge_id TEXT,
    reviewer_type TEXT NOT NULL CHECK(reviewer_type IN ('MODEL','GPT','HUMAN','CHIEF_ANALYST','DETERMINISTIC')),
    reviewer_id TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK(verdict IN ('APPROVE','REVISE','REJECT','ESCALATE')),
    confidence REAL,
    evidence_sufficient INTEGER NOT NULL DEFAULT 0,
    input_revision TEXT,
    prompt_profile TEXT,
    review_json TEXT NOT NULL DEFAULT '{}',
    reviewed_at TEXT NOT NULL,
    FOREIGN KEY(node_id) REFERENCES knowledge_nodes(node_id) ON DELETE RESTRICT,
    FOREIGN KEY(edge_id) REFERENCES knowledge_edges(edge_id) ON DELETE RESTRICT,
    CHECK((node_id IS NOT NULL) <> (edge_id IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS idx_reviews_node ON reviews(node_id);
CREATE INDEX IF NOT EXISTS idx_reviews_edge ON reviews(edge_id);

CREATE TABLE IF NOT EXISTS role_views (
    role_view_id TEXT PRIMARY KEY,
    node_id TEXT NOT NULL,
    role_id TEXT NOT NULL CHECK(role_id IN (
        'ROLE-ARCHITECT','ROLE-SOFTWARE-ENGINEER','ROLE-SECURITY','ROLE-LAWYER','ROLE-MANAGER','ROLE-PRODUCT'
    )),
    relevance REAL,
    role_weight REAL,
    applicability_note TEXT,
    decision_context_json TEXT NOT NULL DEFAULT '{}',
    profile_version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(node_id) REFERENCES knowledge_nodes(node_id) ON DELETE RESTRICT,
    UNIQUE(node_id, role_id, profile_version)
);
CREATE INDEX IF NOT EXISTS idx_role_views_role ON role_views(role_id);
CREATE INDEX IF NOT EXISTS idx_role_views_node ON role_views(node_id);

CREATE VIEW IF NOT EXISTS v_kb_ready_nodes AS
SELECT n.*
FROM knowledge_nodes n
WHERE n.status = 'KB_READY'
  AND EXISTS (SELECT 1 FROM evidence_links e WHERE e.node_id = n.node_id)
  AND EXISTS (
      SELECT 1 FROM reviews r
      WHERE r.node_id = n.node_id
        AND r.verdict = 'APPROVE'
        AND r.evidence_sufficient = 1
  );
