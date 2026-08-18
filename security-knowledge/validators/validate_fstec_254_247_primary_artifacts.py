from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "security-knowledge" / "evidence" / "primary-artifacts-fstec-254-247-2025.json"

EXPECTED = {
    "FSTEC-ORDER-254-2025": {
        "eo_number": "0001202508210006",
        "number": "254",
        "effective_date": "2025-09-01",
        "path": "security-knowledge/evidence/primary-artifacts/2025/fstec-order-254-2025-0001202508210006.pdf",
        "bytes": 190225,
        "pages": 4,
        "sha256": "fb19ba9b03601c62f9ab7d7b70337f83cd36cab39876bdf7879fc351d4c99022",
        "magic": b"%PDF-1.3",
    },
    "FSTEC-ORDER-247-2025": {
        "eo_number": "0001202508210016",
        "number": "247",
        "effective_date": "2025-09-01",
        "path": "security-knowledge/evidence/primary-artifacts/2025/fstec-order-247-2025-0001202508210016.pdf",
        "bytes": 166352,
        "pages": 5,
        "sha256": "663ff9e47ac5e05c7fe2f3db2379fba2971cfe8e055c75474bd41a23363db9a3",
        "magic": b"%PDF-1.3",
    },
}


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = {item["source_id"]: item for item in manifest["artifacts"]}
    failures: list[str] = []

    if set(records) != set(EXPECTED):
        fail(f"source ids differ: {sorted(records)}", failures)

    for source_id, expected in EXPECTED.items():
        record = records.get(source_id)
        if record is None:
            continue
        identity = record["identity"]
        artifact = record["artifact"]
        for key in ("eo_number", "number", "effective_date"):
            if identity.get(key) != expected[key]:
                fail(f"{source_id}: identity {key} mismatch", failures)
        if artifact.get("repository_path") != expected["path"]:
            fail(f"{source_id}: repository path mismatch", failures)
        if artifact.get("byte_length_api") != expected["bytes"]:
            fail(f"{source_id}: API byte length mismatch", failures)
        if artifact.get("pages_api") != expected["pages"]:
            fail(f"{source_id}: API page count mismatch", failures)
        if artifact.get("sha256") != expected["sha256"]:
            fail(f"{source_id}: manifest SHA-256 mismatch", failures)

        path = ROOT / expected["path"]
        data = path.read_bytes()
        observed_pages = len(re.findall(rb"/Type\s*/Page(?!s)\b", data))
        checks = {
            "byte length": len(data) == expected["bytes"],
            "SHA-256": hashlib.sha256(data).hexdigest() == expected["sha256"],
            "PDF magic": data.startswith(expected["magic"]),
            "page count": observed_pages == expected["pages"],
            "not encrypted": b"/Encrypt" not in data,
            "no JavaScript marker": b"/JavaScript" not in data and b"/JS" not in data,
        }
        for check, passed in checks.items():
            if not passed:
                fail(f"{source_id}: {check} failed", failures)

    if failures:
        for message in failures:
            print(f"FAIL {message}")
        return 1
    print("PASS 2 immutable FSTEC primary artifacts: identity, bytes, hashes, PDF safety markers and pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
