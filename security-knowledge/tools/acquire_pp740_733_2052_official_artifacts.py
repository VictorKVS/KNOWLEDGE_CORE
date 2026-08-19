#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


BASE = "https://publication.pravo.gov.ru"
GOVERNMENT_AUTHORITY_ID = "8005d8c9-4b6d-48d3-861a-2a37e69fccb3"
TARGETS = (
    {
        "logical_id": "RU-GOV-PP-740-2025",
        "number": "740",
        "document_date": "2025-05-28",
        "title_must_contain": "Един",
        "filename": "pp-rf-740-2025-05-28-official.pdf",
    },
    {
        "logical_id": "RU-GOV-PP-733-2021",
        "number": "733",
        "document_date": "2021-05-14",
        "title_must_contain": "един",
        "filename": "pp-rf-733-2021-05-14-official.pdf",
    },
    {
        "logical_id": "RU-GOV-PP-2052-2025",
        "number": "2052",
        "document_date": "2025-12-17",
        "title_must_contain": "733",
        "filename": "pp-rf-2052-2025-12-17-official.pdf",
    },
)


def fetch(url: str, attempts: int = 4) -> tuple[bytes, dict[str, str], str]:
    last_error: Exception | None = None
    context = ssl.create_default_context()
    for attempt in range(1, attempts + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "KNOWLEDGE_CORE provenance acquisition/1.0"},
            )
            with urllib.request.urlopen(request, timeout=45, context=context) as response:
                headers = {key.lower(): value for key, value in response.headers.items()}
                return response.read(), headers, response.geturl()
        except Exception as exc:  # network errors must remain visible after bounded retries
            last_error = exc
            if attempt < attempts:
                time.sleep(attempt * 2)
    raise RuntimeError(f"bounded fetch failed for {url}: {last_error}")


def exact_document(target: dict[str, str]) -> tuple[dict, str]:
    query = urllib.parse.urlencode(
        {
            "Block": "government",
            "SignatoryAuthorityId": GOVERNMENT_AUTHORITY_ID,
            "NumberSearchType": "0",
            "Number": target["number"],
            "DocumentDateFrom": target["document_date"],
            "DocumentDateTo": target["document_date"],
            "PageSize": "30",
            "Index": "1",
        }
    )
    url = f"{BASE}/api/Documents?{query}"
    payload, _, _ = fetch(url)
    data = json.loads(payload.decode("utf-8-sig"))
    matches = []
    for item in data.get("items", []):
        document_date = str(item.get("documentDate", ""))[:10]
        title = item.get("complexName") or item.get("title") or item.get("name") or ""
        if (
            str(item.get("number")) == target["number"]
            and document_date == target["document_date"]
            and item.get("signatoryAuthorityId") == GOVERNMENT_AUTHORITY_ID
            and target["title_must_contain"].casefold() in title.casefold()
        ):
            matches.append(item)
    if len(matches) != 1:
        summaries = [
            {
                "number": item.get("number"),
                "documentDate": item.get("documentDate"),
                "eoNumber": item.get("eoNumber"),
                "title": item.get("complexName") or item.get("title"),
            }
            for item in data.get("items", [])
        ]
        raise RuntimeError(
            f"expected one exact match for {target['logical_id']}, got {len(matches)}; "
            f"API summaries={summaries}"
        )
    return matches[0], url


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    receipt = {
        "schema_version": "1.0",
        "retrieved_at": retrieved_at,
        "source": BASE,
        "transport": "DIRECT_HTTPS_PYTHON_DEFAULT_CA_AND_HOSTNAME_VERIFICATION",
        "artifacts": [],
    }

    for target in TARGETS:
        item, query_url = exact_document(target)
        eo_number = str(item.get("eoNumber", ""))
        if not eo_number.isdigit() or len(eo_number) != 19:
            raise RuntimeError(f"invalid eoNumber for {target['logical_id']}: {eo_number!r}")
        pdf_url = f"{BASE}/File/Pdf?{urllib.parse.urlencode({'eoNumber': eo_number})}"
        payload, headers, effective_url = fetch(pdf_url)
        if not payload.startswith(b"%PDF-"):
            raise RuntimeError(
                f"non-PDF payload for {target['logical_id']}: {payload[:32]!r}"
            )
        expected_bytes = item.get("pdfFileLength")
        if isinstance(expected_bytes, int) and expected_bytes != len(payload):
            raise RuntimeError(
                f"byte length mismatch for {target['logical_id']}: "
                f"API={expected_bytes} downloaded={len(payload)}"
            )
        path = output / target["filename"]
        path.write_bytes(payload)
        record = {
            "logical_id": target["logical_id"],
            "document_number": target["number"],
            "document_date": target["document_date"],
            "eo_number": eo_number,
            "publication_date": str(item.get("publishDateShort", ""))[:10],
            "title": item.get("complexName") or item.get("title") or item.get("name"),
            "api_query_url": query_url,
            "official_document_url": f"{BASE}/document/{eo_number}",
            "official_pdf_url": pdf_url,
            "effective_url": effective_url,
            "content_type": headers.get("content-type"),
            "bytes": len(payload),
            "pages": item.get("pagesCount"),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "artifact_filename": target["filename"],
        }
        receipt["artifacts"].append(record)
        print(json.dumps(record, ensure_ascii=False, sort_keys=True))

    (output / "pp740-733-2052-official-origin-receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
