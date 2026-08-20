#!/usr/bin/env python3
"""Byte-exact acquisition for RU Protected Information sector sources.

The official publication endpoint normally returns PDF bytes, but some large
publications are delivered as a ZIP container. Both are valid immutable source
artifacts when the bytes match official API metadata. Semantic/current-version
status is never upgraded by this capture step.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "security-corpora" / "RU" / "protected-information"
SOURCE_DIR = CORPUS / "source"
RAW_DIR = CORPUS / "raw"
MANIFEST_DIR = CORPUS / "manifests"
RUN_FILE = CORPUS / "SECTOR_ACQUISITION_RUN.json"
BASES = ("http://publication.pravo.gov.ru", "https://publication.pravo.gov.ru")
UA = "KNOWLEDGE_CORE-sector-acquirer/1.2 (+https://github.com/VictorKVS/KNOWLEDGE_CORE)"
ID_RE = re.compile(r"^id:\s*([^\s#]+)\s*$", re.M)
EO_RE = re.compile(r'^\s*official_publication_id:\s*["\']?([0-9]{16})["\']?\s*$', re.M)


def fetch_bytes(url: str, timeout: int = 90, attempts: int = 4):
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read(), {k.lower(): v for k, v in r.headers.items()}
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last = exc
            if i + 1 < attempts:
                time.sleep(1.5 * (2 ** i))
    raise RuntimeError(f"GET failed: {url}: {last!r}")


def official_get(path: str, params: dict[str, str]):
    q = urllib.parse.urlencode(params)
    errors = []
    for base in BASES:
        url = f"{base}{path}?{q}"
        try:
            data, headers = fetch_bytes(url)
            return data, headers, url
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("; ".join(errors))


def artifact_type(data: bytes, headers: dict[str, str]):
    if data.startswith(b"%PDF-"):
        return ".pdf", "application/pdf", "PDF"
    if data.startswith(b"PK\x03\x04"):
        return ".zip", "application/zip", "ZIP"
    ctype = (headers.get("content-type") or "application/octet-stream").split(";", 1)[0].strip()
    raise RuntimeError(f"unsupported official artifact signature; content-type={ctype}; first bytes={data[:16]!r}")


def discover_targets():
    out = []
    for path in sorted(SOURCE_DIR.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        mid, meo = ID_RE.search(text), EO_RE.search(text)
        if mid and meo:
            out.append((mid.group(1), meo.group(1), path))
    return out


def main() -> int:
    started = dt.datetime.now(dt.timezone.utc)
    targets = discover_targets()
    results = []
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    for source_id, eo, source_record in targets:
        row = {"source_id": source_id, "eo_number": eo, "status": "PENDING"}
        try:
            meta_raw, _, meta_url = official_get("/api/Document", {"eoNumber": eo})
            meta = json.loads(meta_raw.decode("utf-8"))
            advertised = meta.get("pdfFileLength")
            data, headers, file_url = official_get("/File/Pdf", {"eoNumber": eo})
            ext, mime, container = artifact_type(data, headers)
            if advertised is not None and int(advertised) != len(data):
                raise RuntimeError(f"byte-length mismatch: api={advertised}, downloaded={len(data)}")

            sha = hashlib.sha256(data).hexdigest()
            out_dir = RAW_DIR / source_id
            out_dir.mkdir(parents=True, exist_ok=True)
            artifact = out_dir / f"{eo}{ext}"
            if artifact.exists():
                old_sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
                if old_sha != sha:
                    raise RuntimeError(f"immutable collision: existing={old_sha}, incoming={sha}")
            else:
                artifact.write_bytes(data)

            retrieved = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
            manifest = {
                "schema_version": "1.1",
                "source_id": source_id,
                "official_publication_id": eo,
                "official_metadata_url": meta_url,
                "official_file_url": file_url,
                "retrieved_at": retrieved,
                "mime": mime,
                "container_format": container,
                "byte_length": len(data),
                "sha256": sha,
                "artifact_ref": str(artifact.relative_to(ROOT)).replace("\\", "/"),
                "source_record_ref": str(source_record.relative_to(ROOT)).replace("\\", "/"),
                "official_api_pdf_file_length": advertised,
                "official_api_pages_count": meta.get("pagesCount"),
                "official_api_publish_date": meta.get("publishDateShort"),
                "official_api_number": meta.get("number"),
                "proof": {
                    "recognized_official_container": True,
                    "byte_length_matches_official_api": advertised is None or int(advertised) == len(data),
                    "sha256_calculated_from_downloaded_bytes": True,
                },
                "semantic_status_unchanged": True,
                "version_chain_status_unchanged": True,
            }
            mpath = MANIFEST_DIR / f"{source_id}.json"
            mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            row.update({"status": "IMMUTABLE_CAPTURED", "mime": mime, "container_format": container,
                        "byte_length": len(data), "sha256": sha, "artifact_ref": manifest["artifact_ref"],
                        "manifest_ref": str(mpath.relative_to(ROOT)).replace("\\", "/")})
        except Exception as exc:
            row.update({"status": "PENDING", "error": str(exc)})
        results.append(row)

    ok = sum(1 for r in results if r["status"] == "IMMUTABLE_CAPTURED")
    total_bytes = sum(int(r.get("byte_length", 0)) for r in results if r["status"] == "IMMUTABLE_CAPTURED")
    run = {
        "schema_version": "1.1",
        "kind": "ru-protected-information-acquisition-run",
        "started_at": started.isoformat().replace("+00:00", "Z"),
        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "targets_with_official_publication_id": len(targets),
        "raw_downloaded_exact": ok,
        "immutable_sha256_verified": ok,
        "pending": len(targets) - ok,
        "bytes_downloaded": total_bytes,
        "download_success_rate": (ok / len(targets)) if targets else 0.0,
        "results": results,
    }
    RUN_FILE.write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: run[k] for k in ("targets_with_official_publication_id", "raw_downloaded_exact", "immutable_sha256_verified", "pending", "bytes_downloaded")}, ensure_ascii=False))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
