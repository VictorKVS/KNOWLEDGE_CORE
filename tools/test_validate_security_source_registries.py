from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from validate_security_source_registries import load_inventory, validate_registry


class SecuritySourceRegistryValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.inventory = self.root / "master-source-inventory.yaml"
        self.inventory.write_text(
            yaml.safe_dump(
                {
                    "status_values": [
                        "NOT_REGISTERED",
                        "REGISTERED",
                        "SOURCE_PENDING",
                        "SOURCE_ACQUIRED",
                        "STATUS_VERIFIED",
                        "VERSIONED",
                        "CHUNKED",
                        "ATOMIZED",
                        "LINKED",
                        "EXPERT_REVIEWED",
                        "COMPLETE",
                    ],
                    "source_families": {
                        "THREAT_MODELING_AND_THREAT_CATALOGS": {
                            "priority": "P0",
                            "status": "REGISTERED",
                        }
                    },
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        self.families, self.statuses = load_inventory(self.inventory)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_registry(self, payload: dict) -> Path:
        path = self.root / "registry.yaml"
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        return path

    def base_registry(self) -> dict:
        return {
            "schema_version": 1,
            "family_id": "THREAT_MODELING_AND_THREAT_CATALOGS",
            "priority": "P0",
            "family_status": "REGISTERED",
            "checked_at": "2026-08-13",
            "status_policy": "Catalog observations do not imply system-specific applicability.",
            "sources": [
                {
                    "id": "FSTEK_BDU_ASUTP",
                    "authority_class": "PRIMARY_REGULATOR_DYNAMIC_CATALOG",
                    "source_url": "https://bduasutp.fstec.ru/threats",
                    "ingestion_status": "SOURCE_ACQUIRED_DYNAMIC",
                    "snapshot_required": True,
                }
            ],
            "verified_observations": [
                {
                    "id": "UTP_01",
                    "source_url": "https://bduasutp.fstec.ru/threats/example",
                    "verification_status": "VERIFIED_CATALOG_RECORD",
                    "observed_at": "2026-08-13",
                }
            ],
            "red_team_blocks": ["Dynamic records require timestamped observations."],
        }

    def test_accepts_inventory_aligned_timestamped_dynamic_registry(self) -> None:
        errors = validate_registry(self.write_registry(self.base_registry()), self.families, self.statuses)
        self.assertEqual([], errors)

    def test_rejects_inventory_status_drift(self) -> None:
        payload = self.base_registry()
        payload["family_status"] = "SOURCE_ACQUIRED"
        errors = validate_registry(self.write_registry(payload), self.families, self.statuses)
        self.assertTrue(any("does not match inventory status" in error for error in errors))

    def test_rejects_wrong_official_host(self) -> None:
        payload = self.base_registry()
        payload["sources"] = [
            {
                "id": "STANDARD",
                "authority_class": "OFFICIAL_STANDARD_REGISTRY",
                "source_url": "https://example.com/not-authoritative",
                "ingestion_status": "STATUS_VERIFIED_METADATA_ONLY",
                "status_observed": "active",
            }
        ]
        payload.pop("verified_observations")
        errors = validate_registry(self.write_registry(payload), self.families, self.statuses)
        self.assertTrue(any("OFFICIAL_STANDARD_REGISTRY source_url" in error for error in errors))

    def test_rejects_untimestamped_dynamic_verified_observation(self) -> None:
        payload = self.base_registry()
        payload["verified_observations"][0].pop("observed_at")
        errors = validate_registry(self.write_registry(payload), self.families, self.statuses)
        self.assertTrue(any("dynamic verified observation requires observed_at" in error for error in errors))

    def test_rejects_missing_red_team_limitations(self) -> None:
        payload = self.base_registry()
        payload["red_team_blocks"] = []
        errors = validate_registry(self.write_registry(payload), self.families, self.statuses)
        self.assertTrue(any("red_team_blocks" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
