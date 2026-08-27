from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLASSIFICATION = ROOT / "security-knowledge" / "classification"
EVIDENCE = ROOT / "security-knowledge" / "evidence"

FILES = {
    "402": {
        "matrix": CLASSIFICATION / "pp-rf-402-2026-communications-kii-overlay-v1.json",
        "manifest": EVIDENCE / "primary-artifact-pp-rf-402-2026.json",
        "artifact": EVIDENCE / "primary-artifacts" / "2026" / "pp-rf-402-2026-0001202604130022.pdf",
        "sha": "f666ccb125601dcf0b413ff7aed8f04dba1a74cd0f14655c98fb4f4277c345fc",
        "bytes": 2443943,
        "pages": 10,
    },
    "796": {
        "matrix": CLASSIFICATION / "pp-rf-796-2026-defence-industry-kii-overlay-v1.json",
        "manifest": EVIDENCE / "primary-artifact-pp-rf-796-2026.json",
        "artifact": EVIDENCE / "primary-artifacts" / "2026" / "pp-rf-796-2026-0001202606290031.pdf",
        "sha": "6237b4167295d12b35115f65690e449528a06b0be6c9deac747a1395c23e74c4",
        "bytes": 3722073,
        "pages": 16,
    },
}

FAMILY_PATH = CLASSIFICATION / "kii-sector-overlay-family-scope-2026-v1.json"
FIXTURE_PATH = CLASSIFICATION / "kii-sector-overlay-family-scope-2026-regression-v1.json"


