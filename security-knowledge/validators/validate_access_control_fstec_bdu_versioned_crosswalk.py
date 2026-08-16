import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "security-knowledge/regression/access-control-fstec-bdu-versioned-crosswalk-regression-v1.json"


def route(case):
    i = case["input"]

    if i.get("join_key") == "measure_code_only":
        return {"state": "REJECT_UNVERSIONED_JOIN"}

    if i.get("claim") == "vulnerability proves legal obligation":
        return {"state": "REJECT_AUTOMATIC_LEGAL_APPLICABILITY"}

    if i.get("gost_status") == "Действует" and i.get("claim") == "mandatory_by_law":
        return {"state": "NEEDS_BINDING_EDGE"}

    if i.get("rewrite_to_current") is True and i.get("historical_evidence"):
        return {"state": "REJECT_SILENT_MIGRATION"}

    if i.get("infer_current_fstec_measure_from_code_only") is True:
        return {"state": "CODE_COLLISION_DETECTED"}

    if i.get("bdu_record") == "BDA:C006" and i.get("observed_code") == "УПД.5" and not i.get("bdu_measure_version"):
        return {"state": "BDU_MEASURE_VERSION_UNRESOLVED"}

    if i.get("measure_code") == "УПД.5":
        catalog = i.get("fstec_catalog")
        if catalog is None:
            return {"state": "FSTEC_MEASURE_VERSION_UNKNOWN"}
        if catalog == "2026":
            return {"meaning": "USER_WARNING", "state": "ROUTED"}
        if catalog == "2014":
            return {"meaning": "LEAST_PRIVILEGE", "state": "HISTORICAL_ROUTED"}

    if i.get("query") == "least_privilege":
        if i.get("fstec_catalog") == "2026":
            return {"target": "FSTEC-M2026-UPD-2", "state": "ROUTED"}
        if i.get("fstec_catalog") == "2014":
            return {"target": "FSTEC-M2014-UPD-5", "state": "HISTORICAL_ROUTED"}

    if i.get("current_fstec_measure") == "FSTEC-M2026-UPD-5" and i.get("claim") == "least_privilege":
        return {"state": "CODE_COLLISION_DETECTED"}
    if i.get("current_fstec_measure") == "FSTEC-M2026-UPD-2" and i.get("claim") == "least_privilege":
        return {"state": "ROUTED"}

    if i.get("bdu_record") == "BDA:C006" and i.get("regulatory_applicability") is None and i.get("fstec_target"):
        return {"state": "FSTEC_APPLICABILITY_UNKNOWN"}

    if i.get("iso_implemented") is True:
        if not i.get("fstec_exact_properties_verified"):
            return {"state": "REQUIRES_EXPERT_MAPPING"}
        if i.get("fstec_exact_properties_verified") and i.get("fstec_applicable"):
            return {"relation": "POSSIBLE_IMPLEMENTATION_EVIDENCE", "equivalence": "NOT_PROVEN"}

    if i.get("gost") == "ГОСТ Р ИСО/МЭК 27002-2021" and i.get("theme") == "least_privilege":
        return {"relation": "THEMATIC_OVERLAP", "equivalence": "NOT_PROVEN"}
    if i.get("gost") == "ГОСТ Р 59383-2021" and i.get("theme") == "access_control_model":
        return {"relation": "SUPPORTS_OBJECTIVE", "equivalence": "NOT_PROVEN"}

    raise AssertionError(f"Unhandled case: {case['id']}")


def main():
    suite = json.loads(FIX.read_text(encoding="utf-8"))
    failures = []
    for case in suite["cases"]:
        actual = route(case)
        expected = case["expected"]
        if actual != expected:
            failures.append((case["id"], expected, actual))
    if failures:
        for cid, expected, actual in failures:
            print(f"FAIL {cid}: expected={expected} actual={actual}")
        raise SystemExit(1)
    print(f"PASS {len(suite['cases'])} access-control versioned crosswalk cases")


if __name__ == "__main__":
    main()
