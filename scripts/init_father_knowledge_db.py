# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA = REPO_ROOT / "father" / "agent-factory" / "knowledge" / "schema" / "father_knowledge_v1.sql"
DEFAULT_DB = Path(r"G:\1\FATHER_KNOWLEDGE\db\father_knowledge.db")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def apply_schema(conn: sqlite3.Connection) -> None:
    sql = SCHEMA.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


def golden_fixture(conn: sqlite3.Connection) -> dict:
    ts = now_iso()
    run_id = new_id("RUN")
    doc_id = new_id("DOC")
    frg_id = new_id("FRG")
    trn_id = new_id("TRN")
    node_id = new_id("KN")
    evd_id = new_id("EVD")
    rev_id = new_id("REV")
    score_id = new_id("SCORE")

    source_text = (
        "A resilient service should make failure boundaries explicit and preserve enough evidence "
        "to explain why a recovery decision was made."
    )
    translated = (
        "Устойчивый сервис должен явно определять границы отказов и сохранять достаточно доказательств, "
        "чтобы объяснить, почему было принято решение о восстановлении."
    )

    with conn:
        conn.execute(
            "INSERT INTO processing_runs(run_id,run_type,started_at,status,worker_count,config_json,metrics_json) VALUES(?,?,?,?,?,?,?)",
            (run_id, "GOLDEN_FIXTURE", ts, "RUNNING", 1, "{}", "{}"),
        )
        conn.execute(
            """INSERT INTO documents(document_id,source_sha256,title,source_language,document_type,domain,admitted_at,run_id,metadata_json)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (doc_id, "fixture-source-sha256", "FATHER golden fixture", "en", "FIXTURE", "architecture", ts, run_id, "{}"),
        )
        conn.execute(
            """INSERT INTO fragments(fragment_id,document_id,fragment_sha256,ordinal,section_path,extraction_method,extraction_confidence,source_text,created_at,metadata_json)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (frg_id, doc_id, "fixture-fragment-sha256", 0, "fixture", "native-text", 1.0, source_text, ts, "{}"),
        )
        conn.execute(
            """INSERT INTO translations(translation_id,fragment_id,source_language,target_language,final_text,translation_sha256,translator_model,reviewer_model,translation_confidence,reviewer_verdict,status,created_at,qa_json)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (trn_id, frg_id, "en", "ru", translated, "fixture-translation-sha256", "fixture-translator", "fixture-reviewer", 1.0, "PASS", "READY_FOR_KNOWLEDGE_EXTRACTION", ts, "{}"),
        )
        conn.execute(
            """INSERT INTO knowledge_nodes(node_id,node_type,canonical_text,canonical_language,domain,status,created_at,updated_at,metadata_json)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (node_id, "PRINCIPLE", "Границы отказов системы должны быть явными и решения о восстановлении должны быть объяснимыми по сохранённым доказательствам.", "ru", "architecture", "UNDER_REVIEW", ts, ts, "{}"),
        )
        conn.execute(
            """INSERT INTO evidence_links(evidence_id,node_id,fragment_id,translation_id,evidence_role,exact_anchor,quoted_text,created_at,metadata_json)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (evd_id, node_id, frg_id, trn_id, "PRIMARY", "fixture/paragraph/1", source_text, ts, "{}"),
        )
        conn.execute(
            """INSERT INTO scores(score_id,node_id,source_authority,extraction_confidence,translation_confidence,ambiguity,cross_source_support,applicability,reviewer_confidence,calculated_at,profile_version,metadata_json)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (score_id, node_id, 0.5, 1.0, 1.0, 0.1, 0.0, 0.8, 1.0, ts, "golden-v1", "{}"),
        )
        conn.execute(
            """INSERT INTO reviews(review_id,node_id,reviewer_type,reviewer_id,verdict,confidence,evidence_sufficient,input_revision,prompt_profile,review_json,reviewed_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (rev_id, node_id, "DETERMINISTIC", "golden-fixture", "APPROVE", 1.0, 1, "v1", "golden-v1", "{}", ts),
        )
        for role in ("ROLE-ARCHITECT", "ROLE-SOFTWARE-ENGINEER", "ROLE-SECURITY", "ROLE-LAWYER", "ROLE-MANAGER", "ROLE-PRODUCT"):
            conn.execute(
                """INSERT INTO role_views(role_view_id,node_id,role_id,relevance,role_weight,profile_version,created_at)
                   VALUES(?,?,?,?,?,?,?)""",
                (new_id("VIEW"), node_id, role, 0.5, 0.5, "golden-v1", ts),
            )
        conn.execute("UPDATE knowledge_nodes SET status='KB_READY', updated_at=? WHERE node_id=?", (ts, node_id))
        conn.execute("UPDATE processing_runs SET finished_at=?, status='SUCCESS' WHERE run_id=?", (ts, run_id))

    return {"run_id": run_id, "document_id": doc_id, "fragment_id": frg_id, "translation_id": trn_id, "node_id": node_id}


def integrity(conn: sqlite3.Connection) -> dict:
    fk = conn.execute("PRAGMA foreign_key_check").fetchall()
    qc = conn.execute("PRAGMA quick_check").fetchall()
    ready = conn.execute("SELECT COUNT(*) FROM v_kb_ready_nodes").fetchone()[0]
    return {
        "foreign_key_check": fk,
        "quick_check": qc,
        "kb_ready_count": ready,
        "ok": not fk and qc == [("ok",)] and ready >= 1,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize FATHER Knowledge Factory SQLite M1")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--no-fixture", action="store_true")
    args = parser.parse_args()

    db = Path(args.db)
    if not SCHEMA.exists():
        raise FileNotFoundError(SCHEMA)

    conn = connect(db)
    try:
        apply_schema(conn)
        fixture = None if args.no_fixture else golden_fixture(conn)
        result = integrity(conn)
        report = {"db": str(db), "schema": str(SCHEMA), "fixture": fixture, "integrity": result}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if result["ok"] or args.no_fixture else 2
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
