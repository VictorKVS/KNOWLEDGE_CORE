#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/standards/gost-r-59548-2022-event-registration-core-part1-v1.yaml")
FIXTURES = Path("security-knowledge/standards/gost-r-59548-2022-event-registration-core-part1-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    schemas = {item["id"]: item for item in model["event_type_schemas"]}

    def field(case):
        schema = schemas[case["schema"]]
        candidates = schema["required_fields"] + schema["additional_fields"]
        return next(item for item in candidates if item["id"] == case["field"])

    def evaluate(case):
        query = case["query"]
        if query == "data_type_count":
            return len(model["registered_information_data_types"])
        if query == "common_minimum_count":
            return len(model["common_minimum_information"]["fields"])
        if query == "common_additional_count":
            return len(model["common_additional_information"]["fields"])
        if query == "schema_count":
            return len(schemas)
        if query == "specific_required_count":
            return sum(len(item["required_fields"]) for item in schemas.values())
        if query == "specific_additional_count":
            return sum(len(item["additional_fields"]) for item in schemas.values())
        if query == "subsection_total":
            return model["coverage"]["section_6_2_subsections_total"]
        if query == "subsection_pending":
            return model["coverage"]["section_6_2_subsections_pending"]
        if query == "storage_format":
            return "NOT_ESTABLISHED" if "SECURITY_EVENT_STORAGE_FORMAT" in model["scope"]["does_not_establish"] else None
        if query == "extension_allowed":
            return model["scope"]["extension_rule"] == "REGISTERED_INFORMATION_MAY_BE_EXTENDED_BEYOND_THIS_STANDARD"
        if query == "monitoring_transfer":
            return "provide access" in model["scope"]["monitoring_transfer_rule"]
        if query == "status":
            return model["status_observed"]
        if query == "effective_date":
            return model["effective_date"]
        if query == "order":
            return model["order"]
        if query == "importance_values":
            return next(x for x in model["common_minimum_information"]["fields"] if x["id"] == "IMPORTANCE_LEVEL")["accepted_values"]
        if query == "subject_nullable":
            return next(x for x in model["common_minimum_information"]["fields"] if x["id"] == "ACCESS_SUBJECT")["nullable_when"]
        if query == "sequence_when":
            return next(x for x in model["common_additional_information"]["fields"] if x["id"] == "SEQUENCE_NUMBER")["when"]
        if query == "required_count":
            return len(schemas[case["schema"]]["required_fields"])
        if query == "additional_count":
            return len(schemas[case["schema"]]["additional_fields"])
        if query == "modeled_ids":
            return list(schemas)
        if query == "field_property":
            return field(case)[case["property"]]
        if query == "guard":
            return case["guard"] in model["scope_guards"]
        if query == "official_status_boundary":
            return model["verification_boundary"]["official_status_and_scope"]
        if query == "clause_6_1_boundary":
            return model["verification_boundary"]["clause_6_1"]
        if query == "modeled_clause_boundary":
            return model["verification_boundary"]["clauses_6_2_1_to_6_2_8"]
        if query == "remaining_clause_boundary":
            return model["verification_boundary"]["clauses_6_2_9_to_6_2_81"]
        if query == "official_bytes":
            return model["verification_boundary"]["immutable_official_bytes"]
        if query == "gap_boundary":
            return {
                "critical": model["verification_boundary"]["critical_gap_created"],
                "high": model["verification_boundary"]["high_gap_created"],
            }
        raise AssertionError(query)

    assert model["status"] == "VERIFIED_BOUNDED_PARTIAL_CLAUSE_MODEL_6_1_AND_6_2_1_TO_6_2_8"
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 9 data types; 6 common minimum and 3 common additional fields; 8/81 schemas; 33 required and 36 additional placements; 64 fail-closed cases")


if __name__ == "__main__":
    main()