def main() -> int:
    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    matrices: dict[str, dict] = {}
    for number, spec in FILES.items():
        matrix = json.loads(spec["matrix"].read_text(encoding="utf-8"))
        manifest = json.loads(spec["manifest"].read_text(encoding="utf-8"))
        data = spec["artifact"].read_bytes()
        matrices[number] = matrix
        source = matrix.get("source", {})
        artifact = manifest.get("artifact", {})

        check(matrix.get("status") == "VERIFIED_PRIMARY_IMMUTABLE", f"PP {number} status drift")
        check(source.get("sha256") == spec["sha"] == artifact.get("sha256"), f"PP {number} SHA metadata drift")
        check(source.get("byte_length") == spec["bytes"] == artifact.get("byte_length"), f"PP {number} byte metadata drift")
        check(source.get("pdf_pages") == spec["pages"] == artifact.get("pages"), f"PP {number} page metadata drift")
        check(matrix.get("extraction", {}).get("ocr_is_evidence") is False, f"PP {number} OCR promoted to evidence")
        check(matrix.get("extraction", {}).get("all_primary_pages_rendered") is True, f"PP {number} pages not fully rendered")
        check(len(matrix.get("extraction", {}).get("primary_pages_visually_checked", [])) == spec["pages"], f"PP {number} visual page coverage drift")

        check(data.startswith(b"%PDF-1.5"), f"PP {number} PDF magic/version drift")
        check(len(data) == spec["bytes"], f"PP {number} artifact byte mismatch")
        check(hashlib.sha256(data).hexdigest() == spec["sha"], f"PP {number} artifact SHA mismatch")
        check(re.search(rb"/Encrypt\b", data) is None, f"PP {number} artifact unexpectedly encrypted")
        check(re.search(rb"/JavaScript\b|/JS\s*(?:\d+\s+\d+\s+R|\()", data) is None, f"PP {number} artifact contains JavaScript")

    m402 = matrices["402"]
    rules402 = sum(
        (m402.get(name, []) for name in (
            "governance_rules", "commission_and_assessment_rules", "indicator_routing_rules",
            "input_and_method_rules", "calculation_rules"
        )), []
    )
    by402 = {rule.get("id"): rule for rule in rules402}
    check(len(by402) == 22 == len(rules402), "PP 402 rule count or IDs drift")
    lifecycle402 = m402.get("lifecycle", {})
    check(lifecycle402.get("state_as_of") == "ADOPTED_NOT_IN_FORCE", "PP 402 prematurely marked in force")
    check(lifecycle402.get("effective_from") == "2026-09-01", "PP 402 commencement drift")
    check(lifecycle402.get("valid_until_as_stated") == "2032-09-01", "PP 402 valid-until date drift")
    check(lifecycle402.get("valid_until_qualifier") == "UNTIL_DATE_AS_STATED_NO_INCLUSIVE_END_ASSUMPTION", "PP 402 valid-until qualifier drift")
    routed402 = {p for rule in m402.get("indicator_routing_rules", []) for p in rule.get("positions", [])}
    check(routed402 == {"4(a)", "4(b)", "6", "8", "9"}, "PP 402 routing positions drift")
    check(by402.get("PP402-C13-POSITION-4A", {}).get("rule", "").find("separately") >= 0, "PP 402 per-service split lost")
    check(by402.get("PP402-C16-POSITION-8-FORMULA", {}).get("formula") == "P8 = abs((D_actual - D_average) / D_average) * 100", "PP 402 position 8 formula drift")
    fallback = by402.get("PP402-C17-POSITION-8-INPUTS", {}).get("fallback", {})
    check(fallback == {"trigger": "NO_DOCUMENTS_AND_NO_FIVE_YEAR_STATISTICS_FOR_REMEDIATION_TIME", "value": 10, "unit": "DAY"}, "PP 402 ten-day fallback drift")
    check(by402.get("PP402-C18-POSITION-9-FORMULA", {}).get("formula") == "P9 = Delta_payments / B_average * 100", "PP 402 position 9 formula drift")
    check(by402.get("PP402-C19-POSITION-9-INPUTS", {}).get("budget_window", {}).get("direction") == "PLANNED", "PP 402 planned budget window drift")

    m796 = matrices["796"]
    rules796 = sum(
        (m796.get(name, []) for name in (
            "governance_rules", "submission_and_lifecycle_rules", "indicator_and_dependency_rules", "calculation_rules"
        )), []
    )
    by796 = {rule.get("id"): rule for rule in rules796}
    check(len(by796) == 39 == len(rules796), "PP 796 rule count or IDs drift")
    lifecycle796 = m796.get("lifecycle", {})
    check(lifecycle796.get("state_as_of") == "IN_FORCE", "PP 796 lifecycle drift")
    check(lifecycle796.get("effective_from") == "2026-07-07", "PP 796 effective date drift")
    check(lifecycle796.get("effective_date_confidence") == "DERIVED_FROM_PRIMARY_PUBLICATION_AND_GENERAL_RULE", "PP 796 confidence drift")
    submission = by796.get("PP796-C6-MINPROMTORG-ROUTE", {})
    check(submission.get("timing", {}).get("kind") == "NO_EXPLICIT_NUMERIC_DEADLINE", "PP 796 numeric submission deadline invented")
    check("value" not in submission.get("timing", {}), "PP 796 submission timing value invented")
    cadence = by796.get("PP796-C9-REVIEW-CADENCE", {}).get("minimum_review_intervals", [])
    check([(x.get("category", x.get("decision")), x.get("value")) for x in cadence] == [("NO_CATEGORY_REQUIRED", 1), ("THIRD", 2), ("SECOND", 3), ("FIRST", 5)], "PP 796 review cadence drift")
    expected_positions = {"1", "2", "3", "4", "6", "7", "8", "9", "10", "10^1", "10^2", "10^3", "10^4", "10^5", "10^6", "10^7", "11", "12", "13", "13^1"}
    check(set(by796.get("PP796-C7-APPLICABLE-POSITIONS", {}).get("positions", [])) == expected_positions, "PP 796 applicable positions drift")
    check(by796.get("PP796-C14-POSITION-3-DELEGATION", {}).get("calculation_source") == "TRANSPORT_SECTOR_CII_CATEGORIZATION_OVERLAY", "PP 796 transport delegation drift")
    check(by796.get("PP796-C14-POSITION-3-DELEGATION", {}).get("dependency_status_as_of_2026_08_27") == "PROJECT_ONLY_ADOPTED_ACT_NOT_IDENTIFIED_IN_BOUNDED_SEARCH", "PP 796 transport project-only status drift")
    check(by796.get("PP796-C14-POSITION-3-DELEGATION", {}).get("execution_guard") == "FAIL_CLOSED_PENDING_ADOPTED_EFFECTIVE_ACT_AND_PRIMARY_BYTES", "PP 796 transport execution guard drift")
    check(by796.get("PP796-C15-POSITION-4-DELEGATION", {}).get("calculation_source", "").endswith("PP_RF_402_2026"), "PP 796 communications delegation drift")
    check(by796.get("PP796-C30-POSITIONS-10-10_7-DELEGATION", {}).get("calculation_source", "").endswith("PP_RF_92_2026"), "PP 796 financial delegation drift")
    formula_expectations = {
        "PP796-C18-POSITION-8-PERCENT": "U8 = U_loss8 / R_annual * 100",
        "PP796-C19-POSITION-8-DAMAGE": "U_loss8 = C + A + X",
        "PP796-C24-POSITION-9-PERCENT": "U9 = U_loss9 / N_average * 100",
        "PP796-C34-POSITION-13A": "DeltaV = (1 - (V_max - V_incident) / V_SDO) * 100",
        "PP796-C38-POSITION-13B": "T = (1 - t_normal / t_abnormal) * 100",
    }
    for rule_id, expected in formula_expectations.items():
        check(by796.get(rule_id, {}).get("formula") == expected, f"PP 796 formula drift: {rule_id}")
    check(by796.get("PP796-C35-NONPOSITIVE-STOP", {}).get("rule") == "Do not continue the clause 34 calculation.", "PP 796 clause 35 promoted beyond calculation stop")
    check("do not calculate" in by796.get("PP796-C39-T_ABNORMAL", {}).get("stop_rule", "").lower(), "PP 796 clause 39 stop rule lost")

    family = json.loads(FAMILY_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    check(family.get("record_id") == fixture.get("family_matrix_id"), "family fixture mismatch")
    check(family.get("family_definition", {}).get("exhaustiveness_state") == "VERIFIED_OFFICIAL_PUBLICATION_SET_AS_OF_DATE", "family official-publication scope drift")
    members = family.get("members", [])
    member_ids = [member.get("act_id") for member in members]
    publications = [member.get("publication_number") for member in members]
    check(member_ids == fixture.get("required_member_ids"), "family member set/order drift")
    check(publications == fixture.get("required_publication_numbers"), "family publication set/order drift")
    check(len(set(member_ids)) == 7 == len(members), "family members duplicated or missing")
    states = {member["act_id"]: member["lifecycle_state"] for member in members}
    check(states.get("PP_RF_402_2026") == "ADOPTED_NOT_IN_FORCE", "family loses PP 402 temporal state")
    check(states.get("PP_RF_796_2026") == "IN_FORCE", "family loses PP 796 temporal state")
    pending_transport = [edge for edge in family.get("dependency_edges", []) if edge.get("to", "").startswith("TRANSPORT_")]
    check(len(pending_transport) == 1 and pending_transport[0].get("status") == "PENDING_ADOPTED_PRIMARY_PUBLICATION_PROJECT_ONLY", "transport dependency silently resolved or lost")
    decisions = {row.get("candidate"): row.get("decision") for row in family.get("candidate_reconciliation", [])}
    check(decisions == {"PP_RF_402_2026": "INCLUDE", "PP_RF_796_2026": "INCLUDE"}, "candidate reconciliation drift")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS KII overlay family: PP 402 and PP 796 immutable sources, 61 mapped rules, verified 7-member official-publication scope and fail-closed transport dependency")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
