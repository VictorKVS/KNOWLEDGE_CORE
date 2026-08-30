#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/risks/gost-r-iso-iec-27005-2010-process-core-v1.yaml")
FIXTURES=Path("security-knowledge/risks/gost-r-iso-iec-27005-2010-process-core-regression-v1.json")
OBS=Path("security-knowledge/evidence/gost-r-iso-iec-27005-2010-process-core-observation-2026-08-30.yaml")
REGISTRY=Path("security-knowledge/standards/gost-and-ru-standards-source-registry.yaml")

def main():
    model=json.loads(MODEL.read_text(encoding="utf-8"))
    fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
    obs=json.loads(OBS.read_text(encoding="utf-8"))
    registry=yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    nodes={x["locator"]:x for x in model["process_nodes"]}
    rules={x["id"]:x["rule"] for x in model["control_rules"]}
    counts=model["counts"]
    assert model["status"]=="VERIFIED_CURRENT_ROSSTANDART_IDENTITY_PUBLIC_TEXT_PROCESS_CORE_SECTIONS_4_TO_12_FAIL_CLOSED"
    assert len(model["section_map"])==counts["section_map"]==9
    assert len(nodes)==counts["process_nodes"]==24
    assert len(model["flow"])==4
    assert len(model["continuous_cross_cutting"])==3
    assert model["treatment_options"]==["REDUCE","RETAIN","AVOID","TRANSFER"]
    assert len(model["treatment_options"])==counts["treatment_options"]==4
    assert model["assessment_modes"]==["QUALITATIVE","QUANTITATIVE","COMBINED"]
    assert len(model["assessment_modes"])==counts["assessment_modes"]==3
    assert len(model["appendices"])==counts["appendices"]==7
    assert all(x["status"]=="INFORMATIVE" for x in model["appendices"])
    assert len(model["evidence_artifacts"])==counts["evidence_artifacts"]==15
    assert len(model["evidence_nodes"])==counts["evidence_nodes"]==18
    assert len(rules)==counts["control_rules"]==64
    assert list(rules)==[f"G27005-R{i:03d}" for i in range(1,65)]
    for locator in ["7.2","7.3","7.4","8.2.1.2","8.2.1.3","8.2.1.4","8.2.1.5","8.2.1.6","8.2.2.1","8.2.2.2","8.2.2.3","8.2.2.4","8.3","9.2","9.3","9.4","9.5","10","11","12.1","12.2"]:
        assert locator in nodes
    assert counts["numeric_deadlines_stated"]==0
    assert counts["default_scales_asserted"]==0
    assert counts["default_formulas_asserted"]==0
    assert counts["default_acceptance_thresholds_asserted"]==0
    assert model["verification_boundary"]["appendix_e_example_parameterization"]=="NOT_PROMOTED_TO_DEFAULT"
    assert model["verification_boundary"]["immutable_official_normative_bytes"]=="PENDING"
    assert model["verification_boundary"]["critical_gap_created"]==0
    assert model["verification_boundary"]["high_gap_created"]==0
    assert len(fixtures["cases"])==64
    failures=[]
    for case in fixtures["cases"]:
        actual=rules[case["rule_id"]]
        if actual!=case["expected"]: failures.append((case["id"],case["expected"],actual))
    if failures:
        for failure in failures: print("FAIL",failure)
        raise SystemExit(1)
    source=next(x for x in registry["sources"] if x["id"]=="GOST_R_ISO_IEC_27005_2010")
    assert source["status_observed"]=="Действует"
    assert source["ingestion_status"]=="REGRESSION_PROTECTED_PROCESS_CORE_SECTIONS_4_TO_12"
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    assert obs["rejected_inferences"][2]=="MANDATORY_MULTIPLICATION_FORMULA"
    print("PASS: GOST R ISO/IEC 27005-2010 sections 4-12; 9 sections, 24 process nodes, 4 treatment options, 3 estimation modes, 15 evidence artifacts, 18 evidence nodes, 64 rules/cases; 0 default scales/formulas/thresholds")

if __name__=="__main__": main()

