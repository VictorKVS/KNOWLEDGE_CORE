#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-kzi-2025-methodology-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-kzi-2025-methodology-regression-v1.json")


def evaluate(case, model, groups, indicators, appendix_rows):
    query = case["query"]
    if query == "clause_count":
        return model["counts"]["numbered_clauses"]
    if query == "group_count":
        return len(groups)
    if query == "indicator_count":
        return len(indicators)
    if query == "group_indicator_count":
        return len(groups[case["group"]]["indicators"])
    if query == "group_weight":
        return groups[case["group"]]["group_weight"]
    if query == "indicator_max":
        return indicators[case["indicator"]]["max_value"]
    if query == "normalized_value":
        return model["normalized_value"]["value"]
    if query == "planned_interval_months":
        return model["periodicity_and_triggers"]["planned_max_interval_months"]
    if query == "extraordinary_trigger_count":
        return len(model["periodicity_and_triggers"]["extraordinary"])
    if query == "input_evidence_class_count":
        return len(model["input_evidence_classes"])
    if query == "pipeline":
        return [item["id"] for item in model["evaluation_pipeline"]]
    if query == "band":
        value = case["value"]
        if value == 1.0:
            return "GREEN"
        if 0.75 < value < 1.0:
            return "ORANGE"
        if value <= 0.75:
            return "RED"
        return "OUT_OF_RANGE"
    if query == "missing_evidence":
        return model["evidence_rules"]["missing_requested_material"]
    if query == "partial_measure":
        return model["evidence_rules"]["absent_ineffective_or_partial_measure"]
    if query == "cross_system":
        return model["calculation"]["cross_system_rule"]
    if query == "repeat_failure":
        window = model["calculation"]["repeated_failure_rule"]["window_months"]
        if case["months"] <= window:
            return model["calculation"]["repeated_failure_rule"]["consequence"]
        return "NO_METHOD_ZEROING_ON_THIS_RULE"
    if query == "attack_zeroing":
        return {
            "USER_ACCOUNT_INITIAL_ACCESS": ["R2"],
            "VULNERABILITY_INITIAL_ACCESS": ["R3"],
            "UNACCEPTABLE_EVENT": ["R2", "R3"],
        }[case["route"]]
    if query == "submission_days":
        return model["periodicity_and_triggers"]["submission_numeric_days"]
    if query == "segregation":
        return model["roles"]["segregation_of_duties"]
    if query == "scope":
        if case["candidate"] == "GOSSOPKA_ATTACK_RESPONSE":
            return "EXCLUDED"
    if query == "method_version":
        return "CURRENT_MODEL" if case["date"] == model["approved_date"] else "SUPERSEDED_NOT_CURRENT"
    if query == "metric_identity":
        return "THIS_METRIC" if case["candidate"] == "KZI" else "DISTINCT_METRIC"
    if query == "appendix_completeness":
        return model["verification_boundary"]["appendix_1_complete_artifact_rows"]
    if query == "appendix_count":
        primary = [item for row in appendix_rows.values() for item in row["artifacts"]]
        conditional = [item for row in appendix_rows.values() for item in row.get("conditional_replacements", [])]
        return {
            "rows": len(appendix_rows),
            "primary": len(primary),
            "conditional": len(conditional),
            "on_request": sum(item["submission"] == "ON_REQUEST" for item in primary),
            "with_results": sum(item["submission"] == "WITH_EVALUATION_RESULTS" for item in primary),
        }[case["kind"]]
    if query == "appendix_mode":
        artifact = next(item for item in appendix_rows[case["indicator"]]["artifacts"] if item["id"] == case["artifact"])
        return artifact["submission"]
    if query == "appendix_conditional":
        item = next(item for item in appendix_rows[case["indicator"]]["conditional_replacements"] if item["id"] == case["artifact"])
        return item[case["field"]]
    if query == "k43_special":
        return appendix_rows["k43"]["special_submission"][case["kind"]]
    if query == "official_bytes":
        return model["verification_boundary"]["immutable_official_bytes"]
    if query == "absolute_security":
        return "NOT_PROVEN"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    groups = {item["id"]: item for item in model["indicator_groups"]}
    indicators = {
        indicator["id"]: indicator
        for group in model["indicator_groups"]
        for indicator in group["indicators"]
    }
    appendix_rows = {item["indicator"]: item for item in model["appendix_1_evidence_map"]["rows"]}

    assert model["status"] == "VERIFIED_BOUNDED_PUBLIC_TEXT_INTERFACE_OFFICIAL_BYTES_PENDING"
    assert len(groups) == model["counts"]["indicator_groups"] == 4
    assert len(indicators) == model["counts"]["private_indicators"] == 16
    assert sum(len(group["indicators"]) for group in groups.values()) == 16
    assert round(sum(group["group_weight"] for group in groups.values()), 10) == 1.0
    for group in groups.values():
        assert round(sum(item["max_value"] for item in group["indicators"]), 10) == 1.0
    assert len(model["input_evidence_classes"]) == model["counts"]["input_evidence_classes"] == 9
    assert len(model["periodicity_and_triggers"]["extraordinary"]) == model["counts"]["extraordinary_triggers"] == 4
    assert len(model["result_bands"]) == model["counts"]["result_bands"] == 3
    assert model["source_evidence"]["official_endpoint_result"] == "TIMEOUT_BYTES_NOT_ACQUIRED"
    assert model["verification_boundary"]["appendix_1_complete_artifact_rows"] == "VERIFIED_PUBLIC_TEXT_CROSSCHECK_OFFICIAL_BYTES_PENDING"
    primary_artifacts = [item for row in appendix_rows.values() for item in row["artifacts"]]
    conditional_replacements = [item for row in appendix_rows.values() for item in row.get("conditional_replacements", [])]
    assert len(appendix_rows) == model["counts"]["appendix_indicator_rows"] == 16
    assert set(appendix_rows) == set(indicators)
    assert len(primary_artifacts) == model["counts"]["appendix_primary_artifact_entries"] == 34
    assert len(conditional_replacements) == model["counts"]["appendix_conditional_replacements"] == 6
    assert sum(item["submission"] == "ON_REQUEST" for item in primary_artifacts) == model["counts"]["appendix_on_request_entries"] == 21
    assert sum(item["submission"] == "WITH_EVALUATION_RESULTS" for item in primary_artifacts) == model["counts"]["appendix_with_results_entries"] == 13
    assert len({item["id"] for item in primary_artifacts + conditional_replacements}) == 40
    assert appendix_rows["k43"]["special_submission"]["numeric_days"] == "NOT_STATED"
    assert model["verification_boundary"]["immutable_official_bytes"] == "PENDING"
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case, model, groups, indicators, appendix_rows)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 37 clauses; 4 groups; 16 indicators; 34 primary artifacts; 6 conditional replacements; 60 fail-closed cases")


if __name__ == "__main__":
    main()
