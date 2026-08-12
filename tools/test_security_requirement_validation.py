from __future__ import annotations

import unittest
from pathlib import Path

from validate_security_requirements import validate_requirement_document


class SecurityRequirementValidationTests(unittest.TestCase):
    def validate(self, requirement: dict, *, document: str = "DOC-TEST") -> list[str]:
        data = {"document": document, "requirements": [requirement]}
        return validate_requirement_document(Path("security-knowledge/test/requirements/core.yaml"), data)

    def test_missing_verification_state_is_conservative_unverified(self):
        errors = self.validate({"id": "REQ-SEED-001", "source_locator": "p. 0"})
        self.assertEqual(errors, [])

    def test_reviewed_requirement_does_not_need_source_quote(self):
        errors = self.validate(
            {
                "id": "REQ-REVIEWED-001",
                "source_locator": "p. 1",
                "verification": "REVIEWED",
            }
        )
        self.assertEqual(errors, [])

    def test_verified_requirement_requires_exact_locator(self):
        errors = self.validate(
            {
                "id": "REQ-VERIFIED-001",
                "source_quote": "Exact source fragment",
                "verification": "VERIFIED",
            }
        )
        self.assertTrue(any("source_locator" in error for error in errors))

    def test_verified_requirement_requires_source_quote(self):
        errors = self.validate(
            {
                "id": "REQ-VERIFIED-002",
                "source_locator": "p. 2",
                "verification": "VERIFIED",
            }
        )
        self.assertTrue(any("source_quote" in error for error in errors))

    def test_verified_requirement_requires_source_document_identity(self):
        data = {
            "requirements": [
                {
                    "id": "REQ-VERIFIED-003",
                    "source_locator": "p. 3",
                    "source_quote": "Exact source fragment",
                    "verification": "VERIFIED",
                }
            ]
        }
        errors = validate_requirement_document(Path("security-knowledge/test/requirements/core.yaml"), data)
        self.assertTrue(any("source document identity" in error for error in errors))

    def test_verified_requirement_with_source_locator_and_quote_passes(self):
        errors = self.validate(
            {
                "id": "REQ-VERIFIED-004",
                "source_locator": "p. 4",
                "source_quote": "Exact source fragment",
                "verification": "VERIFIED",
            }
        )
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
