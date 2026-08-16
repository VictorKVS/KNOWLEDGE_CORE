import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "security-knowledge/standards/isms-lifecycle-fstec-crosswalk-regression-v1.json"

BOUNDARIES = {
    "27001": (date(2022, 1, 1), "USE_27001_2006_HISTORICAL", "USE_27001_2021_CURRENT_FOR_DATE"),
    "27002": (date(2021, 11, 30), "USE_27002_2012_HISTORICAL", "USE_27002_2021_CURRENT_FOR_DATE"),
    "27003": (date(2021, 11, 30), "USE_27003_2012_HISTORICAL", "USE_27003_2021_CURRENT_FOR_DATE"),
}

FORBIDDEN_EQUIVALENCE = {"LEGALLY_EQUIVALENT", "TECHNICALLY_EQUIVALENT", "SATISFIES_AUTOMATICALLY"}


def route(c):
    std = c.get("standard")
    ds = c.get("date")
    if ds is None:
        return "HISTORICAL_DATE_MISSING"
    if std not in BOUNDARIES:
        return "UNKNOWN_STANDARD_EDITION"

    d = date.fromisoformat(ds)

    if c.get("bdu_relation_only") and c.get("requested_relation") == "SATISFIES_AUTOMATICALLY":
        return "BLOCK_BDU_AS_EQUIVALENCE_PROOF"

    if c.get("fstec_applicable") == "UNKNOWN":
        return "FSTEC_APPLICABILITY_UNKNOWN"

    if c.get("mapping"):
        if c.get("fstec_applicable") is False and c.get("binding_edge"):
            return "STANDARD_BINDING_FSTEC_NOT_APPLICABLE"
        if c.get("fstec_applicable") is True and not c.get("binding_edge"):
            return "GUIDANCE_PLUS_FSTEC_REQUIREMENT_NO_EQUIVALENCE"
        if not c.get("clause_evidence_both_sides", False):
            return "REQUIRES_EXPERT_MAPPING"
        if not c.get("expert_approved", False):
            return "REQUIRES_EXPERT_MAPPING"
        requested = c.get("requested_relation")
        if requested in FORBIDDEN_EQUIVALENCE and not c.get("equivalence_proof", False):
            return "BLOCK_UNPROVEN_EQUIVALENCE"
        return "MAPPING_ACCEPTED_NON_EQUIVALENT"

    if c.get("requested") == "legal_obligation":
        if not c.get("binding_edge", False):
            return "NEEDS_BINDING_EDGE"
        return "BINDING_STANDARD_REQUIREMENT_CONTEXT"

    boundary, old_result, new_result = BOUNDARIES[std]
    return new_result if d >= boundary else old_result


def main():
    data = json.loads(FIX.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        got = route(case)
        if got != case["expected"]:
            failures.append((case["id"], case["expected"], got))
    if failures:
        for f in failures:
            print("FAIL", *f)
        raise SystemExit(1)
    print(f"PASS {len(data['cases'])} ISMS lifecycle/FSTEC non-equivalence cases")


if __name__ == "__main__":
    main()
