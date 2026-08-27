#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/joint-orders/mindigital-fsb-245-127-2022/sorm-plan-requirements-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/joint-orders/mindigital-fsb-245-127-2022/sorm-plan-requirements-regression-v1.json")


def evaluate(c):
    q = c["query"]
    if q == "version":
        return "CURRENT_245_127" if date.fromisoformat(c["as_of"]) >= date(2022, 8, 13) else "PREDECESSOR_391_437"
    if q == "copies": return "PASS" if c["count"] == 3 else "BLOCK_COPY_COUNT"
    if q == "plan_field":
        if c.get("triggered") is False: return "NOT_APPLICABLE"
        return "PASS" if c["present"] else "BLOCK_MISSING_PLAN_FIELD"
    if q == "instruction": return "PASS" if all(c[k] for k in ("deadline", "nondisclosure", "information_protection")) else "BLOCK_INSTRUCTION_CONTENT"
    if q == "personnel_lists": return "PASS" if all(c[k] for k in ("installation", "service", "separate_deadlines")) else "BLOCK_PERSONNEL_LISTS"
    if q == "tests": return "PASS" if all(c[k] for k in ("preliminary_deadline", "preliminary_procedure", "acceptance_deadline", "acceptance_requirements")) else "BLOCK_TEST_FIELDS"
    if q == "pilot": return "PASS" if c["deadline"] and c["remediation"] else "BLOCK_PILOT_REMEDIATION"
    if q == "commissioning_deadline": return "PASS" if c["present"] else "BLOCK_MISSING_PLAN_FIELD"
    if q == "attachment":
        if c.get("triggered") is False: return "NOT_APPLICABLE"
        return "PASS" if c["present"] else "BLOCK_MISSING_ATTACHMENT"
    if q == "approval": return "PASS" if c["authorized_body"] and c["operator"] else "BLOCK_APPROVAL"
    if q == "connector_agreement":
        if not c["uses_connector_means"]: return "NOT_APPLICABLE"
        return "PASS" if c["agreed"] else "BLOCK_CONNECTOR_AGREEMENT"
    if q == "connector_route": return "PASS" if all(c[k] for k in ("diagram_agreed", "all_traffic", "single_point", "capability", "commissioning_acts", "agreement", "services_agreed")) else "BLOCK_CONNECTOR_ROUTE"
    if q == "deadline_claim": return "REJECT_UNIVERSAL_NUMERIC_DEADLINE"
    if q == "dependency": return "CURRENT_ORDER_245_127" if c["pp538_point"] == 8 else "PENDING_SEPARATE_TECHNICAL_SOURCE_FAMILY"
    if q == "closed_methods": return "BLOCK_OUT_OF_SCOPE"
    raise AssertionError(q)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({x["id"] for x in model["atomic_rules"]}) == 31
    assert len(model["evidence_model"]) == len({x["id"] for x in model["evidence_model"]}) == 15
    assert len(model["temporal_model"]) == 2
    assert len(model["plan_deadline_fields"]["fields"]) == 10
    assert model["plan_deadline_fields"]["universal_numeric_days_or_months_in_order"] == "NONE"
    assert model["legal_route"]["predecessor"]["repealed_from"] == "2022-08-13"
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert len(fixtures["cases"]) == 48
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]: failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures: print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: Order 245/127 current; 31 rules, 2 temporal routes, 15 evidence nodes, 10 plan deadline fields, 48 cases")


if __name__ == "__main__": main()
