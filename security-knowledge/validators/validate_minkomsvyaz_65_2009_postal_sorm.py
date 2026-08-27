#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-65-2009/postal-sorm-requirements-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-65-2009/postal-sorm-requirements-regression-v1.json")


def evaluate(c):
    q = c["query"]
    if q == "scope": return "IN_SCOPE" if c["operator"] == "POSTAL" and c["asset"] in {"NETWORK", "COMMUNICATIONS_MEANS"} else "OUT_OF_SCOPE"
    if q == "transfer_capabilities": return "PASS" if c["services"] and c["users"] and c["items"] else "BLOCK_TRANSFER_CAPABILITY"
    if q == "development": return "PASS" if c["development_or_expansion"] and c["requirements_applied"] else "BLOCK_DEVELOPMENT_ROUTE"
    if q == "request_route": return "PASS" if c["interacting_unit_request"] or c["control_point_request"] else "BLOCK_MISSING_REQUEST"
    if q == "operator_encoding":
        if not c["operator_added_encoding"]: return "NO_GENERAL_DECRYPTION_RULE"
        return "PASS" if c["decoded"] else "BLOCK_OPERATOR_ENCODING"
    if q == "connection": return "PASS" if all(c[k] for k in ("user_db", "service_db", "technical_means", "technical_conditions")) else "BLOCK_CONNECTION_SET"
    if q == "user_lookup": return "PASS" if c["supported"] and c["mode"] in {"PERSONAL_DATA", "POSTAL_ADDRESS"} else "BLOCK_USER_LOOKUP"
    if q == "service_lookup":
        if c["mode"] not in {"PERSONAL_DATA", "POSTAL_ADDRESS"}: return "NOT_STATED_BY_ORDER65"
        return "PASS" if c["supported"] else "BLOCK_SERVICE_LOOKUP"
    if q == "item_control": return "PASS" if all(c[k] for k in ("during_processing", "transferred", "free_packaging_access", "returned")) else "BLOCK_ITEM_CONTROL_CHAIN"
    if q == "decision": return "PASS" if c["action"] in {"SEIZURE", "SUSPENSION"} and c["authorized_decision"] and c["established_procedure"] else "BLOCK_DECISION_ROUTE"
    if q == "room_demand":
        if not c["interacting_unit_requirement"]: return "NOT_TRIGGERED"
        return "PASS" if c["provided"] else "BLOCK_ROOM_DEMAND"
    if q == "technical_control": return "PASS" if c["equipment_route_documented"] and c["technical_conditions"] and c["controlled_from_control_point"] else "BLOCK_TECHNICAL_CONTROL_ROUTE"
    if q == "technical_conditions": return "PASS" if c["items"] == 4 else "BLOCK_INCOMPLETE_TECHNICAL_CONDITIONS"
    if q == "confidentiality": return "PASS" if c["personnel_access_protected"] and c["methods_protected"] and c["rooms_and_personnel_protected"] else "BLOCK_CONFIDENTIALITY"
    if q == "plan_approval": return "PASS" if c["copies"] == 3 and c["supervision_copy"] and c["authorized_body_copy"] and c["two_head_approvals"] else "BLOCK_PLAN_APPROVAL"
    if q == "plan_structure": return "PASS" if (c["field_groups"], c["attachment_groups"]) == (5, 3) else "BLOCK_PLAN_STRUCTURE"
    if q == "plan_deadline": return "PASS_NO_UNIVERSAL_DAYS" if c["case_specific_dates_present"] and c["universal_days"] is None else "BLOCK_PLAN_DEADLINE"
    if q == "room": return "PASS" if c["justified_requirements"] and c["isolated_and_supported"] and c["access_control"] and c["emergency_notification"] else "BLOCK_ROOM_REQUIREMENTS"
    if q == "legal_authority": return "PASS" if c["technical_capability"] and c["separate_lawful_basis"] else "BLOCK_MISSING_LAWFUL_BASIS"
    raise AssertionError(q)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({x["id"] for x in model["atomic_rules"]}) == 60
    assert len(model["evidence_model"]) == len({x["id"] for x in model["evidence_model"]}) == 20
    assert len(model["temporal_model"]) == 2
    assert model["technical_conditions_required_contents"]["count"] == 4
    assert model["plan_model"]["copies"] == 3
    assert model["plan_model"]["required_field_groups"] == 5
    assert model["plan_model"]["attachment_groups"] == 3
    assert model["room_appendix"]["numbered_points"] == 5
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert len(fixtures["cases"]) == 56
    failures=[]
    for case in fixtures["cases"]:
        actual=evaluate(case)
        if actual != case["expected"]: failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures: print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: Order 65 current postal SORM layer; 60 rules, 2 temporal routes, 20 evidence nodes, 4 technical-condition items, 5 plan fields, 3 attachment groups, 5 appendix points, 56 cases")


if __name__ == "__main__": main()
