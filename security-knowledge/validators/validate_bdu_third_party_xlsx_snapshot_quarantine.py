#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "security-knowledge/threats/bdu-third-party-xlsx-snapshot-quarantine-v1.yaml"
FIXTURES = ROOT / "security-knowledge/threats/bdu-third-party-xlsx-snapshot-quarantine-regression-v1.json"
OBS = ROOT / "security-knowledge/evidence/bdu-third-party-xlsx-snapshot-quarantine-observation-2026-09-02.yaml"
INVENTORY = ROOT / "security-knowledge/corpus/master-source-inventory.yaml"

model = json.loads(MODEL.read_text(encoding="utf-8"))
fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
obs = json.loads(OBS.read_text(encoding="utf-8"))
inventory = INVENTORY.read_text(encoding="utf-8")

assert model["id"] == fixtures["model_id"] == obs["model_id"]
assert [x["dataset"] for x in model["snapshots"]] == ["THRLIST", "VULLIST"]
thr, vul = model["snapshots"]
assert thr["source_blob_sha1"] == obs["retrievals"][0]["local_git_hash_object"]
assert vul["source_blob_sha1"] == obs["retrievals"][1]["local_git_hash_object"]
assert thr["worksheet"]["effective_records"] == thr["semantics"]["unique_identifiers"] == 227
assert thr["worksheet"]["physical_rows_after_headers"] == 998
assert thr["worksheet"]["trailing_blank_rows"] == 771
assert sum(thr["semantics"]["statuses"].values()) == 227
assert vul["worksheet"]["effective_records"] == vul["semantics"]["unique_identifiers"] == 62445
assert vul["semantics"]["duplicate_identifier_rows"] == vul["semantics"]["invalid_identifier_rows"] == 0
assert sum(vul["semantics"]["statuses"].values()) == 62445
assert vul["core_metadata"]["modified"][:10] < vul["semantics"]["discovery_date_max"]
assert all(x["container"]["crc_errors"] == 0 for x in model["snapshots"])
assert all(not x["container"]["vba_project"] for x in model["snapshots"])
assert all(x["container"]["external_links"] == x["container"]["formulas"] == 0 for x in model["snapshots"])
assert len(model["provenance_rules"]) == len(model["decision_gates"]) == 8
assert len(model["red_team_attacks"]) == len(fixtures["adversarial_cases"]) == 12
assert len(model["evidence_nodes"]) == len(obs["evidence_nodes"]) == 18
assert len(model["control_rules"]) == len(fixtures["cases"]) == 64
assert len(set(model["control_rules"])) == len(set(fixtures["cases"])) == 64
assert all(model["boundaries"].values())
for key, value in fixtures["expected_counts"].items():
    assert model["counts"][key] == value
for required in ["FSTEK_BDU", "BDU_THIRD_PARTY_XLSX_SNAPSHOT_QUARANTINE", "bdu-third-party-xlsx-snapshot-quarantine-v1.yaml", "validate_bdu_third_party_xlsx_snapshot_quarantine.py"]:
    assert required in inventory
print("PASS: BDU third-party XLSX quarantine; 2 immutable blobs, 62,672 effective records observed; 64/64; red-team 12/12; evidence 18/18")
