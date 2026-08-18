from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "security-knowledge" / "classification" / "pp-rf-4-2026-atomic-energy-kii-overlay-v1.json"
FIXTURE_PATH = ROOT / "security-knowledge" / "classification" / "pp-rf-4-2026-atomic-energy-kii-overlay-regression-v1.json"
MANIFEST_PATH = ROOT / "security-knowledge" / "evidence" / "primary-artifact-pp-rf-4-2026.json"
ARTIFACT_PATH = ROOT / "security-knowledge" / "evidence" / "primary-artifacts" / "2026" / "pp-rf-4-2026-0001202601160013.pdf"
EXPECTED_SHA256 = "65815147d515721d4fadaa251fb33f61c3259a1c4feed562afb50c0f1b087df4"


def main() -> int:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    source = matrix.get("source", {})
    artifact = manifest.get("artifact", {})
    check(matrix.get("status") == "VERIFIED_PRIMARY_IMMUTABLE", "matrix status drift")
    check(matrix.get("record_id") == fixture.get("matrix_id"), "fixture matrix mismatch")
    check(matrix.get("act", {}).get("effective_from") == "2026-01-24", "effective date drift")
    check(matrix.get("act", {}).get("effective_date_confidence") == "DERIVED_FROM_PRIMARY_PUBLICATION_AND_GENERAL_RULE", "effective-date confidence drift")
    check(source.get("sha256") == EXPECTED_SHA256 == artifact.get("sha256"), "SHA-256 metadata drift")
    check(source.get("byte_length") == 2895018 == artifact.get("byte_length"), "byte length drift")
    check(source.get("pdf_pages") == 12 == artifact.get("pages"), "page count drift")
    check(matrix.get("extraction", {}).get("ocr_is_evidence") is False, "OCR must not be evidence")

    data = ARTIFACT_PATH.read_bytes()
    check(data.startswith(b"%PDF-1.5"), "artifact PDF magic/version drift")
    check(len(data) == 2895018, "artifact byte length mismatch")
    check(hashlib.sha256(data).hexdigest() == EXPECTED_SHA256, "artifact SHA-256 mismatch")
    check(b"/Encrypt" not in data, "artifact unexpectedly encrypted")
    check(b"/JavaScript" not in data and b"/JS" not in data, "artifact contains JavaScript")

    routing = matrix.get("scope_and_routing", [])
    calculations = matrix.get("calculation_rules", [])
    by_id = {item.get("id"): item for item in routing + calculations}
    check(len(by_id) == len(routing) + len(calculations), "rule IDs missing or duplicated")
    check(len(routing) == 8, f"expected 8 routing groups, got {len(routing)}")
    check(len(calculations) == 13, f"expected 13 calculation groups, got {len(calculations)}")

    excluded = by_id.get("PP4-C5-EXCLUDED-INDICATORS", {}).get("excluded_pp127_positions", [])
    check(excluded == fixture.get("required_excluded_positions"), "clause 5 excluded indicator set drift")
    routes = by_id.get("PP4-C6-INDICATOR-ROUTING", {}).get("routes", [])
    routed_positions = [position for route in routes for position in route.get("positions", [])]
    check(set(routed_positions) == {"1","2","3","5","6","7","8","9","11","12","13","13^1"}, "clause 6 routed indicator set drift")
    check(len(by_id.get("PP4-C7-ADDITIONAL-INPUTS", {}).get("required_input_groups", [])) == 6, "clause 7 input group count drift")
    check(len(by_id.get("PP4-C11-METHODS", {}).get("methods", [])) == 4, "clause 11 method count drift")

    numeric = {}
    for rule in calculations:
        for item in rule.get("numeric_rules", []):
            numeric[(rule.get("id"), item.get("kind"))] = item
    for expected in fixture.get("required_numeric_rules", []):
        item = numeric.get((expected["rule_id"], expected["kind"]), {})
        check(item.get("value") == expected["value"] and item.get("unit") == expected["unit"], f"numeric rule drift: {expected['rule_id']} {expected['kind']}")
    fallback = numeric.get(("PP4-C18-POSITION-8", "FALLBACK_VALUE"), {})
    check(fallback.get("scope") == "TIME_TO_ELIMINATE_ATTACK_CONSEQUENCES_FOR_POSITION_8_CALCULATION", "10-day fallback scope widened")
    check("deadline" not in fallback.get("kind", "").lower(), "10-day fallback converted to deadline")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS PP RF 4/2026: immutable source, 8 routing and 13 calculation groups")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
