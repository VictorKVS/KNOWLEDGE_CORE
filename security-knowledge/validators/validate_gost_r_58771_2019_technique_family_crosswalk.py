#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "security-knowledge/risks/gost-r-58771-2019-technique-family-crosswalk-v1.yaml"
FIXTURES = ROOT / "security-knowledge/risks/gost-r-58771-2019-technique-family-crosswalk-regression-v1.json"
OBS = ROOT / "security-knowledge/evidence/gost-r-58771-2019-technique-family-crosswalk-observation-2026-08-30.yaml"
REGISTRY = ROOT / "security-knowledge/standards/gost-and-ru-standards-source-registry.yaml"

model = json.loads(MODEL.read_text(encoding="utf-8"))
fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
observation = json.loads(OBS.read_text(encoding="utf-8"))
registry = REGISTRY.read_text(encoding="utf-8")

assert model["id"] == fixtures["model_id"]
assert model["as_of"] == "2026-08-30"
assert model["source"]["status"] == "Действует"
assert model["source"]["replaces"] == "ГОСТ Р ИСО/МЭК 31010-2011"
assert len(model["section_map"]) == 29
assert {x["locator"] for x in model["execution_stages"]} == set(fixtures["required_execution_locators"])
assert {x["locator"] for x in model["technique_families"]} == set(fixtures["required_family_locators"])
assert {x["id"] for x in model["classification_artifacts"]} == set(fixtures["required_classification_artifacts"])
assert len(model["execution_stages"]) == 6
assert len(model["classification_artifacts"]) == 2
assert len(model["technique_families"]) == 9
assert len(model["crosswalk_to_27005"]["mappings"]) == 9
assert model["crosswalk_to_27005"]["status"] == "KB_CROSSWALK_INFERENCE_NOT_NORMATIVE_TEXT"
assert len(model["selection_controls"]) == 6
assert len(model["evidence_artifacts"]) == 14
assert len(model["evidence_nodes"]) == 18
assert len(model["control_rules"]) == 64
assert len(fixtures["cases"]) == 64
assert len(observation["claims"]) == 18
assert len({x["id"] for x in model["control_rules"]}) == 64
assert len({x["id"] for x in fixtures["cases"]}) == 64
assert {x["rule_id"] for x in fixtures["cases"]} == {x["id"] for x in model["control_rules"]}
assert all(v is True for v in model["boundaries"].values())
assert model["counts"]["default_weights"] == 0
assert model["counts"]["default_formulas"] == 0
assert model["counts"]["default_scores"] == 0
assert model["counts"]["default_acceptance_thresholds"] == 0
assert model["counts"]["automatic_technique_selections"] == 0
assert model["counts"]["claimed_individual_technique_count"] == 0
assert all(x["status"] == "INFORMATIVE" for x in model["section_map"] if x["locator"].startswith(("A", "B")))
assert all(x["cell_values"] == "PENDING_PRIMARY_BYTES" for x in model["classification_artifacts"])
for required in [
    "id: GOST_R_58771_2019",
    "status_observed: Действует",
    "FAMILY_CROSSWALK",
    "security-knowledge/risks/gost-r-58771-2019-technique-family-crosswalk-v1.yaml",
    "security-knowledge/risks/gost-r-58771-2019-technique-family-crosswalk-regression-v1.json",
]:
    assert required in registry
print("PASS: GOST R 58771-2019 family crosswalk; 29 section records, 6 stages, 2 classification artifacts, 9 technique families/mappings, 14 evidence artifacts, 18 evidence nodes, 64 rules/cases; 0 defaults/automatic selections/claimed technique count")
