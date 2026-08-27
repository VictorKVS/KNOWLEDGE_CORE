from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "security-knowledge" / "classification" / "pp-rf-92-2026-financial-market-kii-overlay-v1.json"
FIXTURE_PATH = ROOT / "security-knowledge" / "classification" / "pp-rf-92-2026-financial-market-kii-overlay-regression-v1.json"
MANIFEST_PATH = ROOT / "security-knowledge" / "evidence" / "primary-artifact-pp-rf-92-2026.json"
ARTIFACT_PATH = ROOT / "security-knowledge" / "evidence" / "primary-artifacts" / "2026" / "pp-rf-92-2026-0001202602070010.pdf"
EXPECTED_SHA256 = "83e32867b115a18a720a316905b001eed3a2211d1e68183ad57ce21fb4968b38"


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
    check(matrix.get("act", {}).get("effective_from") == "2026-02-15", "effective date drift")
    check(matrix.get("act", {}).get("effective_date_confidence") == "DERIVED_FROM_PRIMARY_PUBLICATION_AND_GENERAL_RULE", "effective-date confidence drift")
    check(source.get("sha256") == EXPECTED_SHA256 == artifact.get("sha256"), "SHA-256 metadata drift")
    check(source.get("git_blob_sha") == "cde5d8f5b9c68415c846e9dfa9758ff4437307d2" == artifact.get("git_blob_sha"), "Git blob SHA drift")
    check(source.get("byte_length") == 4272251 == artifact.get("byte_length"), "byte length drift")
    check(source.get("pdf_pages") == 17 == artifact.get("pages"), "page count drift")
    check(matrix.get("extraction", {}).get("ocr_is_evidence") is False, "OCR must not be evidence")

    data = ARTIFACT_PATH.read_bytes()
    check(data.startswith(b"%PDF-1.5"), "artifact PDF magic/version drift")
    check(len(data) == 4272251, "artifact byte length mismatch")
    check(hashlib.sha256(data).hexdigest() == EXPECTED_SHA256, "artifact SHA-256 mismatch")
    check(b"/Encrypt" not in data, "artifact unexpectedly encrypted")
    check(b"/JavaScript" not in data and b"/JS" not in data, "artifact contains JavaScript")

    groups = {name: matrix.get(name, []) for name in ("governance_rules", "indicator_routing_rules", "calculation_rules")}
    for name, expected in fixture.get("required_counts", {}).items():
        check(len(groups[name]) == expected, f"{name} count drift")
    all_rules = sum(groups.values(), [])
    by_id = {item.get("id"): item for item in all_rules}
    check(len(by_id) == len(all_rules), "rule IDs missing or duplicated")

    for expected in fixture.get("required_deadlines", []):
        deadline = by_id.get(expected["rule_id"], {}).get("deadline", {})
        for field in ("kind", "value", "unit", "starts_from"):
            check(deadline.get(field) == expected[field], f"deadline drift: {expected['rule_id']} {field}")
    c5 = by_id.get("PP92-C5-REVIEW-AND-POST-CONFIRMATION-REPORT", {}).get("deadline", {})
    check(c5.get("starts_from") == "RECEIPT_OF_FSTEC_CONFIRMATION_OF_REVIEW_RESULTS", "clause 5 trigger widened")
    c6 = by_id.get("PP92-C6-ANNUAL-INVENTORY-REPORT", {}).get("deadline", {})
    check(c6.get("unit") == "WORKING_DAY_OF_CALENDAR_YEAR", "clause 6 due point converted to calendar date")

    routes = by_id.get("PP92-C35-RECIPIENT-ROUTING", {}).get("routes", [])
    check({r.get("recipient") for r in routes} == set(fixture.get("required_recipient_routes", [])), "recipient routing drift")
    for rule_id, formula in fixture.get("required_formulas", {}).items():
        check(by_id.get(rule_id, {}).get("formula") == formula, f"formula drift: {rule_id}")
    check(by_id.get("PP92-C27-CLIENT-REMOTE-ACCESS", {}).get("positions") == fixture.get("required_clause_27_route"), "clause 27 route drift")
    check(by_id.get("PP92-C41-POSITION-9-FORMULA", {}).get("absolute_value_operator") == "ABSENT", "clause 41 absolute-value drift")
    check(by_id.get("PP92-C41-POSITION-9-FORMULA", {}).get("execution_guard") == "FAIL_CLOSED_WHEN_D_IS_ZERO_OR_MISSING", "clause 41 denominator guard drift")
    check(by_id.get("PP92-C42-P-AVG", {}).get("source_notation_anomaly") == "LOWER_BOUND_IMAGE_SHOWS_i_WITHOUT_EXPLICIT_EQUALS_ONE", "clause 42 lower-bound anomaly lost")
    check(by_id.get("PP92-C42-P-AVG", {}).get("execution_guard") == "FAIL_CLOSED_WHEN_n_IS_ZERO_OR_MISSING_OR_LOWER_BOUND_INTERPRETATION_IS_MATERIAL", "clause 42 execution guard drift")
    check(by_id.get("PP92-C55-CONSEQUENCE-SCENARIOS", {}).get("normative_strength") == "RECOMMENDED", "clause 55 promoted to mandatory")

    c50 = by_id.get("PP92-C50-POSITION-10-3", {})
    check(c50.get("components", {}).get("PA_npf", {}).get("measurement_time") == "TENTH_WORKING_DAY_OF_CALENDAR_YEAR", "clause 50 PA snapshot drift")
    check(c50.get("components", {}).get("PR_npf", {}).get("measurement_time") == "NOT_SEPARATELY_SPECIFIED_IN_CLAUSE_50", "clause 50 PR scope widened")
    check("measurement_time" not in c50, "clause 50 snapshot incorrectly generalized to whole formula")
    for rule_id in ("PP92-C51-POSITION-10-4", "PP92-C52-POSITION-10-5"):
        rule = by_id.get(rule_id, {})
        check(rule.get("measurement_time") == "TENTH_WORKING_DAY_OF_CALENDAR_YEAR", f"{rule_id}: measurement time drift")
        check("deadline" not in rule, f"{rule_id}: measurement snapshot converted to deadline")
    check(by_id.get("PP92-C49-POSITION-10-2", {}).get("glyph_context_guard") is not None, "reused Q_o glyph context guard missing")
    extraction = matrix.get("extraction", {})
    check(extraction.get("formula_images_verified") == 10, "formula verification count drift")
    check(extraction.get("all_primary_pages_rendered") is True, "all-pages render gate drift")
    for rule_id in ("PP92-C42-P-AVG", "PP92-C43-S-I", "PP92-C44-C-MAX", "PP92-C45-ASSOCIATED-HARM", "PP92-C46-BUDGET-DENOMINATOR", "PP92-C48-POSITION-10-1", "PP92-C49-POSITION-10-2"):
        for item in by_id.get(rule_id, {}).get("numeric_rules", []):
            check("RETENTION" not in item.get("kind", ""), f"{rule_id}: calculation period converted to retention")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS PP RF 92/2026: immutable source, 12 governance, 23 routing and 20 calculation rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
