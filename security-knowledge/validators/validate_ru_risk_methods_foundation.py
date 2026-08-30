#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/risks/ru-risk-methods-foundation-v1.yaml")
FIXTURES = Path("security-knowledge/risks/ru-risk-methods-foundation-regression-v1.json")
OBS = Path("security-knowledge/evidence/rosstandart-risk-methods-foundation-observation-2026-08-30.yaml")
REGISTRY = Path("security-knowledge/standards/gost-and-ru-standards-source-registry.yaml")

def main():
    model = json.loads(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    obs = json.loads(OBS.read_text(encoding="utf-8"))
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    current = {x["id"]: x for x in model["current_sources"]}
    history = {x["designation"]: x for x in model["historical_replacement_records"]}
    rules = {x["id"]: x["rule"] for x in model["control_rules"]}
    assert model["status"] == "VERIFIED_CURRENT_ROSSTANDART_FOUNDATION_METADATA_SCOPE_AND_REPLACEMENT_CHAINS_FAIL_CLOSED"
    assert len(current) == model["counts"]["current_sources"] == 4
    assert len(history) == model["counts"]["historical_replacement_records"] == 6
    assert len(model["routing"]) == model["counts"]["routing_nodes"] == 5
    assert len(model["evidence_nodes"]) == model["counts"]["evidence_nodes"] == 18
    assert len(rules) == model["counts"]["control_rules"] == 64
    assert list(rules) == [f"RISK-FOUND-{i:03d}" for i in range(1, 65)]
    assert all(x["status"] == "Действует" for x in current.values())
    assert current["GOST_R_ISO_31000_2019"]["replaces"] == ["ГОСТ Р ИСО 31000-2010"]
    assert current["GOST_R_ISO_31073_2024"]["replaces"] == ["ГОСТ Р 51897-2021"]
    assert current["GOST_R_58771_2019"]["replaces"] == ["ГОСТ Р ИСО/МЭК 31010-2011"]
    assert len(current["GOST_R_ISO_IEC_27005_2010"]["replaces"]) == 2
    assert history["ГОСТ Р 51897-2011"]["replaced_by"] == "ГОСТ Р 51897-2021"
    assert history["ГОСТ Р 51897-2021"]["replaced_by"] == "ГОСТ Р ИСО 31073-2024"
    assert model["counts"]["numeric_formulas_asserted"] == 0
    assert model["counts"]["universal_thresholds_asserted"] == 0
    assert model["verification_boundary"]["immutable_official_normative_bytes"] == "PENDING"
    assert model["verification_boundary"]["critical_gap_created"] == 0
    assert model["verification_boundary"]["high_gap_created"] == 0
    assert obs["accepted_claims"][-1] == "ZERO_QUANTITATIVE_FORMULAS_CLAIMED"
    assert len(fixtures["cases"]) == 64
    failures = []
    for case in fixtures["cases"]:
        actual = rules[case["rule_id"]]
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    indexed = {x["id"]: x for x in registry["sources"]}
    for source_id in current:
        assert indexed[source_id]["status_observed"] == "Действует"
        assert str(MODEL) in indexed[source_id]["repo_bindings"]
        assert str(FIXTURES) in indexed[source_id]["repo_bindings"]
    assert indexed["GOST_R_ISO_31000_2019"]["replaces"] == "ГОСТ Р ИСО 31000-2010"
    assert indexed["GOST_R_ISO_31073_2024"]["replaces"] == "ГОСТ Р 51897-2021"
    assert indexed["GOST_R_58771_2019"]["replaces"] == "ГОСТ Р ИСО/МЭК 31010-2011"
    assert len(indexed["GOST_R_ISO_IEC_27005_2010"]["replaces"]) == 2
    print("PASS: 4 current risk standards; 6 historical replacement records; 5 routing nodes; 18 evidence nodes; 64 fail-closed rules/cases; 0 invented formulas or thresholds")

if __name__ == "__main__":
    main()

