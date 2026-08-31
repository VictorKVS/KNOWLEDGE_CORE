#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/threats/fstec-2021-appendix8-11-scenario-chain-red-team-v1.yaml"
FIXTURES=ROOT/"security-knowledge/threats/fstec-2021-appendix8-11-scenario-chain-red-team-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/fstec-2021-appendix8-11-scenario-chain-red-team-observation-2026-08-31.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
DEPS=[
 ROOT/"security-knowledge/threats/fstec-2021-adversary-method-scenario-relevance-v1.yaml",
 ROOT/"security-knowledge/threats/fstec-2021-appendix8-adversary-capability-levels-v1.yaml",
 ROOT/"security-knowledge/threats/fstec-2021-appendix11-tactics-technique-identifiers-v1.yaml",
 ROOT/"security-knowledge/threats/fstec-2021-appendix11-t1-t3-semantic-atoms-v1.yaml",
 ROOT/"security-knowledge/threats/fstec-2021-appendix11-t4-t7-semantic-atoms-v1.yaml",
 ROOT/"security-knowledge/threats/fstec-2021-appendix11-t8-t10-semantic-atoms-v1.yaml"]
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); deps=[json.loads(x.read_text(encoding="utf-8")) for x in DEPS]; inventory=INVENTORY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["depends_on"]==[x["id"] for x in deps] and len(model["depends_on"])==6
assert [x["order"] for x in model["chain_stages"]]==list(range(1,9))
assert [x["id"] for x in model["chain_stages"]]==["SOURCE_CANDIDATE","ACTUAL_VIOLATOR_CAPABILITY","POSSIBLE_THREAT_TUPLE","METHOD_ACTUALITY","TECHNIQUE_CANDIDATES","EVIDENCE_SUPPORTED_SEQUENCE","SCENARIO_SUPPORTED","RELEVANCE_DECISION"]
assert len(model["transition_policy"]["states"])==5
assert len(model["red_team_attacks"])==12 and all(x["blocked"] for x in model["red_team_attacks"])
assert len({x["blocked_at"] for x in model["red_team_attacks"]})>=7
assert len(model["adversarial_fixtures"])==12 and all(x["expected"] and x["forbidden"] for x in model["adversarial_fixtures"])
assert len(model["evidence_artifacts"])==18 and len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items(): assert model["counts"][key]==value
identifier_model=deps[2]; assert sum(len(x["technique_ids"]) for x in identifier_model["tactics"])==145
for required in ["THREAT_MODELING_AND_THREAT_CATALOGS","attack_scenarios","fstec-2021-appendix8-11-scenario-chain-red-team-v1.yaml","fstec-2021-appendix8-11-scenario-chain-red-team-regression-v1.json"]: assert required in inventory
print("PASS: FSTEC appendix 8/11 to section 5.3 chain red-team; 8 stages, 7 evidence-bearing transitions, 12/12 attacks and 12/12 adversarial fixtures blocked, 64 rules/cases, 18 evidence nodes")
