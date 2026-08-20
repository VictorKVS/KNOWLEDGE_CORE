#!/usr/bin/env python3
"""Byte-exact acquisition for the RU PDN core from official sources.

Two official acquisition routes are supported:
1. publication.pravo.gov.ru publication IDs -> authoritative metadata + PDF;
2. canonical official URLs -> byte-exact official snapshots for consolidated/current texts
   that do not expose a publication-ID PDF route in the source registry.

Every successful capture records URL, retrieval time, MIME, byte length and SHA-256.
The script never upgrades semantic/verification status: raw capture proves only the
bytes obtained from an already METADATA_VERIFIED official source route.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import mimetypes
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "security-corpora" / "RU" / "152-FZ"
SOURCE_DIR = CORPUS / "source"
RAW_DIR = CORPUS / "raw"
MANIFEST_DIR = CORPUS / "manifests"
RUN_FILE = CORPUS / "PDN_ACQUISITION_RUN.json"
BASES = (
    "http://publication.pravo.gov.ru",
    "https://publication.pravo.gov.ru",
)
UA = "KNOWLEDGE_CORE-pdn-acquirer/1.1 (+https://github.com/VictorKVS/KNOWLEDGE_CORE)"

ID_RE = re.compile(r"^id:\s*([^\s#]+)\s*$", re.M)
EO_RE = re.compile(r'^\s*official_publication_id:\s*["\']?([0-9]{16})["\']?\s*$', re.M)
CANONICAL_URL_RE = re.compile(r'(?ms)^canonical_source:\s*\n.*?^\s{2}url:\s*["\']([^"\']+)["\']\s*$')
STATUS_RE = re.compile(r"^status:\s*([^\s#]+)\s*$", re.M)


def fetch_bytes(url: str, timeout: int = 90, attempts: int = 4) -> tuple[bytes, dict[str, str], str]:
    last: Exception | None = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read(), {k.lower(): v for k, v in r.headers.items()}, r.geturl()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last = exc
            if i + 1 < attempts:
                time.sleep(1.5 * (2**i))
    raise RuntimeError(f"GET failed: {url}: {last!r}")


def official_get(path: str, params: dict[str, str]) -> tuple[bytes, dict[str, str], str]:
    q = urllib.parse.urlencode(params)
    errors: list[str] = []
    for base in BASES:
        url = f"{base}{path}?{q}"
        try:
            data, headers, final_url = fetch_bytes(url)
            return data, headers, final_url
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("; ".join(errors))


def extension_for_mime(mime: str, data: bytes) -> str:
    mime = mime.lower()
    if data.startswith(b"%PDF-") or mime == "application/pdf":
        return ".pdf"
    if "json" in mime:
        return ".json"
    if "xml" in mime:
        return ".xml"
    if "html" in mime or data.lstrip().lower().startswith((b"<!doctype html", b"<html")):
        return ".html"
    if mime.startswith("text/"):
        return ".txt"
    guessed = mimetypes.guess_extension(mime) if mime else None
    return guessed or ".bin"


def write_immutable(source_id: str, stem: str, data: bytes, extension: str) -> tuple[Path, str]:
    sha = hashlib.sha256(data).hexdigest()
    out_dir = RAW_DIR / source_id
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = out_dir / f"{stem}-{sha[:16]}{extension}"
    if artifact.exists():
        old_sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if old_sha != sha:
            raise RuntimeError(f"immutable collision: existing={old_sha}, incoming={sha}")
    else:
        artifact.write_bytes(data)
    return artifact, sha


def discover_targets() -> list[dict[str, object]]:
    targets: list[dict[str, object]] = []
    for path in sorted(SOURCE_DIR.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        mid = ID_RE.search(text)
        if not mid:
            continue
        status = STATUS_RE.search(text)
        if not status or status.group(1) != "METADATA_VERIFIED":
            continue
        eo = EO_RE.search(text)
        curl = CANONICAL_URL_RE.search(text)
        if eo:
            targets.append({"source_id": mid.group(1), "route": "publication_pdf", "value": eo.group(1), "path": path})
        elif curl:
            targets.append({"source_id": mid.group(1), "route": "canonical_snapshot", "value": curl.group(1), "path": path})
    return targets


def capture_publication_pdf(source_id: str, eo: str, source_record: Path) -> dict[str, object]:
    meta_raw, _meta_headers, meta_url = official_get("/api/Document", {"eoNumber": eo})
    meta = json.loads(meta_raw.decode("utf-8"))
    advertised = meta.get("pdfFileLength")
    pdf, pdf_headers, pdf_url = official_get("/File/Pdf", {"eoNumber": eo})
    if not pdf.startswith(b"%PDF-"):
        raise RuntimeError(f"not a PDF signature; first bytes={pdf[:16]!r}")
    if advertised is not None and int(advertised) != len(pdf):
        raise RuntimeError(f"byte-length mismatch: api={advertised}, downloaded={len(pdf)}")

    artifact, sha = write_immutable(source_id, eo, pdf, ".pdf")
    retrieved = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    mime = (pdf_headers.get("content-type") or "application/pdf").split(";", 1)[0].strip()
    if mime == "application/octet-stream":
        mime = "application/pdf"
    return {
        "schema_version": "1.1",
        "source_id": source_id,
        "capture_kind": "official_publication_pdf",
        "official_publication_id": eo,
        "official_metadata_url": meta_url,
        "official_file_url": pdf_url,
        "source_url": pdf_url,
        "retrieved_at": retrieved,
        "mime": mime,
        "byte_length": len(pdf),
        "sha256": sha,
        "artifact_ref": str(artifact.relative_to(ROOT)).replace("\\", "/"),
        "source_record_ref": str(source_record.relative_to(ROOT)).replace("\\", "/"),
        "official_api_pdf_file_length": advertised,
        "official_api_pages_count": meta.get("pagesCount"),
        "official_api_publish_date": meta.get("publishDateShort"),
        "official_api_number": meta.get("number"),
        "proof": {
            "official_route": True,
            "byte_exact_download": True,
            "pdf_signature_ok": True,
            "byte_length_matches_official_api": advertised is None or int(advertised) == len(pdf),
            "sha256_calculated_from_downloaded_bytes": True,
        },
        "semantic_status_unchanged": True,
    }


def capture_canonical_snapshot(source_id: str, url: str, source_record: Path) -> dict[str, object]:
    data, headers, final_url = fetch_bytes(url)
    if not data:
        raise RuntimeError("empty canonical-source response")
    mime = (headers.get("content-type") or "application/octet-stream").split(";", 1)[0].strip().lower()
    extension = extension_for_mime(mime, data)
    artifact, sha = write_immutable(source_id, "official-snapshot", data, extension)
    retrieved = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": "1.1",
        "source_id": source_id,
        "capture_kind": "official_canonical_snapshot",
        "official_file_url": final_url,
        "source_url": url,
        "retrieved_at": retrieved,
        "mime": mime,
        "byte_length": len(data),
        "sha256": sha,
        "artifact_ref": str(artifact.relative_to(ROOT)).replace("\\", "/"),
        "source_record_ref": str(source_record.relative_to(ROOT)).replace("\\", "/"),
        "proof": {
            "official_route": True,
            "byte_exact_download": True,
            "sha256_calculated_from_downloaded_bytes": True,
            "publication_api_length_check_not_applicable": True,
        },
        "semantic_status_unchanged": True,
        "review_note": "Snapshot proves the exact bytes returned by the registered official canonical URL at retrieved_at; semantic/version-locator review remains required.",
    }


def main() -> int:
    started = dt.datetime.now(dt.timezone.utc)
    targets = discover_targets()
    results: list[dict[str, object]] = []
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    for target in targets:
        source_id = str(target["source_id"])
        route = str(target["route"])
        value = str(target["value"])
        source_record = Path(target["path"])
        row: dict[str, object] = {"source_id": source_id, "route": route, "status": "PENDING"}
        try:
            if route == "publication_pdf":
                manifest = capture_publication_pdf(source_id, value, source_record)
            else:
                manifest = capture_canonical_snapshot(source_id, value, source_record)
            mpath = MANIFEST_DIR / f"{source_id}.json"
            mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            row.update({
                "status": "IMMUTABLE_CAPTURED",
                "byte_length": manifest["byte_length"],
                "sha256": manifest["sha256"],
                "mime": manifest["mime"],
                "artifact_ref": manifest["artifact_ref"],
                "manifest_ref": str(mpath.relative_to(ROOT)).replace("\\", "/"),
            })
        except Exception as exc:
            row.update({"status": "PENDING", "error": str(exc)})
        results.append(row)

    ok = sum(1 for r in results if r["status"] == "IMMUTABLE_CAPTURED")
    publication_targets = sum(1 for t in targets if t["route"] == "publication_pdf")
    canonical_targets = sum(1 for t in targets if t["route"] == "canonical_snapshot")
    run = {
        "schema_version": "1.1",
        "kind": "pdn-core-acquisition-run",
        "started_at": started.isoformat().replace("+00:00", "Z"),
        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "targets_total": len(targets),
        "targets_with_official_publication_id": publication_targets,
        "targets_with_canonical_official_route": canonical_targets,
        "raw_downloaded_exact": ok,
        "immutable_sha256_verified": ok,
        "pending": len(targets) - ok,
        "results": results,
    }
    RUN_FILE.write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: run[k] for k in ("targets_total", "targets_with_official_publication_id", "targets_with_canonical_official_route", "raw_downloaded_exact", "immutable_sha256_verified", "pending")}, ensure_ascii=False))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
