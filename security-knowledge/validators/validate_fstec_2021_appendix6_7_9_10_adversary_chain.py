#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/threats/fstec-2021-appendix6-7-9-10-adversary-chain-v1.yaml"
FIXTURES=ROOT/"security-knowledge/threats/fstec-2021-appendix6-7-9-10-adversary-chain-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/fstec-2021-appendix6-7-9-10-adversary-chain-observation-2026-09-01.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"

model=json.loads(MODEL.read_text(encoding="utf-8"))
fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
obs=json.loads(OBS.read_text(encoding="utf-8"))
inventory=INVENTORY.read_text(encoding="utf-8")

assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["source"]["approval_date"]=="2021-02-05"
assert model["source"]["saved_visual_copy_sha256"]=="a7ea712a8ec6952750a2cfc733e909ddd1236819a777ddf69dc1159a192d8cdd"
assert model["source"]["saved_visual_copy_role"].startswith("SECONDARY_VISUAL")
violators=model["appendix6"]["violator_types"]
assert len(violators)==13
assert sum(v["category"]=="EXTERNAL" for v in violators)==7
assert sum(v["category"]=="INTERNAL" for v in violators)==6
assert len(model["appendix6"]["collusion_routes"])==3
assert sum(len(x["partners"]) for x in model["appendix6"]["collusion_routes"])==14
assert model["appendix7"]["example_only"] is True
assert len(model["appendix7"]["risk_routes"])==13
assert model["appendix9"]["example_only"] is True
assert len(model["appendix9"]["profile_rows"])==16
assert sum(len(x["categories"]) for x in model["appendix9"]["profile_rows"])==19
assert len(model["appendix9"]["printed_anomalies"])+sum("printed_anomaly" in x for x in model["appendix10"]["scenario_bindings"])==4
assert all(x["status"].startswith("PENDING") for x in model["appendix9"]["printed_anomalies"])
assert model["appendix10"]["example_only"] is True
assert len(model["appendix10"]["scenario_bindings"])==11
assert all(set(model["appendix10"]["tuple_required"])<=set(x) for x in model["appendix10"]["scenario_bindings"])
assert len(model["decision_gates"])==len(model["scenarios"])==8
assert len(model["red_team_attacks"])==12
assert {x["blocked_by"] for x in model["red_team_attacks"]}<={x["id"] for x in model["decision_gates"]}
assert len(model["evidence_artifacts"])==18
assert len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items():
    assert model["counts"][key]==value
for required in ["THREAT_MODELING_AND_THREAT_CATALOGS","fstec-2021-appendix6-7-9-10-adversary-chain-v1.yaml","fstec-2021-appendix6-7-9-10-adversary-chain-regression-v1.json"]:
    assert required in inventory
print("PASS: FSTEC 2021 appendices 6/7/9/10; 13 violator types, 14 collusion edges, 16/19 Appendix 9 rows/bindings, 11 scenario bindings, 64 rules/cases, 12/12 red-team attacks blocked")
