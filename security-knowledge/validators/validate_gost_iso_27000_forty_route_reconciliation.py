#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "standards/gost-iso-27000-forty-route-reconciliation-v1.yaml"
REG = ROOT / "standards/gost-iso-27000-forty-route-reconciliation-regression-v1.json"
EVIDENCE = ROOT / "evidence/gost-iso-27000-forty-route-reconciliation-observation-2026-09-02.yaml"
MASTER = ROOT / "corpus/master-source-inventory.yaml"
SCORE = ROOT / "coverage/coverage-scorecard-2026-09-02-run370.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

model, reg, evidence, score = map(load, (MODEL, REG, EVIDENCE, SCORE))
records = model["route_records"]
assert model["id"] == "GOST-ISO-27000-FORTY-ROUTE-RECONCILIATION-V1"
assert len(records) == len({x["designation"] for x in records}) == 40
assert sum(x["jurisdiction"] == "RU_NATIONAL" for x in records) == 30
assert sum(x["jurisdiction"] == "INTERNATIONAL_ONLY" for x in records) == 10
assert sum(x["conformity"] == "IDT" for x in records) == 28
assert sum(x["conformity"] == "NEQ" for x in records) == 2
assert sum(x["lifecycle_alignment"] == "SOURCE_MATCHES_CURRENT_BASE" for x in records) == 17
assert sum(x["lifecycle_alignment"] == "SOURCE_REPLACED_OR_SUCCESSOR_EXISTS" for x in records) == 12
assert sum(x["lifecycle_alignment"] == "AMENDMENT_NOT_CAPTURED_IN_NATIONAL_ROUTE" for x in records) == 1
assert all(x["immutable_normative_bytes"] == "PENDING" for x in records)

aggregate = []
for path in dict.fromkeys(x["source_file"] for x in records):
    source = load(ROOT.parent / path)
    aggregate.extend(source.get("standards") or source.get("routes") or [])
assert {x["designation"] for x in aggregate} == {x["designation"] for x in records}
assert len(model["source_models"]) == 8
assert len(model["decision_gates"]) == len(model["scenarios"]) == 8
assert len(model["control_rules"]) == len(reg["cases"]) == 64
assert len(model["red_team_attacks"]) == len(reg["adversarial_cases"]) == 12
assert len(model["evidence_nodes"]) == len(evidence["evidence_nodes"]) == 18
assert evidence["immutable_bytes"]["state"] == "PENDING"
assert score["key_domains_percent"]["gost_gost_r_iso"] == 97
assert score["global_gate"] == "FAIL_SCOPE_INCOMPLETE"
master = MASTER.read_text(encoding="utf-8")
for token in (
    "GOST_ISO_27000_FORTY_ROUTE_RECONCILIATION",
    str(MODEL.relative_to(ROOT.parent)),
    str(REG.relative_to(ROOT.parent)),
    str(EVIDENCE.relative_to(ROOT.parent)),
    str(Path(__file__).relative_to(ROOT.parent)),
):
    assert token in master, token
print("PASS: 40 unique routes; 30 RU (28 IDT, 2 NEQ) + 10 international-only; 64/64; red-team 12/12; evidence 18/18")

