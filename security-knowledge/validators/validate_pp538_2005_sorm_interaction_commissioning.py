#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/government-decrees/538-2005/sorm-interaction-commissioning-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/government-decrees/538-2005/sorm-interaction-commissioning-regression-v1.json")


def evaluate(c):
    q = c["query"]
    if q == "identity":
        if c["date"] == "2005-08-27" and c["title_family"] == "SORM": return "PP538_2005_SORM"
        if c["date"] == "2025-04-24" and c["title_family"] == "ANONYMIZATION": return "PP538_2025_ANONYMIZATION"
        return "BLOCK_AMBIGUOUS_NUMBER_ONLY"
    if q == "version": return "CURRENT_2021_REVISION" if date.fromisoformat(c["as_of"]) >= date(2021, 4, 30) else "HISTORICAL_PRE_CURRENT_REVISION"
    if q == "fsb_unit_application": return "PASS" if c["days_from_license"] <= 45 else "BLOCK_LATE_APPLICATION"
    if q == "fsb_unit_designation": return "PASS" if c["working_days"] <= 30 else "BLOCK_LATE_DESIGNATION"
    if q == "fsb_unit_designation_claim": return "REJECT_WORKING_DAY_CONFLATION"
    if q == "interior_route": return "CONDITIONAL_INTERIOR_ROUTE" if c["fsb_lacks_capability"] else "NO_INTERIOR_ROUTE"
    if q == "technical_room":
        if not c["requirements_absent"]: return "NO_POINT6_ROUTE"
        if not c["fsb_request"]: return "BLOCK_REQUEST_MISSING"
        return "PASS" if c["conforming"] else "BLOCK_CONFORMANCE_UNPROVEN"
    if q == "plan":
        if not c["joint"]: return "BLOCK_NOT_JOINT"
        if c["months_from_application"] > 3: return "BLOCK_PLAN_LATE"
        return "PASS" if c["deadline_in_plan"] else "BLOCK_COMMISSIONING_DEADLINE_MISSING"
    if q == "plan_claim": return "REJECT_UNIT_CONVERSION"
    if q == "plan_copies": return "PASS" if (c["copies"],c["rkn"],c["fsb"],c["operator"]) == (3,1,1,1) else "BLOCK_COPY_DISTRIBUTION"
    if q == "new_plan_trigger": return "DECISION_ROUTE" if c["trigger"] in {"NEW_COMMUNICATIONS_MEANS","NEW_TECHNOLOGICAL_SOLUTION","DECOMMISSION_OLD_MEANS","MODERNIZE_OLD_MEANS"} else "NO_ENUMERATED_TRIGGER"
    if q == "commissioning":
        if not all(c[k] for k in ("fsb","supervision","operator")): return "BLOCK_REQUIRED_SIGNATORY"
        if c["point3"] and not c["interior"]: return "BLOCK_CONDITIONAL_INTERIOR_SIGNATORY"
        return "PASS"
    if q == "commissioning_claim": return "PASS" if c["signed_act"] else "BLOCK_NO_SIGNED_ACT"
    if q == "personnel_control":
        if not c["fsb_agreed"]: return "BLOCK_FSB_AGREEMENT"
        if not c["limited"]: return "BLOCK_PERSONNEL_LIMIT"
        return "PASS" if c["nondisclosure"] else "BLOCK_NONDISCLOSURE"
    if q == "database_retention":
        if c["years"] != 3: return "BLOCK_PERIOD"
        return "PASS" if c["location"] == "RUSSIA" else "BLOCK_LOCATION"
    if q == "database_claim": return "REJECT_METADATA_CONTENT_CONFLATION"
    if q == "remote_access":
        if c["actor"] == "INTERIOR" and not c.get("point3", False): return "BLOCK_NO_POINT3_CASE"
        return "PASS" if c["continuous"] else "BLOCK_NOT_CONTINUOUS"
    if q == "request_route":
        if not c["through_fsb"]: return "BLOCK_WRONG_ROUTE"
        return "PASS" if c["all_discrepancies"] else "BLOCK_INCOMPLETE_DISCREPANCIES"
    if q == "request_cap":
        caps={"15_DAYS":0.3,"CALENDAR_MONTH":0.6,"CALENDAR_YEAR":5}
        return "PASS" if c["percent"] <= caps[c["period"]] else "BLOCK_CAP"
    if q == "request_response": return "PASS" if c["days"] <= 15 else "BLOCK_LATE_RESPONSE"
    if q == "request_response_claim": return "REJECT_WORKING_DAY_INSERTION"
    if q == "cap_excess_notice": return "NO_NUMERIC_DEADLINE_STATED"
    if q == "connection_point": return "PASS" if c["fsb_determined"] else "BLOCK_FSB_POINT_UNPROVEN"
    if q == "content_provision":
        if not c["russia_storage"]: return "BLOCK_LOCATION"
        return "PASS" if c["federal_law_case"] else "BLOCK_NO_FEDERAL_LAW_CASE"
    if q == "closed_methods": return "BLOCK_OUT_OF_SCOPE"
    raise AssertionError(q)


def main():
    model=yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({x["id"] for x in model["atomic_rules"]}) == 31
    assert len(model["evidence_model"]) == len({x["id"] for x in model["evidence_model"]}) == 18
    assert len(model["temporal_model"]) == 6
    assert model["source"]["current_revision"] == "2021-04-17"
    assert model["source"]["current_revision_effective_from"] == "2021-04-30"
    assert model["identifier_collision_guard"]["rule"] == "NEVER_JOIN_BY_NUMBER_WITHOUT_DATE_AND_TITLE"
    assert model["temporal_model"][2]["operator_application_max_calendar_days_from_license"] == 45
    assert model["temporal_model"][2]["fsb_head_designation_max_working_days_from_application"] == 30
    assert model["temporal_model"][4]["operator_response_max_days_from_request"] == 15
    assert model["temporal_model"][5]["value"] == 3
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert len(fixtures["cases"]) == 64
    failures=[]
    for c in fixtures["cases"]:
        actual=evaluate(c)
        if actual != c["expected"]: failures.append((c["id"],c["expected"],actual))
    if failures:
        for f in failures: print("FAIL",f)
        raise SystemExit(1)
    print("PASS: PP538/2005 current; 31 rules, 6 temporal routes, 18 evidence nodes, 64 cases; PP538/2025 collision blocked")


if __name__ == "__main__": main()
