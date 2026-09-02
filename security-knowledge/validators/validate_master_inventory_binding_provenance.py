#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/audits/master-inventory-binding-provenance-2026-09-02-v1.yaml"
FIXTURES=ROOT/"security-knowledge/audits/master-inventory-binding-provenance-2026-09-02-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/master-inventory-binding-provenance-observation-2026-09-02.yaml"
MASTER=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
GAPS=ROOT/"security-knowledge/audits/fixed-scope-residual-gap-register-2026-09-02-v1.yaml"
SCORE=ROOT/"security-knowledge/coverage/coverage-scorecard-2026-09-02-run379.json"

def main():
    model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8"))
    master=yaml.safe_load(MASTER.read_text(encoding="utf-8")); gaps=json.loads(GAPS.read_text(encoding="utf-8")); score=json.loads(SCORE.read_text(encoding="utf-8"))
    assert model["id"]==fixtures["model_id"]==obs["model_id"]
    assert len(master["source_families"])==model["counts"]["source_families"]==5
    assert len(master["fixed_scope"])==model["counts"]["fixed_scope_after"]==17
    assert set(master["fixed_scope"])==set(fixtures["expected_fixed_scope_ids"])
    order=master["fixed_scope"]["ORDER_573_630_ASN1_PRIMARY_AND_COMPILER"]
    assert order["status"]=="REGISTERED" and "PENDING" in order["ingestion_status"]
    expected=set(fixtures["expected_gap_family_ids"]); assert expected=={x["id"] for x in gaps["gap_families"]}
    bindings={x["fixed_scope_id"] for x in model["fixed_scope_bindings"]}; assert bindings==set(master["fixed_scope"])
    bound={g for x in model["fixed_scope_bindings"] for g in x["gap_family_ids"]}; assert bound==expected
    assert model["binding_reconciliation"]["unbound_gap_family_ids"]==[] and model["binding_reconciliation"]["unbound_fixed_scope_ids"]==[]
    assert score["inventory"]=={"verified":293,"pending":31}
    assert "source_items" not in master and model["scorecard_count_provenance"]["row_level_recalculation_performed"] is False
    assert len(model["scorecard_count_provenance"]["required_fields"])==8
    assert len(model["evidence_nodes"])==len(obs["claims"])==18 and len(model["red_team_attacks"])==12
    assert len(model["control_rules"])==len(fixtures["cases"])==64
    assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
    for k,v in fixtures["expected_counts"].items(): assert model["counts"][k]==v
    assert all(model["boundaries"].values())
    print("PASS: 5 source families; 17/17 fixed-scope rows and 9/9 gap families bound; M06 registered; 293/31 preserved but not re-derived; 64/64 rules/cases")

if __name__=="__main__": main()
