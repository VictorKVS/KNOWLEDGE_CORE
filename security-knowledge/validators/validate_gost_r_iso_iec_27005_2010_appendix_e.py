#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "security-knowledge/risks/gost-r-iso-iec-27005-2010-appendix-e-v1.yaml"
FIXTURES = ROOT / "security-knowledge/risks/gost-r-iso-iec-27005-2010-appendix-e-regression-v1.json"
OBS = ROOT / "security-knowledge/evidence/gost-r-iso-iec-27005-2010-appendix-e-observation-2026-08-30.yaml"
REGISTRY = ROOT / "security-knowledge/standards/gost-and-ru-standards-source-registry.yaml"

model = json.loads(MODEL.read_text(encoding="utf-8"))
fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
observation = json.loads(OBS.read_text(encoding="utf-8"))
registry = REGISTRY.read_text(encoding="utf-8")

assert model["id"] == fixtures["model_id"]
assert model["as_of"] == "2026-08-30"
assert model["source"]["status"] == "Действует"
assert model["source"]["appendix_status"] == "INFORMATIVE"
assert len(model["section_map"]) == 6
assert {x["locator"] for x in model["section_map"]} == set(fixtures["required_locators"])
assert {x["id"] for x in model["assessment_routes"]} == set(fixtures["required_routes"])
assert {x["id"] for x in model["examples"]} == set(fixtures["required_examples"])
assert len(model["assessment_routes"]) == 2
assert len(model["examples"]) == 3
assert len(model["assessment_routes"][1]["likelihood_factors"]) == 4
assert len(model["evidence_artifacts"]) == 13
assert len(model["evidence_nodes"]) == 18
assert len(model["control_rules"]) == 64
assert len(fixtures["cases"]) == 64
assert len(observation["claims"]) == 18
assert len({x["id"] for x in model["control_rules"]}) == 64
assert len({x["id"] for x in fixtures["cases"]}) == 64
assert {x["rule_id"] for x in fixtures["cases"]} == {x["id"] for x in model["control_rules"]}
assert all(v is True for v in model["boundaries"].values())
assert model["counts"]["default_scales"] == 0
assert model["counts"]["default_formulas"] == 0
assert model["counts"]["default_acceptance_thresholds"] == 0
assert model["counts"]["numeric_reassessment_intervals"] == 0
assert model["counts"]["automatic_table_corrections"] == 0
e2 = next(x for x in model["examples"] if x["id"] == "EXAMPLE_2")
assert e2["example_formula"] == "b_times_c" and e2["default_formula"] is False
e3 = next(x for x in model["examples"] if x["id"] == "EXAMPLE_3")
assert e3["subsequent_sample_values_explicitly_random"] is True
anomaly = next(x for x in model["rendered_anomalies"] if x["id"] == "APPENDIX_E_TABLE_E1B_TERMINAL_CELL")
assert anomaly["disposition"] == "PENDING_PRIMARY_BYTES_NO_CORRECTION"
assert anomaly["inferred_replacement"] is None
for required in [
    "id: GOST_R_ISO_IEC_27005_2010",
    "status_observed: Действует",
    "REGRESSION_PROTECTED_PROCESS_CORE_AND_APPENDIX_E_EXAMPLES",
    "security-knowledge/risks/gost-r-iso-iec-27005-2010-appendix-e-v1.yaml",
    "security-knowledge/risks/gost-r-iso-iec-27005-2010-appendix-e-regression-v1.json",
]:
    assert required in registry
print("PASS: GOST R ISO/IEC 27005-2010 Appendix E; 6 section records, 2 routes, 3 informative examples, 4 likelihood factors, 13 evidence artifacts, 18 evidence nodes, 64 rules/cases; 0 default scales/formulas/thresholds/intervals/corrections")
