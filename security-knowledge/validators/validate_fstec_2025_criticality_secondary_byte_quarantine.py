#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "threats/fstec-2025-criticality-secondary-byte-quarantine-v1.yaml"
REG = ROOT / "threats/fstec-2025-criticality-secondary-byte-quarantine-regression-v1.json"
EVIDENCE = ROOT / "evidence/fstec-2025-criticality-secondary-byte-quarantine-observation-2026-09-02.yaml"
MASTER = ROOT / "corpus/master-source-inventory.yaml"
SCORE = ROOT / "coverage/coverage-scorecard-2026-09-02-run374.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

model, reg, evidence, score = map(load, (MODEL, REG, EVIDENCE, SCORE))
assert model["id"] == "RU-FSTEC-2025-CRITICALITY-SECONDARY-BYTE-QUARANTINE-V1"
assert model["sources"][1]["sha256"] == "3302f8266f61d2911342e412eb15bfbae58db1d6d0445bd2de87ba536f6837ff"
assert model["sources"][1]["equivalence_to_official_bytes"] == "NOT_PROVEN"
assert model["calculation"]["clause_12_formula"] == "V = Icvss * Iinfr * (Iat + Iimp)"
assert [x["condition"] for x in model["thresholds"]] == ["V > 8.0", "5.0 <= V <= 8.0", "2.0 <= V < 5.0", "V < 2.0"]
assert [x["trigger"] for x in model["recommended_remediation_clocks"]] == ["time of the assessment"] * 4
assert len(model["decision_gates"]) == 8
assert len(model["control_rules"]) == len(reg["cases"]) == 64
assert len(model["red_team_attacks"]) == len(reg["adversarial_cases"]) == 12
assert len(model["evidence_nodes"]) == len(evidence["evidence_nodes"]) == 18
assert len(set(model["control_rules"])) == len(set(reg["cases"])) == 64
assert all(x["expected"] == "BLOCK" for x in model["red_team_attacks"])
assert all(not x["tls_verification_disabled"] for x in evidence["acquisition"])
assert model["boundaries"]["secondary_bytes_quarantined"]
assert model["boundaries"]["official_byte_equivalence_not_claimed"]
assert model["boundaries"]["recommended_clocks_not_hard_law"]
assert score["key_domains_percent"]["fstec_threat_method_and_bdu"] == 95
assert score["global_gate"] == "FAIL_SCOPE_INCOMPLETE"
master = MASTER.read_text(encoding="utf-8")
for token in (
    "FSTEC_2025_CRITICALITY_SECONDARY_BYTE_QUARANTINE",
    str(MODEL.relative_to(ROOT.parent)),
    str(REG.relative_to(ROOT.parent)),
    str(EVIDENCE.relative_to(ROOT.parent)),
    str(Path(__file__).relative_to(ROOT.parent)),
):
    assert token in master, token
print("PASS: FSTEC 2025 criticality secondary-byte quarantine; 64/64; red-team 12/12; evidence 18/18")
