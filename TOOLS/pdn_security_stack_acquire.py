#!/usr/bin/env python3
"""Reuse-first immutable acquisition for the RU PDN technical/crypto security stack.

The stream is intentionally isolated from the general PDN-core acquirer so technical,
crypto and bounded public-sector overlays can be measured without corrupting core
counters. Successful acquisition proves official bytes only; semantic promotion is a
separate compiler/review gate.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import mimetypes
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDN = ROOT / "security-corpora" / "RU" / "152-FZ"
STACK = PDN / "security-stack"
SOURCE_DIR = STACK / "source"
RAW_DIR = STACK / "raw"
MANIFEST_DIR = STACK / "manifests"
INVENTORY = STACK / "PDN_SECURITY_STACK_SOURCE_INVENTORY.yaml"
RUN_FILE = STACK / "PDN_SECURITY_STACK_ACQUISITION_RUN.json"
STREAM_STATUS = STACK / "STREAM2_STATUS_2026-08-22.yaml"
MASTER = PDN / "PDN_MASTER_SOURCE_INVENTORY.yaml"
BASES = ("http://publication.pravo.gov.ru", "https://publication.pravo.gov.ru")
UA = "KNOWLEDGE_CORE-pdn-security-stack-acquirer/1.1 (+https://github.com/VictorKVS/KNOWLEDGE_CORE)"

ID_RE = re.compile(r"^id:\s*([^\s#]+)\s*$", re.M)
STATUS_RE = re.compile(r"^status:\s*([^\s#]+)\s*$", re.M)
TOP_LEVEL_RE = re.compile(r"(?m)^[A-Za-z_][A-Za-z0-9_-]*:\s*(?:.*)?$")
PUB_RE = re.compile(r'^  official_publication_id:\s*["\']?([0-9]{16})["\']?\s*$', re.M)
NUMBER_RE = re.compile(r'^  number:\s*["\']?([^"\'\n]+)["\']?\s*$', re.M)
URL_RE = re.compile(r'^  url:\s*["\']([^"\']+)["\']\s*$', re.M)
FALLBACK_URL_RE = re.compile(r'^  fallback_url:\s*["\']([^"\']+)["\']\s*$', re.M)
EXPECTED_MIME_RE = re.compile(r'^  expected_mime:\s*["\']?([^"\'\n]+)["\']?\s*$', re.M)
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def section(text: str, name: str) -> str:
    m = re.search(rf"(?m)^{re.escape(name)}:\s*$", text)
    if not m:
        return ""
    tail = text[m.end():]
    nxt = TOP_LEVEL_RE.search(tail)
    return text[m.end(): m.end() + nxt.start()] if nxt else text[m.end():]


def fetch_bytes(url: str, timeout: int = 75, attempts: int = 3):
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read(), {k.lower(): v for k, v in r.headers.items()}, r.geturl()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last = exc
            if i + 1 < attempts:
                time.sleep(1.5 * (2 ** i))
    raise RuntimeError(f"GET failed: {url}: {last!r}")


def official_get(path: str, eo: str):
    q = urllib.parse.urlencode({"eoNumber": eo})
    errors = []
    for base in BASES:
        url = f"{base}{path}?{q}"
        try:
            return fetch_bytes(url)
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("; ".join(errors))


def extension(mime: str, data: bytes, expected_mime: str = "") -> str:
    if data.startswith(b"%PDF-") or mime == "application/pdf" or expected_mime == "application/pdf":
        return ".pdf"
    if expected_mime == DOCX_MIME and data.startswith(b"PK\x03\x04"):
        return ".docx"
    if "html" in mime or data.lstrip().lower().startswith((b"<!doctype html", b"<html")):
        return ".html"
    if "json" in mime:
        return ".json"
    if mime.startswith("text/"):
        return ".txt"
    return mimetypes.guess_extension(mime) or ".bin"


def validate_expected(data: bytes, mime: str, expected_mime: str) -> None:
    if not expected_mime:
        return
    if expected_mime == "application/pdf" and not data.startswith(b"%PDF-"):
        raise RuntimeError(f"expected official PDF but got mime={mime}")
    if expected_mime == DOCX_MIME and not data.startswith(b"PK\x03\x04"):
        raise RuntimeError(f"expected official DOCX/OOXML but got mime={mime}")


def write_immutable(source_id: str, stem: str, data: bytes, ext: str):
    sha = hashlib.sha256(data).hexdigest()
    out = RAW_DIR / source_id / f"{stem}-{sha[:16]}{ext}"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and hashlib.sha256(out.read_bytes()).hexdigest() != sha:
        raise RuntimeError("immutable collision")
    if not out.exists():
        out.write_bytes(data)
    return out, sha


def discover_targets():
    out = []
    for path in sorted(SOURCE_DIR.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        mid, mst = ID_RE.search(text), STATUS_RE.search(text)
        if not mid or not mst or mst.group(1) != "METADATA_VERIFIED":
            continue
        doc = section(text, "document")
        canon = section(text, "canonical_source")
        pub, num, url = PUB_RE.search(doc), NUMBER_RE.search(doc), URL_RE.search(canon)
        fallback_urls = FALLBACK_URL_RE.findall(canon)
        expected_mime = EXPECTED_MIME_RE.search(canon)
        if pub:
            out.append({
                "source_id": mid.group(1), "route": "publication_pdf", "value": pub.group(1),
                "number": num.group(1) if num else "", "path": path,
                "expected_mime": "application/pdf", "fallback_urls": fallback_urls,
            })
        elif url:
            out.append({
                "source_id": mid.group(1), "route": "canonical_snapshot", "value": url.group(1),
                "number": num.group(1) if num else "", "path": path,
                "expected_mime": expected_mime.group(1) if expected_mime else "",
                "fallback_urls": fallback_urls,
            })
    return out


def reusable(source_id: str):
    mp = MANIFEST_DIR / f"{source_id}.json"
    if not mp.exists():
        return None
    try:
        m = json.loads(mp.read_text(encoding="utf-8"))
        artifact = ROOT / str(m["artifact_ref"])
        if m.get("source_id") != source_id or not artifact.is_file():
            return None
        if hashlib.sha256(artifact.read_bytes()).hexdigest() != m.get("sha256"):
            return None
        if not m.get("proof", {}).get("sha256_calculated_from_downloaded_bytes"):
            return None
        return m
    except Exception:
        return None


def _canonical_fetch_with_fallback(target):
    expected = target.get("expected_mime", "")
    errors = []
    candidates = [target["value"], *target.get("fallback_urls", [])]
    for index, candidate in enumerate(candidates):
        try:
            data, headers, final_url = fetch_bytes(candidate)
            if not data:
                raise RuntimeError("empty official response")
            response_mime = (headers.get("content-type") or "application/octet-stream").split(";", 1)[0].strip().lower()
            validate_expected(data, response_mime, expected)
            mime = expected if expected and response_mime in {"application/octet-stream", "binary/octet-stream"} else response_mime
            return data, mime, final_url, index > 0, errors
        except Exception as exc:
            errors.append(f"{candidate}: {exc}")
    raise RuntimeError("; ".join(errors))


def capture(target):
    sid, route, value = target["source_id"], target["route"], target["value"]
    retrieved = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    if route == "publication_pdf":
        meta_raw, _, meta_url = official_get("/api/Document", value)
        meta = json.loads(meta_raw.decode("utf-8"))
        pdf, headers, pdf_url = official_get("/File/Pdf", value)
        if not pdf.startswith(b"%PDF-"):
            raise RuntimeError("official publication response is not a PDF")
        advertised = meta.get("pdfFileLength")
        if advertised is not None and int(advertised) != len(pdf):
            raise RuntimeError(f"official byte length mismatch: {advertised} != {len(pdf)}")
        artifact, sha = write_immutable(sid, value, pdf, ".pdf")
        mime = (headers.get("content-type") or "application/pdf").split(";", 1)[0].strip()
        if mime == "application/octet-stream":
            mime = "application/pdf"
        return {
            "schema_version": "1.1", "source_id": sid, "capture_kind": route,
            "official_publication_id": value, "official_metadata_url": meta_url,
            "source_url": pdf_url, "retrieved_at": retrieved, "mime": mime,
            "byte_length": len(pdf), "sha256": sha,
            "artifact_ref": str(artifact.relative_to(ROOT)).replace("\\", "/"),
            "source_record_ref": str(target["path"].relative_to(ROOT)).replace("\\", "/"),
            "proof": {"official_route": True, "pdf_signature_ok": True,
                      "byte_length_matches_official_api": advertised is None or int(advertised) == len(pdf),
                      "sha256_calculated_from_downloaded_bytes": True},
            "semantic_status_unchanged": True,
        }
    data, mime, final_url, fallback_used, failed_primary_attempts = _canonical_fetch_with_fallback(target)
    expected = target.get("expected_mime", "")
    ext = extension(mime, data, expected)
    artifact, sha = write_immutable(sid, "official-snapshot", data, ext)
    return {
        "schema_version": "1.1", "source_id": sid, "capture_kind": route,
        "configured_primary_url": value, "source_url": final_url,
        "fallback_used": fallback_used, "failed_primary_attempts": failed_primary_attempts,
        "retrieved_at": retrieved, "mime": mime, "byte_length": len(data), "sha256": sha,
        "artifact_ref": str(artifact.relative_to(ROOT)).replace("\\", "/"),
        "source_record_ref": str(target["path"].relative_to(ROOT)).replace("\\", "/"),
        "proof": {"official_route": True, "byte_exact_download": True,
                  "expected_pdf_signature_ok": expected != "application/pdf" or data.startswith(b"%PDF-"),
                  "expected_docx_signature_ok": expected != DOCX_MIME or data.startswith(b"PK\x03\x04"),
                  "sha256_calculated_from_downloaded_bytes": True},
        "semantic_status_unchanged": True,
    }


def sync_source(manifest):
    path = ROOT / manifest["source_record_ref"]
    text = path.read_text(encoding="utf-8")
    mp = MANIFEST_DIR / f"{manifest['source_id']}.json"
    block = (
        "capture:\n"
        f"  raw_artifact_ref: {json.dumps(manifest['artifact_ref'], ensure_ascii=False)}\n"
        f"  manifest_ref: {json.dumps(str(mp.relative_to(ROOT)).replace(chr(92), '/'), ensure_ascii=False)}\n"
        f"  capture_kind: {json.dumps(manifest['capture_kind'])}\n"
        f"  source_url: {json.dumps(manifest['source_url'], ensure_ascii=False)}\n"
        f"  retrieved_at: {json.dumps(manifest['retrieved_at'])}\n"
        f"  mime: {json.dumps(manifest['mime'])}\n"
        f"  byte_length: {manifest['byte_length']}\n"
        f"  sha256: {json.dumps(manifest['sha256'])}\n"
        "  fingerprint_status: IMMUTABLE_CAPTURED\n"
        "  semantic_status: UNCHANGED\n"
        "  note: \"Exact bytes from the registered official route captured; extraction/semantic status is not promoted.\"\n"
    )
    updated, n = re.subn(r"(?ms)^capture:\n.*?(?=^[A-Za-z_][A-Za-z0-9_]*:|\Z)", block + "\n", text, count=1)
    if n != 1:
        raise RuntimeError(f"capture block missing: {path}")
    path.write_text(updated, encoding="utf-8")


def update_inventory(captured_ids, total_sources, run):
    text = INVENTORY.read_text(encoding="utf-8")
    sources_text = section(text, "sources")
    source_ids = re.findall(r"(?m)^  - id:\s*([^\s#]+)$", sources_text)
    for sid in source_ids:
        value = "IMMUTABLE_CAPTURED" if sid in captured_ids else "PENDING"
        text = re.sub(rf"(?ms)(^  - id: {re.escape(sid)}\n.*?^    raw_capture:)\s*[^\n]+", rf"\1 {value}", text, count=1)
    values = {
        "identified": total_sources,
        "metadata_verified": total_sources,
        "raw_downloaded_exact": len(captured_ids),
        "immutable_sha256_verified": len(captured_ids),
        "pending_raw_capture": total_sources - len(captured_ids),
        "exact_official_route_unresolved": len(run["unrouted_source_ids"]),
    }
    for key, val in values.items():
        text = re.sub(rf"(?m)^(  {key}:)\s*[^\n]+$", rf"\1 {val}", text, count=1)
    if "latest_acquisition_run:" in text:
        text = re.sub(r"(?ms)^latest_acquisition_run:\n.*?(?=^next_gate:)", "", text, count=1)
    marker = "\nnext_gate:\n"
    summary = (
        "\nlatest_acquisition_run:\n"
        f"  finished_at: {json.dumps(run['finished_at'])}\n"
        f"  targets_total: {run['targets_total']}\n"
        f"  reused_immutable: {run['reused_immutable']}\n"
        f"  network_targets_attempted: {run['network_targets_attempted']}\n"
        f"  new_immutable_captured: {run['new_immutable_captured']}\n"
        f"  pending_after_run: {run['pending_after_run']}\n"
    )
    text = text.replace(marker, summary + marker, 1)
    INVENTORY.write_text(text, encoding="utf-8")


def update_stream_status(captured, total, run):
    if not STREAM_STATUS.exists():
        return
    text = STREAM_STATUS.read_text(encoding="utf-8")
    values = {
        "sources_identified": total,
        "sources_metadata_verified": total,
        "exact_official_route_unresolved": len(run["unrouted_source_ids"]),
        "raw_downloaded_exact": captured,
        "immutable_sha256_verified": captured,
        "pending_raw_capture": total - captured,
    }
    for key, val in values.items():
        text = re.sub(rf"(?m)^(  {key}:)\s*[^\n]+$", rf"\1 {val}", text, count=1)
    state = "IMMUTABLE_CAPTURE_COMPLETE" if captured == total else "PARTIAL_IMMUTABLE_CAPTURED"
    text = re.sub(r"(?m)^(  status:)\s*[^\n]+$", rf"\1 {state}", text, count=1)
    text = re.sub(r"(?m)^(  accepted_run_record:)\s*[^\n]+$", r'\1 "PDN_SECURITY_STACK_ACQUISITION_RUN.json"', text, count=1)
    STREAM_STATUS.write_text(text, encoding="utf-8")


def update_master(captured, total, run):
    text = MASTER.read_text(encoding="utf-8")
    block = (
        "security_stack:\n"
        "  linked_inventory: \"security-stack/PDN_SECURITY_STACK_SOURCE_INVENTORY.yaml\"\n"
        "  status: ACTIVE_DISCOVERY\n"
        f"  checked_at: \"2026-08-22\"\n"
        f"  identified: {total}\n"
        f"  immutable_sha256_verified: {captured}\n"
        f"  pending_raw_capture: {total - captured}\n"
        "  applicability_rule: \"Neighboring technical, crypto, licensing, certification and GosSOPKA regimes require an explicit applicability edge before reuse in PDN decisions.\"\n"
        f"  latest_acquisition_finished_at: {json.dumps(run['finished_at'])}\n\n"
    )
    if re.search(r"(?m)^security_stack:\s*$", text):
        text, n = re.subn(r"(?ms)^security_stack:\n.*?(?=^[A-Za-z_][A-Za-z0-9_-]*:|\Z)", block, text, count=1)
        if n != 1:
            raise RuntimeError("master security_stack replacement failed")
    else:
        anchor = "production_counters:\n"
        if anchor not in text:
            raise RuntimeError("master production_counters anchor missing")
        text = text.replace(anchor, block + anchor, 1)
    MASTER.write_text(text, encoding="utf-8")


def main():
    started = dt.datetime.now(dt.timezone.utc)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    targets = discover_targets()
    inventory_text = INVENTORY.read_text(encoding="utf-8")
    all_source_ids = set(re.findall(r"(?m)^  - id:\s*([^\s#]+)$", section(inventory_text, "sources")))
    reused, attempted = [], []
    for target in targets:
        old = reusable(target["source_id"])
        if old:
            reused.append(old)
            continue
        row = {"source_id": target["source_id"], "route": target["route"], "status": "PENDING"}
        try:
            m = capture(target)
            (MANIFEST_DIR / f"{target['source_id']}.json").write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            sync_source(m)
            row.update({"status": "IMMUTABLE_CAPTURED", "byte_length": m["byte_length"], "sha256": m["sha256"], "mime": m["mime"], "source_url": m["source_url"], "fallback_used": m.get("fallback_used", False)})
        except Exception as exc:
            row["error"] = str(exc)
        attempted.append(row)
    accepted = []
    for sid in all_source_ids:
        m = reusable(sid)
        if m:
            accepted.append(m)
    finished = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    run = {
        "schema_version": "1.1", "kind": "pdn-security-stack-reuse-first-acquisition-run",
        "started_at": started.isoformat().replace("+00:00", "Z"), "finished_at": finished,
        "sources_registered": len(all_source_ids), "targets_total": len(targets),
        "reused_immutable": len(reused), "network_targets_attempted": len(attempted),
        "new_immutable_captured": sum(r["status"] == "IMMUTABLE_CAPTURED" for r in attempted),
        "immutable_total": len(accepted), "pending_after_run": len(all_source_ids) - len(accepted),
        "results": attempted,
        "unrouted_source_ids": sorted(all_source_ids - {t["source_id"] for t in targets}),
    }
    RUN_FILE.write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    captured_ids = {m["source_id"] for m in accepted}
    update_inventory(captured_ids, len(all_source_ids), run)
    update_stream_status(len(accepted), len(all_source_ids), run)
    update_master(len(accepted), len(all_source_ids), run)
    print(json.dumps({k: run[k] for k in ("sources_registered", "targets_total", "reused_immutable", "network_targets_attempted", "new_immutable_captured", "immutable_total", "pending_after_run", "unrouted_source_ids")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
