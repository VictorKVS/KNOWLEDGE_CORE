from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

DEFAULT_STAGE6 = Path(r"G:\1\FATHER_LIBRARY_STAGE6_LEGAL")
DEFAULT_OUTPUT = Path(r"G:\1\FATHER_LIBRARY_STAGE7")
DEFAULT_SEED = Path(__file__).resolve().parents[1] / "father" / "agent-factory" / "knowledge" / "library" / "ai_ru_regulatory_enrichment_queue.json"


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


def norm_number(value: str | None) -> str:
    s = (value or "").upper().replace("–", "-").replace("—", "-")
    s = re.sub(r"\s+", "", s)
    if re.fullmatch(r"\d+", s):
        return s
    m = re.search(r"(\d+)[-]?ФЗ", s)
    return f"{m.group(1)}-ФЗ" if m else s


def local_key(row: dict) -> tuple[str, str]:
    typ = row.get("document_type") or ""
    mapping = {"LAW": "FEDERAL_LAW", "GOVERNMENT_DECREE": "GOVERNMENT_DECREE", "AGENCY_ORDER": "AGENCY_ORDER"}
    return mapping.get(typ, typ), norm_number(row.get("document_number_candidate"))


def seed_key(row: dict) -> tuple[str, str]:
    return row.get("type") or "", norm_number(row.get("number"))


def main() -> int:
    ap = argparse.ArgumentParser(description="FATHER Stage 7: merge AI regulatory enrichment with local legal candidates")
    ap.add_argument("--stage6", type=Path, default=DEFAULT_STAGE6)
    ap.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()

    src = args.stage6 / "legal_candidates.jsonl"
    if not src.exists():
        raise SystemExit(f"Missing Stage6 legal candidates: {src}")
    if not args.seed.exists():
        raise SystemExit(f"Missing AI enrichment seed: {args.seed}")

    args.output.mkdir(parents=True, exist_ok=True)
    local = read_jsonl(src)
    seed = json.loads(args.seed.read_text(encoding="utf-8"))
    ai_legal = seed.get("legal_p0", [])
    ai_standards = seed.get("ai_standards", [])

    local_map: dict[tuple[str, str], list[dict]] = {}
    for row in local:
        local_map.setdefault(local_key(row), []).append(row)

    overlaps = []
    missing = []
    for item in ai_legal:
        key = seed_key(item)
        matches = local_map.get(key, [])
        if matches:
            overlaps.append({"ai_seed": item, "local_matches": matches, "merge_status": "OVERLAP_FOUND"})
        else:
            missing.append({**item, "merge_status": "ENRICHMENT_ONLY", "next_action": "ADD_TO_OFFICIAL_VERIFICATION_QUEUE"})

    write_jsonl(args.output / "ai_legal_overlap_with_local.jsonl", overlaps)
    write_jsonl(args.output / "ai_legal_missing_from_local.jsonl", missing)
    (args.output / "ai_standards_enrichment.json").write_text(json.dumps(ai_standards, ensure_ascii=False, indent=2), encoding="utf-8")

    combined = []
    for row in local:
        combined.append({"origin": "LOCAL_STAGE6", **row})
    for row in missing:
        combined.append({"origin": "AI_ENRICHMENT", **row})
    write_jsonl(args.output / "combined_legal_official_verification_queue.jsonl", combined)

    report = {
        "record_type": "FATHER_STAGE7_AI_REGULATORY_MERGE",
        "status": "PASS",
        "local_legal_candidates": len(local),
        "ai_seed_legal": len(ai_legal),
        "ai_overlap_found": len(overlaps),
        "ai_missing_from_local": len(missing),
        "combined_queue_total": len(combined),
        "ai_standards_enrichment": len(ai_standards),
        "kb_ready": 0,
        "notes": [
            "Merge is identity preparation only; no legal currentness/applicability is asserted for local candidates.",
            "AI seed entries marked VERIFIED_SOURCE have an official-source identity check but still require applicability analysis before producing obligations.",
            "No source files are modified."
        ]
    }
    (args.output / "LATEST_STAGE7_AI_REGULATORY_MERGE_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [
        "# FATHER Stage 7 — AI regulatory enrichment merge", "",
        f"- Status: **PASS**", f"- Local legal candidates: **{len(local)}**", f"- AI legal seed: **{len(ai_legal)}**",
        f"- AI overlap with local: **{len(overlaps)}**", f"- AI missing from local: **{len(missing)}**",
        f"- Combined official-verification queue: **{len(combined)}**", f"- AI standards enrichment: **{len(ai_standards)}**",
        "- KB_READY: **0**", "",
        "> Identity merge only. Official currentness, amendment lineage, scope and applicability remain separate gates."
    ]
    (args.output / "LATEST_STAGE7_AI_REGULATORY_MERGE_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Report: {args.output / 'LATEST_STAGE7_AI_REGULATORY_MERGE_REPORT.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
