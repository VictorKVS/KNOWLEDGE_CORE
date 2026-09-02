#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "threats/fstec-2026-public-extract-numeric-research-gates-v1.yaml"
REG = ROOT / "threats/fstec-2026-public-extract-numeric-research-gates-regression-v1.json"
EVIDENCE = ROOT / "evidence/fstec-2026-public-extract-numeric-research-gates-observation-2026-09-02.yaml"
MASTER = ROOT / "corpus/master-source-inventory.yaml"
SCORE = ROOT / "coverage/coverage-scorecard-2026-09-02-run376.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

model, reg, evidence, score = map(load, (MODEL, REG, EVIDENCE, SCORE))
assert model["id"] == "RU-FSTEC-2026-PUBLIC-EXTRACT-NUMERIC-RESEARCH-GATES-V1"
assert model["sources"][1]["sha256"] == "4801f59209772d0e428af25c47aa2e0936726f84a49ed1d1084f99c566b2a9c8"
assert model["sources"][1]["document_marking"] == "EXTRACT"
assert model["extraction_provenance"]["ocr_model_sha256"] == "e16e5e036cce1d9ec2b00063cf8b54472625b9e14d893a169e2b0dedeb4df225"
assert model["extract_boundary"]["observed_matrix_levels_in_public_extract"] == [6, 5, 4]
assert model["extract_boundary"]["missing_matrix_levels"] == [3, 2, 1]
assert len(model["numeric_routes"]) == 22
assert len(model["evidence_routes"]) == 4
assert len(model["decision_gates"]) == 8
assert len(model["control_rules"]) == len(reg["cases"]) == 64
assert len(model["red_team_attacks"]) == len(reg["adversarial_cases"]) == 12
assert len(model["evidence_nodes"]) == len(evidence["evidence_nodes"]) == 18
assert len(set(model["control_rules"])) == len(set(reg["cases"])) == 64
assert all(x["expected"] == "BLOCK" for x in model["red_team_attacks"])
routes = {x["id"]: x for x in model["numeric_routes"]}
assert routes["N07"]["operator"] == "<= 10%"
assert routes["N08"]["operator"] == "> 10%"
assert routes["N11"]["operator"] == "<= 5"
assert routes["N12"]["operator"] == "> 5"
assert routes["N16"]["operator"] == "<= 3"
assert routes["N17"]["operator"] == "> 3"
assert routes["N21"]["operator"] == ">= 90% lines OR >= 80% blocks"
assert model["boundaries"]["extract_not_complete_method"]
assert model["boundaries"]["ocr_not_authority"]
assert model["boundaries"]["coverage_not_security_proof"]
assert score["key_domains_percent"]["fstec_threat_method_and_bdu"] == 97
assert score["global_gate"] == "FAIL_SCOPE_INCOMPLETE"
master = MASTER.read_text(encoding="utf-8")
for token in ("FSTEC_2026_PUBLIC_EXTRACT_NUMERIC_RESEARCH_GATES", str(MODEL.relative_to(ROOT.parent)), str(REG.relative_to(ROOT.parent)), str(EVIDENCE.relative_to(ROOT.parent)), str(Path(__file__).relative_to(ROOT.parent))):
    assert token in master, token
print("PASS: FSTEC 2026 public-extract numeric research gates; 64/64; red-team 12/12; evidence 18/18")
