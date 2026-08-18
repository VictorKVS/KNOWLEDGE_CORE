from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "security-knowledge" / "evidence" / "primary-artifacts-fsb-gossopka-package-2025.json"

EXPECTED = {
    "539": ("0001202512260014", 139336, 4, "d930504f21e10efc73f670fa7ffa1cb0594f402ec550767ec7ba99e7539a8710"),
    "546": ("0001202512300066", 425775, 8, "30d1128e75ab07cab4b60d050d5ff14f41fc75e09c0dbb086929a5e92f0c0b81"),
    "547": ("0001202512300064", 683814, 12, "43c702947771d36afe5a28e0487fc75d315f713466d66aea71538eee8c49946d"),
    "548": ("0001202512300058", 415149, 8, "61b0d81c56cfa8aa76ac335d98237efd9a4768ae05c0cdf7fe83a2137ca79430"),
    "553": ("0001202512300059", 679704, 12, "3d825579897e4f06021c8cee9e3ff49e323f2ae833cb7658145ec9ddc54eb7ba"),
    "554": ("0001202512300063", 866427, 17, "818c6d2774bdccda0167f81c8c94fae2d4a2939a5a2c1290322c7783fba9e3f9"),
}


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = {x["identity"]["number"]: x for x in manifest["artifacts"]}
    failures: list[str] = []
    if set(records) != set(EXPECTED):
        failures.append("manifest order set mismatch")
    for number, (eo, size, pages, digest) in EXPECTED.items():
        record = records.get(number)
        if record is None:
            continue
        identity = record["identity"]
        artifact = record["artifact"]
        expected_path = f"security-knowledge/evidence/primary-artifacts/2025/fsb-order-{number}-2025-{eo}.pdf"
        manifest_checks = {
            "eo number": identity.get("eo_number") == eo,
            "path": artifact.get("repository_path") == expected_path,
            "byte length": artifact.get("byte_length") == size,
            "page count": artifact.get("pages") == pages,
            "SHA-256": artifact.get("sha256") == digest,
        }
        data = (ROOT / expected_path).read_bytes()
        observed_pages = len(re.findall(rb"/Type\s*/Page(?!s)\b", data))
        byte_checks = {
            "repository byte length": len(data) == size,
            "repository SHA-256": hashlib.sha256(data).hexdigest() == digest,
            "PDF magic": data.startswith(b"%PDF-1.3"),
            "repository page count": observed_pages == pages,
            "not encrypted": b"/Encrypt" not in data,
            "no JavaScript marker": b"/JavaScript" not in data and b"/JS" not in data,
        }
        for label, passed in {**manifest_checks, **byte_checks}.items():
            if not passed:
                failures.append(f"FSB {number}: {label} failed")
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS 6 immutable FSB GosSOPKA artifacts: identity, bytes, hashes, pages and PDF safety markers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
