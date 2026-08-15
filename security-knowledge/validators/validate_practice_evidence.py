import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "security-knowledge" / "practical-cases" / "judicial-regulatory-practice-evidence-regression-v1.json"

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


def classify(x):
    if x.get("search_no_hit"):
        return "NO_VERIFIED_OFFICIAL_CASE_ACQUIRED"

    ptype = x.get("practice_type")
    tier = x.get("source_tier")
    status = x.get("status")

    if ptype == "SYNTHETIC_BOUNDARY_CASE" or tier == "SYNTHETIC":
        return "TEST_ONLY"
    if tier in {"SEARCH_SNIPPET", "SECONDARY"}:
        return "DISCOVERY_ONLY"
    if tier == "AUTHORITATIVE_SECONDARY":
        return "AUTHORITATIVE_SECONDARY_ONLY"
    if status == "CANCELLED":
        return "HISTORICAL_ONLY"

    if ptype == "JUDICIAL_DECISION" and tier == "PRIMARY_OFFICIAL":
        # Sparse records may be immutable-gate-only fixtures.
        if x.get("immutable_requested"):
            if not (
                x.get("exact_bytes_preserved") is True
                and x.get("retrieved_at")
                and HEX64.match(str(x.get("sha256", "")))
            ):
                return "NOT_IMMUTABLE"

        identity_fields = ["case_number", "court_name"]
        if any(k in x for k in identity_fields) and not all(x.get(k) for k in identity_fields):
            return "NEEDS_CASE_IDENTITY"

        if "cited_norms" in x and (not x.get("cited_norms") or not x.get("legal_anchors")):
            return "NEEDS_LEGAL_ANCHORS"

        required = [
            "case_number", "court_name", "decision_date", "document_type",
            "procedural_stage", "disposition", "cited_norms", "holding_summary",
            "appeal_status", "source_url", "observed_at", "status", "facts_scope",
            "legal_anchors", "proposition_limits"
        ]
        if x.get("immutable_requested") and all(x.get(k) for k in required):
            return "IMMUTABLE_PRIMARY_PRACTICE"
        if all(x.get(k) for k in required):
            return "AUTHORITATIVE_PRACTICE_VERIFIED"
        return "NEEDS_CASE_IDENTITY"

    if ptype == "REGULATOR_DECISION" and tier == "PRIMARY_OFFICIAL":
        if not x.get("decision_or_protocol_number"):
            return "NEEDS_DECISION_IDENTITY"
        return "AUTHORITATIVE_PRACTICE_VERIFIED"

    if ptype in {"REGULATOR_GUIDANCE", "ENFORCEMENT_STATISTICS"} and tier == "PRIMARY_OFFICIAL":
        common = ["authority_name", "source_url", "observed_at", "status", "legal_anchors", "proposition_limits"]
        return "AUTHORITATIVE_PRACTICE_VERIFIED" if all(x.get(k) for k in common) else "NEEDS_SOURCE_EVIDENCE"

    return "NEEDS_SOURCE_EVIDENCE"


def main():
    data = json.loads(FIX.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = classify(case["input"])
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for f in failures:
            print(f"FAIL {f[0]} expected={f[1]} actual={f[2]}")
        raise SystemExit(1)
    print(f"PASS {len(data['cases'])} practice-evidence regression cases")


if __name__ == "__main__":
    main()
