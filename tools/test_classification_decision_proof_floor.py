from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "security-knowledge/classification/classification-decision-proof-floor.yaml"


class ClassificationDecisionProofFloorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load(ARTIFACT.read_text(encoding="utf-8"))

    def test_family_stays_unverified(self):
        self.assertEqual(self.data["family_id"], "CLASSIFICATION_AND_CATEGORIZATION_METHODS")
        self.assertEqual(self.data["status"], "PROOF_FLOOR_DEFINED_NOT_VERIFIED")

    def test_required_provenance_inputs_are_explicit(self):
        inputs = {item["id"]: item for item in self.data["required_inputs"]}
        for required in {"REGIME", "OBJECT_SCOPE", "ORGANIZATION_FACTS", "VERSION_CONTEXT", "RULE_INPUTS"}:
            self.assertIn(required, inputs)
            self.assertTrue(inputs[required]["provenance_required"])

    def test_fail_closed_invariants_exist(self):
        rules = "\n".join(item["if"] + " -> " + item["result"] for item in self.data["fail_closed_rules"])
        self.assertIn("current_version_chain is not VERIFIED -> INSUFFICIENT_EVIDENCE", rules)
        self.assertIn("any consumed input fact lacks provenance -> INSUFFICIENT_EVIDENCE", rules)
        self.assertIn("effective date cannot be established -> INSUFFICIENT_EVIDENCE", rules)

    def test_promotion_requires_reproducible_reviewed_case(self):
        promotion = self.data["promotion_rule"]
        self.assertIn("reproducible case", promotion)
        self.assertIn("independent review", promotion)


if __name__ == "__main__":
    unittest.main()
