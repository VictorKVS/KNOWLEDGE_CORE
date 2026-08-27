from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "security-knowledge" / "classification" / "pp-rf-246-2026-science-kii-overlay-v1.json"
FIXTURE_PATH = ROOT / "security-knowledge" / "classification" / "pp-rf-246-2026-science-kii-overlay-regression-v1.json"
MANIFEST_PATH = ROOT / "security-knowledge" / "evidence" / "primary-artifact-pp-rf-246-2026.json"
ARTIFACT_PATH = ROOT / "security-knowledge" / "evidence" / "primary-artifacts" / "2026" / "pp-rf-246-2026-0001202603070013.pdf"
VISUAL_EVIDENCE_PATH = ROOT / "security-knowledge" / "evidence" / "pp-rf-246-2026-primary-pdf-visual-verification-2026-08-27.yaml"
EXPECTED_SHA256 = "07047bc77584b469d0be258540b10565f12e8d8c3d54ba387ecdc4a397073aef"


def main() -> int:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    visual_evidence = VISUAL_EVIDENCE_PATH.read_text(encoding="utf-8")
    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    source = matrix.get("source", {})
    artifact = manifest.get("artifact", {})
    check(matrix.get("status") == "VERIFIED_PRIMARY_IMMUTABLE", "matrix status drift")
    check(matrix.get("record_id") == fixture.get("matrix_id"), "fixture matrix mismatch")
    check(matrix.get("act", {}).get("effective_from") == "2026-03-15", "effective date drift")
    check(matrix.get("act", {}).get("effective_date_confidence") == "DERIVED_FROM_PRIMARY_PUBLICATION_AND_GENERAL_RULE", "effective-date confidence drift")
    check(source.get("sha256") == EXPECTED_SHA256 == artifact.get("sha256"), "SHA-256 metadata drift")
    check(source.get("byte_length") == 2509532 == artifact.get("byte_length"), "byte length drift")
    check(source.get("pdf_pages") == 10 == artifact.get("pages"), "page count drift")
    check(matrix.get("extraction", {}).get("ocr_is_evidence") is False, "OCR must not be evidence")
    check(matrix.get("extraction", {}).get("primary_pages_visually_checked") == list(range(1, 11)), "all primary pages must be visually checked")
    check(matrix.get("extraction", {}).get("standalone_formula_images_expected") == 0, "prose-only act formula count drift")
    check(manifest.get("verification", {}).get("all_pages_visually_checked") == list(range(1, 11)), "manifest visual page gate drift")
    check("VERIFIED_PRIMARY_IMMUTABLE_PROSE_ONLY_NO_STANDALONE_FORMULAS" in visual_evidence, "visual evidence status drift")
    check(visual_evidence.count("pdf_page:") == 10, "visual page hash count drift")

    data = ARTIFACT_PATH.read_bytes()
    check(data.startswith(b"%PDF-1.5"), "artifact PDF magic/version drift")
    check(len(data) == 2509532, "artifact byte length mismatch")
    check(hashlib.sha256(data).hexdigest() == EXPECTED_SHA256, "artifact SHA-256 mismatch")
    check(re.search(rb"/Encrypt\b", data) is None, "artifact unexpectedly encrypted")
    check(re.search(rb"/JavaScript\b|/JS\s*(?:\d+\s+\d+\s+R|\()", data) is None, "artifact contains JavaScript")

    group_names = ("governance_rules", "indicator_routing_rules", "calculation_rules", "temporal_rules")
    groups = {name: matrix.get(name, []) for name in group_names}
    for name, expected in fixture.get("required_counts", {}).items():
        check(len(groups[name]) == expected, f"{name} count drift")
    all_rules = sum(groups.values(), [])
    by_id = {item.get("id"): item for item in all_rules}
    check(len(by_id) == len(all_rules), "rule IDs missing or duplicated")

    covered = by_id.get("PP246-C2-COVERED-SUBJECTS", {})
    check(set(covered.get("subject_types", [])) == set(fixture.get("required_subject_types", [])), "covered subject types drift")
    check("ALL_SCIENCE_ORGANIZATIONS" not in covered.get("subject_types", []), "science subject scope widened")
    check(by_id.get("PP246-C7-MODERNIZATION-SPLIT", {}).get("normative_strength") == "DISCRETIONARY", "optional modernization split promoted to mandatory")
    check(fixture.get("required_outside_list_rule") in by_id, "outside-list consequence rule missing")

    routing = groups["indicator_routing_rules"]
    check({r.get("position") for r in routing} == set(fixture.get("required_indicator_positions", [])), "indicator routing positions drift")
    check(by_id.get("PP246-C9E-POSITION-13-1", {}).get("applicable_when") == "SUBJECT_PERFORMS_R_AND_D_UNDER_THE_STATE_DEFENCE_ORDER", "position 13^1 state-defence-order route drift")
    trl = by_id.get("PP246-C11-TRL-AND-INDICATORS", {}).get("numeric_rule", {})
    check(trl.get("kind") == "MINIMUM_TECHNOLOGY_READINESS_LEVEL", "TRL 7 converted to another numeric rule")
    check(trl.get("value") == fixture.get("required_minimum_technology_readiness_level"), "TRL threshold drift")

    check(groups["temporal_rules"] == [], "overlay-specific deadline invented")
    check(not any("deadline" in rule for rule in all_rules), "numeric value converted into deadline")
    check(by_id.get("PP246-C12-APPLICABILITY-FIRST") is not None, "applicability-first gate missing")
    check(by_id.get("PP246-C13-NO-CALCULATION-WHEN-INAPPLICABLE") is not None, "inapplicable-indicator gate missing")
    check(by_id.get("PP246-C10-WORST-CASE") is not None, "worst-case gate missing")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS PP RF 246/2026: immutable source, 10 governance, 5 routing and 14 calculation rules; no invented deadline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
