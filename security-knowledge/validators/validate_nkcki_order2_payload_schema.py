import hashlib
import json
from pathlib import Path

import yaml


SCHEMA = Path("security-knowledge/evidence/nkcki-order-2-2026-payload-schema-v1.yaml")
METHOD = Path("security-knowledge/threat-modeling/nkcki-attack-type-initial-data-2026-taxonomy-v1.yaml")
FIXTURES = Path("security-knowledge/evidence/nkcki-order-2-2026-payload-schema-regression-v1.json")
PUBLICATION_STATUS = Path("security-knowledge/evidence/nkcki-automated-interaction-protocol-publication-status-2026-08-19.yaml")


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def field_map(schema):
    rows = schema["shared_fields"] + schema["attack_specific_fields"] + schema["incident_specific_fields"]
    return {row["id"]: row for row in rows}


def evaluate(case, schema, method, publication_status):
    query = case["query"]
    fields = field_map(schema)
    if query == "expanded_field_count":
        specific = schema["attack_specific_fields"] if case["report_type"] == "ATTACK" else schema["incident_specific_fields"]
        return len(schema["shared_fields"]) + len(specific)
    if query == "reference_value_allowed":
        ref = fields[case["field"]]["reference_values"]
        return case["value"] in schema["reference_values"][ref]
    if query == "pdn_conditional_fields":
        if not case["pdn_leak"]:
            return "PASS"
        required = set(next(r for r in schema["cross_field_rules"] if r["id"] == "PDN-CONDITIONAL-001")["require"])
        return "PASS" if required <= set(case["provided"]) else "BLOCK_MISSING_CONDITIONAL_FIELDS"
    if query == "indicator_overflow":
        if case["count"] <= 30:
            return "INLINE_ALLOWED"
        if case.get("attachment") == "indicators.txt" and case.get("one_per_line") and not case.get("separators"):
            return "ATTACHMENT_ALLOWED"
        return "BLOCK_MISSING_INDICATORS_TXT"
    if query == "threshold_authority":
        return "DO_NOT_TREAT_AS_BINDING" if case["threshold_status"] == "EXAMPLE_NON_NORMATIVE" else "REQUIRES_REVIEW"
    if query == "deadline_effect":
        return "KEEP_FSB547_DEADLINE" if schema["workflow_bindings"]["fsb_order_547"]["payload_schema_does_not_modify_deadlines"] else "BLOCK"
    if query == "reserve_channel_schema":
        return "USE_SAME_SCHEMA" if schema["workflow_bindings"]["fsb_order_548"]["reserve_channel_retains_schema"] else "BLOCK"
    if query == "delivery_identifier":
        return "DELIVERY_NOT_COMPLETENESS" if case["identifier_assigned"] and not case["field_validation_passed"] else "REQUIRES_REVIEW"
    if query == "effective_date":
        return "DO_NOT_INVENT_EFFECTIVE_DATE" if schema["authority_and_time"]["explicit_effective_date_in_artifact"] == "NOT_STATED" else "USE_EXPLICIT_DATE"
    if query == "applicant_requiredness":
        return fields["applicant"]["requiredness"]
    if query == "automated_transport_key":
        return "PENDING_DO_NOT_INFER_FROM_LABEL" if schema["extraction"]["machine_serialization_status"].startswith("PENDING") else "VALIDATE_PROTOCOL"
    if query == "partial_method_evidence":
        return "SEND_AVAILABLE_MATERIALS" if case["available"] > 0 and case["missing"] > 0 else "REQUIRES_REVIEW"
    if query == "public_connection_page_authority":
        if case["connection_steps_published"] and not case["protocol_artifact_located"]:
            return "BLOCK_AS_TRANSPORT_SCHEMA"
        return "REQUIRES_PROTOCOL_VALIDATION"
    if query == "vendor_serialization_claim":
        if case["vendor_says_xml"] and not case["authoritative_protocol_bound"]:
            return "BLOCK_UNAUTHORITATIVE_VENDOR_MAPPING"
        return "REQUIRES_REVIEW"
    if query == "authenticated_instruction_status":
        if case["request_route_known"] and not case["artifact_acquired"]:
            return "PENDING_AUTHORIZED_ACQUISITION"
        return "REQUIRES_REVIEW"
    if query == "printed_schema_without_protocol":
        if case["order2_hash_bound"] and not case["protocol_acquired"]:
            return "ALLOW_PRINTED_TABLE_VALIDATION_ONLY"
        return "REQUIRES_REVIEW"
    raise AssertionError(f"Unhandled query: {query}")


def structural_checks(schema, method, publication_status):
    assert len(schema["shared_fields"]) == 35
    assert len(schema["attack_specific_fields"]) == 3
    assert len(schema["incident_specific_fields"]) == 18
    assert len(schema["shared_fields"]) + len(schema["attack_specific_fields"]) == 38
    assert len(schema["shared_fields"]) + len(schema["incident_specific_fields"]) == 53
    fields = field_map(schema)
    assert len(fields) == 56, "All repository field IDs must be unique"
    for row in fields.values():
        assert row.get("exact_name_ru")
        assert row.get("requiredness") in schema["requiredness_codes"]
    assert len(schema["reference_values"]["attack_types"]) == 7
    assert len(schema["reference_values"]["incident_types"]) == 10
    assert len(schema["reference_values"]["sector_values"]) == 18
    assert len(schema["reference_values"]["categorization_values"]) == 5
    assert schema["authority_and_time"]["explicit_effective_date_in_artifact"] == "NOT_STATED"
    assert schema["extraction"]["machine_serialization_status"].startswith("PENDING")

    assert len(method["taxonomy"]) == 7
    source_names = set(schema["reference_values"]["attack_types"])
    method_names = {row["exact_name_ru"] for row in method["taxonomy"]}
    assert source_names == method_names
    for row in method["taxonomy"]:
        assert row["classification_logic"]["operator"] in {"ALL", "ANY"}
        assert row["evidence_point_5"]
        for example in row["classification_logic"].get("examples", []):
            assert example["status"] == "EXAMPLE_NON_NORMATIVE"
        for exclusion in row["exclusions"]:
            if isinstance(exclusion, dict):
                assert exclusion["status"] == "EXAMPLE_NON_NORMATIVE"

    order_pdf = Path(schema["source"]["repository_artifact"])
    method_pdf = Path(method["source"]["repository_artifact"])
    assert sha256(order_pdf) == schema["source"]["sha256"]
    assert sha256(method_pdf) == method["source"]["sha256"]
    assert publication_status["status"] == "AUTHORITATIVE_PUBLIC_DISCOVERY_COMPLETE_PROTOCOL_NOT_LOCATED_PUBLICLY"
    assert len(publication_status["official_public_surfaces_checked"]) == 4
    assert all(not row["protocol_artifact_link_observed"] for row in publication_status["official_public_surfaces_checked"])
    assert publication_status["machine_behavior"]["automated_transport_serialization"].startswith("PENDING")
    assert publication_status["machine_behavior"]["guessed_json_xml_keys"] == "BLOCK"
    assert publication_status["red_team"]["critical_gap_created"] is False
    assert publication_status["red_team"]["high_gap_created"] is False


def main():
    schema = load_yaml(SCHEMA)
    method = load_yaml(METHOD)
    publication_status = load_yaml(PUBLICATION_STATUS)
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    structural_checks(schema, method, publication_status)
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case, schema, method, publication_status)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 38 attack fields; 53 incident fields; 7 method types; " f"{len(fixtures['cases'])} regression cases; public protocol boundary fail-closed")


if __name__ == "__main__":
    main()
