from __future__ import annotations

import tempfile
import unittest

from father.factory.runtime.approval import ApprovalGate
from father.factory.runtime.models import ApprovalRecord, DecisionRequest, Materiality
from father.factory.runtime.panel import DecisionPanel
from father.factory.runtime.registry import ModelRegistry, ModelSpec
from father.factory.runtime.routing import MaterialityRouter
from father.factory.runtime.store import RuntimeStore


class RoutingTests(unittest.TestCase):
    def test_routing_profiles(self):
        router = MaterialityRouter()
        self.assertEqual(router.route(Materiality()).profile, router.ROUTINE)
        self.assertEqual(router.route(Materiality(architecture_decision=True)).profile, router.ARCHITECTURE)
        self.assertEqual(router.route(Materiality(security_impact="CRITICAL")).profile, router.HIGH_RISK)


class RegistryTests(unittest.TestCase):
    def test_sensitive_data_excludes_public_only_model(self):
        registry = ModelRegistry([
            ModelSpec("remote", "fixture", "x", {"CHAMPION"}, {"*"}, {"PUBLIC"}),
            ModelSpec("local", "fixture", "x", {"CHAMPION"}, {"*"}, {"PUBLIC", "SENSITIVE"}),
        ])
        self.assertEqual(registry.select_one("CHAMPION", "x", "SENSITIVE").model_id, "local")


class PanelTests(unittest.TestCase):
    def _registry(self, invented_ref: bool = False) -> ModelRegistry:
        champion_ref = "EV-X" if invented_ref else "EV-1"
        models = [
            ModelSpec("champion", "fixture", "c", {"CHAMPION"}, {"*"}, {"PUBLIC"}, options={"response": {
                "proposedDecision": "A", "rationale": "r", "evidenceRefs": [champion_ref], "assumptions": [], "unknowns": [], "tradeoffs": [], "failureModes": []
            }}),
            ModelSpec("ch1", "fixture", "x", {"CHALLENGER"}, {"*"}, {"PUBLIC"}, options={"response": {"challengedClaims": [], "alternativeOptions": [], "counterEvidenceRefs": ["EV-1"], "hiddenAssumptions": [], "unresolvedUnknowns": [], "severity": "LOW"}}),
            ModelSpec("ch2", "fixture", "x", {"CHALLENGER"}, {"*"}, {"PUBLIC"}, options={"response": {"challengedClaims": [], "alternativeOptions": [], "counterEvidenceRefs": ["EV-2"], "hiddenAssumptions": [], "unresolvedUnknowns": [], "severity": "LOW"}}),
            ModelSpec("ch3", "fixture", "x", {"CHALLENGER"}, {"*"}, {"PUBLIC"}, options={"response": {"challengedClaims": [], "alternativeOptions": [], "counterEvidenceRefs": ["EV-1"], "hiddenAssumptions": [], "unresolvedUnknowns": [], "severity": "LOW"}}),
            ModelSpec("ch4", "fixture", "x", {"CHALLENGER"}, {"*"}, {"PUBLIC"}, options={"response": {"challengedClaims": [], "alternativeOptions": [], "counterEvidenceRefs": ["EV-2"], "hiddenAssumptions": [], "unresolvedUnknowns": [], "severity": "LOW"}}),
            ModelSpec("judge", "fixture", "j", {"JUDGE"}, {"*"}, {"PUBLIC"}, options={"response": {
                "consensusState": "CONSENSUS_WITH_STRONG_EVIDENCE", "strongestSupportedOption": "A", "dissentRegister": [], "insufficientEvidenceItems": [], "additionalEvidenceRequired": [], "suggestedGateOutcome": "PASS", "decisionConfidenceBand": "HIGH_EVIDENCE_SUPPORT", "unknowns": []
            }}),
        ]
        return ModelRegistry(models)

    def _request(self) -> DecisionRequest:
        return DecisionRequest(
            prompt="choose",
            capability="architecture_review",
            lifecycle_stage="ARCHITECTURE_DECISION",
            evidence_refs=["EV-1", "EV-2"],
            materiality=Materiality(architecture_decision=True),
        )

    def test_architecture_panel(self):
        with tempfile.TemporaryDirectory() as td:
            packet = DecisionPanel(self._registry(), RuntimeStore(td)).run(self._request())
            self.assertEqual(packet.profile, MaterialityRouter.ARCHITECTURE)
            self.assertEqual(len(packet.challengers), 4)
            self.assertIsNotNone(packet.judge)
            self.assertNotEqual(packet.champion.model_id, packet.judge.model_id)
            self.assertEqual(packet.suggested_gate_outcome, "PASS")

    def test_invented_evidence_ref_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            packet = DecisionPanel(self._registry(invented_ref=True), RuntimeStore(td)).run(self._request())
            self.assertFalse(packet.evidence_verification["pass"])
            self.assertEqual(packet.suggested_gate_outcome, "BLOCKED")

    def test_authorized_human_gate(self):
        with tempfile.TemporaryDirectory() as td:
            store = RuntimeStore(td)
            packet = DecisionPanel(self._registry(), store).run(self._request())
            good = ApprovalRecord(
                panel_run_id=packet.panel_run_id,
                task_id=packet.task_id,
                actor_id="u1",
                actor_role="business_or_system_decision_owner",
                decision="APPROVE",
                rationale="evidence reviewed",
            )
            self.assertEqual(ApprovalGate(store).record(packet, good), "PASS")
            bad = ApprovalRecord(
                panel_run_id=packet.panel_run_id,
                task_id=packet.task_id,
                actor_id="u2",
                actor_role="random_role",
                decision="APPROVE",
                rationale="no",
            )
            with self.assertRaises(PermissionError):
                ApprovalGate(store).record(packet, bad)


if __name__ == "__main__":
    unittest.main()
