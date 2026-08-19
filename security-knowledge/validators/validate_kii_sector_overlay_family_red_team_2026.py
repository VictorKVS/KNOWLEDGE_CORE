from __future__ import annotations

import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / "security-knowledge"

ITEMS = [
    {
        "id": "PP_RF_4_2026", "number": "4", "eo": "0001202601160013",
        "matrix": "classification/pp-rf-4-2026-atomic-energy-kii-overlay-v1.json",
        "manifest": "evidence/primary-artifact-pp-rf-4-2026.json",
        "artifact": "evidence/primary-artifacts/2026/pp-rf-4-2026-0001202601160013.pdf",
        "sha": "65815147d515721d4fadaa251fb33f61c3259a1c4feed562afb50c0f1b087df4", "bytes": 2895018, "pages": 12,
    },
    {
        "id": "PP_RF_92_2026", "number": "92", "eo": "0001202602070010",
        "matrix": "classification/pp-rf-92-2026-financial-market-kii-overlay-v1.json",
        "manifest": "evidence/primary-artifact-pp-rf-92-2026.json",
        "artifact": "evidence/primary-artifacts/2026/pp-rf-92-2026-0001202602070010.pdf",
        "sha": "83e32867b115a18a720a316905b001eed3a2211d1e68183ad57ce21fb4968b38", "bytes": 4272251, "pages": 17,
    },
    {
        "id": "PP_RF_246_2026", "number": "246", "eo": "0001202603070013",
        "matrix": "classification/pp-rf-246-2026-science-kii-overlay-v1.json",
        "manifest": "evidence/primary-artifact-pp-rf-246-2026.json",
        "artifact": "evidence/primary-artifacts/2026/pp-rf-246-2026-0001202603070013.pdf",
        "sha": "07047bc77584b469d0be258540b10565f12e8d8c3d54ba387ecdc4a397073aef", "bytes": 2509532, "pages": 10,
    },
    {
        "id": "PP_RF_303_2026", "number": "303", "eo": "0001202603240036",
        "matrix": "classification/pp-rf-303-2026-egrn-kii-overlay-v1.yaml",
        "manifest": "evidence/primary-artifact-pp-rf-303-2026.yaml",
        "artifact": "evidence/primary-artifacts/2026/pp-rf-303-2026-0001202603240036.pdf",
        "sha": "e93e8a0cba5bc7817c53b2f6a233ed2283e1cf9e1ee2a01e30281a4dced91079", "bytes": 1351967, "pages": 6,
    },
    {
        "id": "PP_RF_356_2026", "number": "356", "eo": "0001202604010039",
        "matrix": "classification/pp-rf-356-2026-rocket-space-kii-overlay-v1.json",
        "manifest": "evidence/primary-artifact-pp-rf-356-2026.json",
        "artifact": "evidence/primary-artifacts/2026/pp-rf-356-2026-0001202604010039.pdf",
        "sha": "830efe29784ac04b57b9d6f56ab2d3c9a7cf4c75c2ddc6f18ba9efbbd8d9df1b", "bytes": 1686133, "pages": 8,
    },
    {
        "id": "PP_RF_402_2026", "number": "402", "eo": "0001202604130022",
        "matrix": "classification/pp-rf-402-2026-communications-kii-overlay-v1.json",
        "manifest": "evidence/primary-artifact-pp-rf-402-2026.json",
        "artifact": "evidence/primary-artifacts/2026/pp-rf-402-2026-0001202604130022.pdf",
        "sha": "f666ccb125601dcf0b413ff7aed8f04dba1a74cd0f14655c98fb4f4277c345fc", "bytes": 2443943, "pages": 10,
    },
    {
        "id": "PP_RF_796_2026", "number": "796", "eo": "0001202606290031",
        "matrix": "classification/pp-rf-796-2026-defence-industry-kii-overlay-v1.json",
        "manifest": "evidence/primary-artifact-pp-rf-796-2026.json",
        "artifact": "evidence/primary-artifacts/2026/pp-rf-796-2026-0001202606290031.pdf",
        "sha": "6237b4167295d12b35115f65690e449528a06b0be6c9deac747a1395c23e74c4", "bytes": 3722073, "pages": 16,
    },
]

