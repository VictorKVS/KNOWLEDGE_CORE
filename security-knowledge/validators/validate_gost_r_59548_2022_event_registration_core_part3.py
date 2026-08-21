#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/standards/gost-r-59548-2022-event-registration-core-part3-v1.yaml")
FIXTURES = Path("security-knowledge/standards/gost-r-59548-2022-event-registration-core-part3-regression-v1.json")


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
        if query == "schema_count": return len(schemas)
        if query == "required_total": return sum(len(x["required_fields"]) for x in schemas.values())
        if query == "additional_total": return sum(len(x["additional_fields"]) for x in schemas.values())
        if query == "cumulative_modeled": return model["coverage"]["cumulative_modeled_subsections"]
        if query == "cumulative_pending": return model["coverage"]["cumulative_pending_subsections"]
        if query == "literal_set_count": return len(model["literal_value_sets"])
        if query == "required_count": return len(schemas[case["schema"]]["required_fields"])
        if query == "additional_count": return len(schemas[case["schema"]]["additional_fields"])
        if query == "modeled_ids": return list(schemas)
        if query == "field_property": return field(case)[case["property"]]
        if query == "literal_set": return model["literal_value_sets"][case["set"]]["values"]
        if query == "official_status_boundary": return model["verification_boundary"]["official_status_and_scope"]
        if query == "modeled_clause_boundary": return model["verification_boundary"]["clauses_6_2_21_to_6_2_32"]
        if query == "remaining_clause_boundary": return model["verification_boundary"]["clauses_6_2_33_to_6_2_81"]
        if query == "official_bytes": return model["verification_boundary"]["immutable_official_bytes"]
        if query == "guard": return case["guard"] in model["scope_guards"]
        if query == "gap_boundary":
            return {"critical": model["verification_boundary"]["critical_gap_created"], "high": model["verification_boundary"]["high_gap_created"]}
        raise AssertionError(query)

    assert model["status"] == "VERIFIED_BOUNDED_PARTIAL_CLAUSE_MODEL_6_2_21_TO_6_2_32"
    assert list(schemas) == [f"G59548-6.2.{i}" for i in range(21, 33)]
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures: print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 12 schemas; 89 required and 54 additional placements; cumulative 32/81; 64 fail-closed cases")


if __name__ == "__main__":
    main()
