from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

STAGE4 = Path(r"G:\1\FATHER_LIBRARY_STAGE4")
OUT = Path(r"G:\1\FATHER_LIBRARY_STAGE5")
SEED = Path(__file__).resolve().parents[1] / "father" / "agent-factory" / "knowledge" / "library" / "standards_p0_official_seed_2026-08-30.json"


def norm_id(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().upper())


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    manifest = STAGE4 / "standards_verification_manifest.jsonl"
    if not manifest.exists():
        print(f"ERROR: missing {manifest}", file=sys.stderr); return 2
    if not SEED.exists():
        print(f"ERROR: missing seed {SEED}", file=sys.stderr); return 3

    OUT.mkdir(parents=True, exist_ok=True)
    rows = read_jsonl(manifest)
    seed_doc = json.loads(SEED.read_text(encoding="utf-8"))
    seed = {norm_id(x["standard_id"]): x for x in seed_doc["standards"]}

    updated = []
    matched = []
    unmatched_p0 = []
    for row in rows:
        sid = norm_id(row.get("standard_id_hint"))
        rec = dict(row)
        if rec.get("priority") == "P0" and sid in seed:
            s = seed[sid]
            rec.update({
                "official_catalog_status": "VERIFIED_ACTIVE",
                "currentness_status": "CURRENT",
                "effective_date_verified": s.get("effective_date"),
                "replaces": s.get("replaces"),
                "official_title_verified": s.get("title"),
                "official_authority": seed_doc.get("authority"),
                "official_verified_at": seed_doc.get("verified_at"),
                "verification_result": "OFFICIAL_CATALOG_VERIFIED_CURRENT",
                "promotion_as_guidance_allowed": True,
                "promotion_as_obligation_allowed": False,
                "legal_applicability": "PENDING_REVIEW",
                "next_action": "LEGAL_APPLICABILITY_AND_REQUIREMENT_EXTRACTION",
            })
            matched.append(rec)
        elif rec.get("priority") == "P0":
            unmatched_p0.append(rec)
        updated.append(rec)

    write_jsonl(OUT / "standards_verification_manifest_stage5.jsonl", updated)
    write_jsonl(OUT / "standards_p0_officially_verified.jsonl", matched)
    write_jsonl(OUT / "standards_p0_unmatched_review.jsonl", unmatched_p0)
    write_jsonl(OUT / "standards_p1_pending.jsonl", [x for x in updated if x.get("priority") == "P1"])

    summary = {
        "record_type": "FATHER_STAGE5_P0_STANDARD_SEED_APPLY",
        "status": "PASS" if not unmatched_p0 else "PASS_WITH_UNMATCHED_P0",
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "standards_total": len(rows),
        "p0_verified_current": len(matched),
        "p0_unmatched": len(unmatched_p0),
        "p1_pending": sum(1 for x in updated if x.get("priority") == "P1"),
        "obligation_promoted": 0,
        "guidance_promoted": len(matched),
        "kb_ready": 0,
        "notes": [
            "Official Rosstandart catalog currentness is verified for matched P0 standards.",
            "Legal applicability is still pending and no standard is promoted as a binding obligation yet.",
            "Knowledge extraction has not started in this step."
        ]
    }
    (OUT / "LATEST_STAGE5_P0_STANDARD_REPORT.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [
        "# FATHER Stage 5 — P0 standard official verification", "",
        f"- Status: **{summary['status']}**",
        f"- P0 officially verified current: **{summary['p0_verified_current']}**",
        f"- P0 unmatched: **{summary['p0_unmatched']}**",
        f"- P1 pending: **{summary['p1_pending']}**",
        f"- Binding obligations promoted: **0**",
        f"- KB_READY: **0**", "",
        "> Currentness/catalog status is verified separately from legal applicability."
    ]
    (OUT / "LATEST_STAGE5_P0_STANDARD_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Report: {OUT / 'LATEST_STAGE5_P0_STANDARD_REPORT.md'}")
    return 0 if not unmatched_p0 else 1


if __name__ == "__main__":
    sys.exit(main())