EXPECTED_EOS = [item["eo"] for item in ITEMS]
CORRUPT_PP303_SHA = "fe8a967507c783328c19edd6517d0afc22f36906ce3556434d138e5d27cad320"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def yaml_scalar(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*[\"']?([^\"'\n]+)", text)
    return match.group(1).strip() if match else None


def pdf_assertions(data: bytes, spec: dict) -> list[str]:
    errors: list[str] = []
    if not data.startswith(b"%PDF-1.5"):
        errors.append("PDF magic/version")
    if len(data) != spec["bytes"]:
        errors.append("byte length")
    if sha256(data) != spec["sha"]:
        errors.append("SHA-256")
    if sha256(data) == CORRUPT_PP303_SHA:
        errors.append("known corrupt PP 303 payload")
    if len(re.findall(rb"/Type\s*/Page\b", data)) != spec["pages"]:
        errors.append("page-object count")
    if re.search(rb"/Encrypt\b", data):
        errors.append("encryption")
    if re.search(rb"/JavaScript\b|/JS\s*(?:\d+\s+\d+\s+R|\()", data):
        errors.append("JavaScript")
    return errors


def main() -> int:
    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    for spec in ITEMS:
        matrix_path = SK / spec["matrix"]
        manifest_path = SK / spec["manifest"]
        artifact_path = SK / spec["artifact"]
        data = artifact_path.read_bytes()
        check(not pdf_assertions(data, spec), f"{spec['id']} artifact mismatch: {', '.join(pdf_assertions(data, spec))}")

        if matrix_path.suffix == ".json":
            matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
            source = matrix.get("source", {})
            check(matrix.get("status") == "VERIFIED_PRIMARY_IMMUTABLE", f"{spec['id']} matrix status")
            check(matrix.get("act", {}).get("official_publication_number") == spec["eo"], f"{spec['id']} matrix eoNumber")
            check(source.get("sha256") == spec["sha"], f"{spec['id']} matrix SHA")
            check(source.get("byte_length") == spec["bytes"], f"{spec['id']} matrix bytes")
            check(source.get("pdf_pages") == spec["pages"], f"{spec['id']} matrix pages")
        else:
            matrix_text = matrix_path.read_text(encoding="utf-8")
            check(yaml_scalar(matrix_text, "status") == "VERIFIED_PRIMARY_IMMUTABLE", f"{spec['id']} matrix status")
            check(yaml_scalar(matrix_text, "official_publication_number") == spec["eo"], f"{spec['id']} matrix eoNumber")
            check(yaml_scalar(matrix_text, "sha256") == spec["sha"], f"{spec['id']} matrix SHA")
            check(yaml_scalar(matrix_text, "byte_length") == str(spec["bytes"]), f"{spec['id']} matrix bytes")

        if manifest_path.suffix == ".json":
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            artifact = manifest.get("artifact", {})
            check(manifest.get("status") == "VERIFIED_PRIMARY_IMMUTABLE", f"{spec['id']} manifest status")
            check(manifest.get("official_publication_number") == spec["eo"], f"{spec['id']} manifest eoNumber")
            check(artifact.get("sha256") == spec["sha"], f"{spec['id']} manifest SHA")
            check(artifact.get("byte_length") == spec["bytes"], f"{spec['id']} manifest bytes")
            check(artifact.get("pages") == spec["pages"], f"{spec['id']} manifest pages")
        else:
            manifest_text = manifest_path.read_text(encoding="utf-8")
            check(yaml_scalar(manifest_text, "status") == "PRIMARY_IMMUTABLE", f"{spec['id']} manifest status")
            check(yaml_scalar(manifest_text, "eo_number") == spec["eo"], f"{spec['id']} manifest eoNumber")
            check(yaml_scalar(manifest_text, "sha256") == spec["sha"], f"{spec['id']} manifest SHA")
            check(yaml_scalar(manifest_text, "byte_length_observed") == str(spec["bytes"]), f"{spec['id']} manifest bytes")
            check(yaml_scalar(manifest_text, "pages_observed") == str(spec["pages"]), f"{spec['id']} manifest pages")
            check(yaml_scalar(manifest_text, "github_blob_sha") == "fecc55fafc13bf38d0efcdd61a5601828c71a8c0", "PP 303 repaired Git blob SHA")
            check("previous_byte_length: 786444" not in manifest_text, "repair block structure drift")
            check("truncated 786444-byte PDF" in manifest_text, "PP 303 repair evidence missing")

        tampered = data[:-1] + bytes([data[-1] ^ 1])
        check(bool(pdf_assertions(tampered, spec)), f"{spec['id']} tamper mutation was not rejected")

    family = json.loads((SK / "classification/kii-sector-overlay-family-scope-2026-v1.json").read_text(encoding="utf-8"))
    members = family.get("members", [])
    check([row.get("act_id") for row in members] == [item["id"] for item in ITEMS], "family member order/set")
    check([row.get("publication_number") for row in members] == EXPECTED_EOS, "family publication order/set")
    check(len(set(EXPECTED_EOS)) == len(members) == 7, "family duplicate or missing member")
    definition = family.get("family_definition", {})
    check(definition.get("exhaustiveness_state") == "VERIFIED_OFFICIAL_PUBLICATION_SET_AS_OF_DATE", "family scope over/understatement")
    check(definition.get("red_team_state") == "PASS_FOR_DECLARED_OFFICIAL_PUBLICATION_SCOPE", "family red-team state")
    states = {row["act_id"]: row.get("lifecycle_state") for row in members}
    check(states.get("PP_RF_402_2026") == "ADOPTED_NOT_IN_FORCE", "PP 402 temporal state")
    pp402 = next(row for row in members if row["act_id"] == "PP_RF_402_2026")
    check(pp402.get("effective_from") == "2026-09-01" and pp402.get("effective_until_exclusive") == "2032-09-01", "PP 402 temporal boundaries")
    check([row.get("act_id") for row in members[:-1]] != [item["id"] for item in ITEMS], "missing-member mutation was not rejected")

    catalog = json.loads((SK / "evidence/official-catalog-kii-sector-overlay-replay-2026-08-19.json").read_text(encoding="utf-8"))
    catalog_eos = [row.get("publication_number") for row in catalog.get("official_publication_set", [])]
    check(catalog_eos == EXPECTED_EOS, "catalogue/member divergence")
    for replay in catalog.get("replays", []):
        packed = replay.get("preserved_gzip", {})
        packed_data = (ROOT / packed["path"]).read_bytes()
        check(len(packed_data) == packed.get("byte_length"), f"{replay['id']} gzip bytes")
        check(sha256(packed_data) == packed.get("sha256"), f"{replay['id']} gzip SHA")
        raw = gzip.decompress(packed_data)
        raw_meta = replay.get("raw_response", {})
        check(len(raw) == raw_meta.get("byte_length"), f"{replay['id']} raw bytes")
        check(sha256(raw) == raw_meta.get("sha256"), f"{replay['id']} raw SHA")
        html = raw.decode("utf-8")
        eos = re.findall(r'Номер опубликования:\s*</span><span class="info-data">(\d{16})', html)
        if replay["id"] == "TRANSPORT_EXACT_TITLE_NEGATIVE":
            check(eos == [] and "Документы не найдены" in html, "transport catalogue negative replay")
        else:
            check(sorted(eos) == sorted(EXPECTED_EOS), f"{replay['id']} result set")
            check(re.search(r"Показаны на странице:\s*с 1\s*по 7\s*из 7", html) is not None, f"{replay['id']} total count")

    transport = json.loads((SK / "classification/transport-kii-sector-overlay-status-2026-08-19-v1.json").read_text(encoding="utf-8"))
    legal = transport.get("legal_state", {})
    operation = transport.get("operational_rule", {})
    check(transport.get("status") == "PENDING_PRIMARY_PUBLICATION", "transport pending state")
    check(legal == {"adoption_state":"NOT_PROVEN","publication_state":"NO_MATCH_FOUND_AS_OF_DATE","effective_state":"NOT_ESTABLISHED","dependency_closure":"OPEN"}, "transport legal state")
    check(operation.get("mode") == "FAIL_CLOSED", "transport fail-closed mode")
    check("PROJECT_EQUALS_ADOPTED_ACT" in operation.get("forbidden_inferences", []), "transport project/adoption guard")
    transport_edges = [edge for edge in family.get("dependency_edges", []) if edge.get("positions") == ["3"]]
    check(len(transport_edges) == 1 and transport_edges[0].get("status") == "PENDING_EXTERNAL_DEPENDENCY_NOT_OFFICIALLY_PUBLISHED", "transport edge status")

    audit = json.loads((SK / "audits/kii-sector-overlay-family-red-team-2026-08-19-v1.json").read_text(encoding="utf-8"))
    check(audit.get("scope_decision") == "PASSED", "bounded red-team decision")
    check(audit.get("findings_by_severity_after_remediation") == {"critical":0,"high":0,"medium":0,"low":0}, "bounded residual findings")
    global_decision = audit.get("global_decision", {})
    check(global_decision.get("status") == "FAILED" and global_decision.get("high_gaps") == 1, "global gap was improperly closed")
    check(global_decision.get("high_gap_ids") == ["HIGH-IMMUTABLE-PROVENANCE"], "global High identity drift")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS KII sector-overlay family red-team: 7 official publications, 7 exact immutable PDFs, repaired PP 303, bounded transport dependency; global High remains open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
