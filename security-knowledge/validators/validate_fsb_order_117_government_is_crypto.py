#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml

MODEL = Path("security-knowledge/legislation/RU/regulators/FSB/117-2025/atomic-requirements-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/regulators/FSB/117-2025/regression-v1.json")
FSB378 = Path("security-knowledge/corpus/ru-personal-data/fsb-order-378-ispdn-crypto-controls-atomic-v1.yaml")


def strongest(classes, order):
    return max(classes, key=order.index)


def evaluate(c, model):
    q = c["query"]
    order = model["class_order_weak_to_strong"]
    if q == "version":
        return "NOT_YET_EFFECTIVE" if date.fromisoformat(c["as_of"]) < date(2025, 4, 6) else "CURRENT_ORIGINAL"
    if q == "repeal":
        return "REPEALED_BY_FSB117" if c["order"] == 524 else "NOT_REPEALED_ROUTE_IF_APPLICABLE"
    if q == "scope":
        if c["excluded"]:
            return "EXCLUDED_ROUTE_OTHER_REQUIREMENTS"
        return "OUTSIDE_FSB117_SYSTEM_SCOPE" if c["system"] == "PRIVATE_IS" else "COVERED_SYSTEM_REVIEW_TRIGGERS"
    if q == "applicability":
        valid = {"NPA_REQUIRES_SKZI", "CHANNEL_OUTSIDE_CONTROLLED_ZONE", "E_DOCUMENT_EQUIVALENCE", "MEDIA_THIRD_PARTY_ACCESS_NOT_EXCLUDABLE_NONCRYPTO"}
        return "SKZI_REQUIRED" if valid.intersection(c["triggers"]) else "NO_FSB117_CRYPTO_TRIGGER_PROVEN"
    if q == "justification":
        if not c["threat_model"]: return "BLOCK_THREAT_MODEL"
        if not c["technical_design"]: return "BLOCK_TECHNICAL_DESIGN"
        if not c["technical_spec"]: return "BLOCK_TECHNICAL_SPECIFICATION"
        return "PASS"
    if q == "gis_agreement":
        return "PASS" if not c["gis"] or c["agreed"] else "BLOCK_FSB_CRYPTO_PART_AGREEMENT"
    if q == "matrix":
        return model["minimum_class_matrix"][c["significance"]][c["scale"]]
    if q == "threat_escalation":
        base, cap = c["base"], c["capability"]
        if cap == "KA_SPECIALISTS": return "KA"
        if cap == "KV_SPECIALISTS" and base in {"KS1","KS2","KS3"}: return "KV"
        if cap == "INSIDE_PHYSICAL" and base in {"KS1","KS2"}: return "KS3"
        if cap == "INSIDE_NO_PHYSICAL" and base == "KS1": return "KS2"
        if cap == "OUTSIDE_ZONE" and base == "KS1": return "KS1"
        return base
    if q == "citizen":
        return "MAY_USE_LOWER_THREAT_BASED_CLASS" if c["threat_supports_lower"] else "SYSTEM_CLASS"
    if q == "interaction":
        return strongest(c["classes"], order) if not c["same_system"] else f"NOT_LOWER_THAN_LEAST_{c['classes'][0]}_EXPERT_REVIEW"
    if q == "cross_npa":
        return strongest([c["fsb117"], c["other"]], order)
    if q == "environment":
        if not c["documentation_requires"]: return "NOT_APPLICABLE"
        if not c["assessment"]: return "BLOCK_ASSESSMENT"
        return "PASS" if c["positive"] else "BLOCK_PROTECTED_PROCESSING"
    if q == "room":
        if not c["rules"] or not c["list"]: return "BLOCK_BASIC_CONTROLS"
        if c["federal_high"] and not c["special"]: return "BLOCK_SPECIAL_CONTROLS"
        return "PASS_SPECIAL" if c["federal_high"] else "PASS_BASIC"
    if q == "certificate":
        if not c["certified"]: return "BLOCK_FSB_CERTIFICATION"
        return "PASS" if c["current_product_evidence"] else "BLOCK_CURRENT_PRODUCT_EVIDENCE"
    if q == "license":
        return "DO_NOT_INFER_PP313_LICENSE" if c["internal_use_only"] else "CLASSIFY_ACTUAL_REGULATED_ACTIVITY"
    raise AssertionError(q)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    fsb378 = yaml.safe_load(FSB378.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == 44
    assert len({r["id"] for r in model["atomic_rules"]}) == 44
    assert sum(len(v) for v in model["minimum_class_matrix"].values()) == 9
    assert len(model["evidence_model"]) == 18
    assert len(fixtures["cases"]) == 52
    assert model["verification_boundary"]["clauses_1_to_18_and_appendix"] == "VERIFIED"
    assert model["verification_boundary"]["numeric_deadlines_in_requirements"] == "NONE_FOUND"
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert fsb378["id"] == "RU-FSB378-ISPDN-CRYPTO-CONTROLS-ATOMIC-V1"
    assert fsb378["class_order_weak_to_strong"] == model["class_order_weak_to_strong"]
    failures=[]
    for case in fixtures["cases"]:
        actual=evaluate(case,model)
        if actual != case["expected"]: failures.append((case["id"],case["expected"],actual))
    if failures:
        for f in failures: print("FAIL",f)
        raise SystemExit(1)
    print("PASS: 44 atomic rules; 9 matrix routes; 18 evidence nodes; 52 cases")


if __name__ == "__main__": main()
