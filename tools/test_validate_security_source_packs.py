from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_security_source_packs import validate_pack


class SecuritySourcePackValidatorTests(unittest.TestCase):
    def write_pack(self, text: str) -> Path:
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        path = Path(tempdir.name) / "test-source-pack.yaml"
        path.write_text(text, encoding="utf-8")
        return path

    def test_verified_source_accepts_official_consolidated_text(self) -> None:
        path = self.write_pack(
            """
pack_id: TEST
sources:
  - source_id: RU_FZ_TEST
    verification_status: STATUS_VERIFIED
    official_text:
      edition_as_of: 2025-09-01
      url: https://ips.pravo.gov.ru/api/ips/legislation/document?hash=test
atomic_facts:
  - fact_id: FACT_1
    source_id: RU_FZ_TEST
    locator: Article 22, part 1
    statement: bounded statement
    verification_status: VERIFIED
"""
        )
        self.assertEqual(validate_pack(path), [])

    def test_verified_official_text_rejects_non_official_host(self) -> None:
        path = self.write_pack(
            """
pack_id: TEST
sources:
  - source_id: RU_FZ_TEST
    verification_status: STATUS_VERIFIED
    official_text:
      edition_as_of: 2025-09-01
      url: https://example.com/current-law
atomic_facts: []
"""
        )
        errors = validate_pack(path)
        self.assertTrue(any("ips.pravo.gov.ru" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
