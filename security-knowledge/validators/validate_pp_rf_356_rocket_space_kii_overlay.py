from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "security-knowledge" / "classification" / "pp-rf-356-2026-rocket-space-kii-overlay-v1.json"
FIXTURE_PATH = ROOT / "security-knowledge" / "classification" / "pp-rf-356-2026-rocket-space-kii-overlay-regression-v1.json"
MANIFEST_PATH = ROOT / "security-knowledge" / "evidence" / "primary-artifact-pp-rf-356-2026.json"
ARTIFACT_PATH = ROOT / "security-knowledge" / "evidence" / "primary-artifacts" / "2026" / "pp-rf-356-2026-0001202604010039.pdf"
EXPECTED_SHA256 = "830efe29784ac04b57b9d6f56ab2d3c9a7cf4c75c2ddc6f18ba9efbbd8d9df1b"


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
    check(matrix.get("act", {}).get("effective_from") == "2026-04-09", "effective date drift")
    check(matrix.get("act", {}).get("effective_date_confidence") == "DERIVED_FROM_PRIMARY_PUBLICATION_AND_GENERAL_RULE", "effective-date confidence drift")
    check(source.get("sha256") == EXPECTED_SHA256 == artifact.get("sha256"), "SHA-256 metadata drift")
    check(source.get("byte_length") == 1686133 == artifact.get("byte_length"), "byte length drift")
    check(source.get("pdf_pages") == 8 == artifact.get("pages"), "page count drift")
    check(matrix.get("extraction", {}).get("ocr_is_evidence") is False, "OCR must not be evidence")

    data = ARTIFACT_PATH.read_bytes()
    check(data.startswith(b"%PDF-1.5"), "artifact PDF magic/version drift")
    check(len(data) == 1686133, "artifact byte length mismatch")
    check(hashlib.sha256(data).hexdigest() == EXPECTED_SHA256, "artifact SHA-256 mismatch")
    check(re.search(rb"/Encrypt\b", data) is None, "artifact unexpectedly encrypted")
    check(re.search(rb"/JavaScript\b|/JS\s*(?:\d+\s+\d+\s+R|\()", data) is None, "artifact contains JavaScript")

    group_names = ("governance_rules", "submission_rules", "indicator_routing_rules", "assessment_rules", "calculation_rules")
    groups = {name: matrix.get(name, []) for name in group_names}
    for name, expected in fixture.get("required_counts", {}).items():
        check(len(groups[name]) == expected, f"{name} count drift")
    all_rules = sum(groups.values(), [])
    by_id = {item.get("id"): item for item in all_rules}
    check(len(by_id) == len(all_rules), "rule IDs missing or duplicated")

    check(by_id.get("PP356-C6-INTERACTION-MERGE", {}).get("normative_strength") == "DISCRETIONARY", "optional interaction merge promoted to mandatory")
    check(by_id.get("PP356-C7-MODERNIZATION-SPLIT", {}).get("normative_strength") == "DISCRETIONARY", "optional modernization split promoted to mandatory")
    submission = by_id.get("PP356-C8-ROSCOSMOS-SUBMISSION", {})
    check(submission.get("recipient") == "ROSCOSMOS_STATE_CORPORATION", "Roscosmos route drift")
    check(submission.get("timing", {}).get("kind") == "NO_EXPLICIT_NUMERIC_DEADLINE", "numeric deadline invented for clause 8")
    check("value" not in submission.get("timing", {}), "numeric deadline value invented for clause 8")

    routed = {position for rule in groups["indicator_routing_rules"] for position in rule.get("positions", [])}
    check(routed == set(fixture.get("required_indicator_positions", [])), "indicator routing positions drift")
    check(by_id.get("PP356-C9B-POSITIONS-8-9", {}).get("subjects") == "ALL_ROCKET_SPACE_CII_SUBJECTS", "Roscosmos exclusion incorrectly extended to positions 8 and 9")
    check("EXCEPT_ROSCOSMOS" in by_id.get("PP356-C9A-POSITION-1", {}).get("subjects", ""), "position 1 Roscosmos exclusion lost")
    check("EXCEPT_ROSCOSMOS" in by_id.get("PP356-C9C-POSITION-11", {}).get("subjects", ""), "position 11 Roscosmos exclusion lost")

    formulas = fixture.get("required_formulas", {})
    for rule_id, lookback in fixture.get("required_lookbacks", {}).items():
        rule = by_id.get(rule_id, {})
        check(rule.get("percentage_formula") == formulas.get("percentage"), f"percentage formula drift: {rule_id}")
        check(rule.get("damage_formula") == formulas.get("damage"), f"damage formula drift: {rule_id}")
        check(rule.get("lookback", {}).get("value") == lookback, f"lookback drift: {rule_id}")
        check(rule.get("lookback", {}).get("unit") == "YEAR", f"lookback unit drift: {rule_id}")
        check(rule.get("negative_delta_rule", {}).get("stated_basis") == "t_maintenance", f"negative-delta basis drift: {rule_id}")
        check("RETENTION" not in rule.get("lookback", {}).get("unit", ""), f"lookback converted to retention: {rule_id}")
    delegated = by_id.get("PP356-C15-POSITIONS-13-13-1", {})
    check(delegated.get("calculation_source") == "SECTOR_SPECIFIC_CATEGORIZATION_FEATURES_FOR_DEFENCE_INDUSTRY_CII", "delegated defence-industry calculation source drift")
    check("formula" not in delegated, "delegated positions received an invented formula")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS PP RF 356/2026: immutable source, 7 governance, 1 submission, 5 routing, 4 assessment and 5 calculation rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
