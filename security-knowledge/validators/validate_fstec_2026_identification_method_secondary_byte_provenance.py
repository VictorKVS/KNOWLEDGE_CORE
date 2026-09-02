#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "threats/fstec-2026-identification-method-secondary-byte-provenance-v1.yaml"
REG = ROOT / "threats/fstec-2026-identification-method-secondary-byte-provenance-regression-v1.json"
EVIDENCE = ROOT / "evidence/fstec-2026-identification-method-secondary-byte-provenance-observation-2026-09-02.yaml"
MASTER = ROOT / "corpus/master-source-inventory.yaml"
SCORE = ROOT / "coverage/coverage-scorecard-2026-09-02-run375.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

model, reg, evidence, score = map(load, (MODEL, REG, EVIDENCE, SCORE))
assert model["id"] == "RU-FSTEC-2026-IDENTIFICATION-METHOD-SECONDARY-BYTE-PROVENANCE-V1"
assert model["sources"][1]["sha256"] == "4801f59209772d0e428af25c47aa2e0936726f84a49ed1d1084f99c566b2a9c8"
assert model["sources"][1]["size_bytes"] == 601884
assert model["sources"][1]["pages"] == 60
assert model["sources"][1]["equivalence_to_official_bytes"] == "NOT_PROVEN"
assert model["sources"][3]["actual_document"].startswith("GOST R 56939-2024")
assert model["sources"][3]["state"] == "REJECTED_NOT_THE_FSTEC_2026_METHOD"
assert [x["clause"] for x in model["secondary_clause_crosschecks"]] == ["1.2", "1.3", "1.5", "2.2"]
assert len(model["decision_gates"]) == len(model["scenarios"]) == 8
assert len(model["control_rules"]) == len(reg["cases"]) == 64
assert len(model["red_team_attacks"]) == len(reg["adversarial_cases"]) == 12
assert len(model["evidence_nodes"]) == len(evidence["evidence_nodes"]) == 18
assert len(set(model["control_rules"])) == len(set(reg["cases"])) == 64
assert all(x["expected"] == "BLOCK" for x in model["red_team_attacks"])
assert all(not x["tls_verification_disabled"] for x in evidence["acquisition"])
assert sum(x["bytes_accepted"] for x in evidence["acquisition"]) == 1
assert model["boundaries"]["secondary_bytes_quarantined"]
assert model["boundaries"]["official_byte_equivalence_not_claimed"]
assert model["boundaries"]["wrong_document_rejected"]
assert model["boundaries"]["bdu_endpoint_not_export_evidence"]
assert score["key_domains_percent"]["fstec_threat_method_and_bdu"] == 96
assert score["global_gate"] == "FAIL_SCOPE_INCOMPLETE"
master = MASTER.read_text(encoding="utf-8")
for token in (
    "FSTEC_2026_IDENTIFICATION_METHOD_SECONDARY_BYTE_PROVENANCE",
    str(MODEL.relative_to(ROOT.parent)),
    str(REG.relative_to(ROOT.parent)),
    str(EVIDENCE.relative_to(ROOT.parent)),
    str(Path(__file__).relative_to(ROOT.parent)),
):
    assert token in master, token
print("PASS: FSTEC 2026 identification-method secondary-byte provenance; 64/64; red-team 12/12; evidence 18/18")
