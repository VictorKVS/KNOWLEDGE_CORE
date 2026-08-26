#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/fstec-order-236-2025-kii-categorization-result-form-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/fstec-order-236-2025-kii-categorization-result-form-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}
    fields = [field for section in model["sections"] for field in section["fields"]]

    assert model["status"] == "VERIFIED_CURRENT_FORM_34_FIELDS_2019_2025_LIFECYCLE"
    assert model["edition_effective_date"] == "2025-09-01"
    assert len(model["temporal_lifecycle"]) == 3
    assert len(model["sections"]) == 9
    assert len(fields) == 34
    assert [field["id"] for field in fields] == [
        "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8",
        "2.1", "2.2", "2.3", "2.4", "2.5", "2.6",
        "3.1", "3.2", "3.3", "3.4", "4.1", "4.2", "4.3", "4.4",
        "5.1", "5.2", "5.3", "5.4", "6.1", "6.2", "7.1",
        "8.1", "8.2", "8.3", "9.1", "9.2"
    ]
    assert model["submission_contract"]["paper_copy"] == "REQUIRED"
    assert model["submission_contract"]["electronic_copy"]["file_format"] == "ODS_OPEN_DOCUMENT_SPREADSHEET"
    assert model["sections"][-1]["applicability"] == "SIGNIFICANT_OBJECT_ONLY"
    assert len(model["current_2025_changes"]) == 6
    assert model["historical_2019_changes"]["repealed"] == ["7.2"]
    assert len(rules) == 64
    assert list(rules) == [f"F236-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    assert rules["F236-044"] == "REQUIRE_ELECTRONIC_COPY_IN_ODS_FORMAT"
    assert rules["F236-062"] == "DO_NOT_INVENT_SUBMISSION_DEADLINE_FROM_FORM_ORDER"
    assert model["verification_boundary"]["critical_gap_created"] == 0
    assert model["verification_boundary"]["high_gap_created"] == 0

    failures = []
    for case in fixtures["cases"]:
        actual = rules[case["rule_id"]]
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: FSTEC Order 236 current form; 9 sections, 34 fields, 3 versions, paper+ODS, 64 rules/cases")

if __name__ == "__main__":
    main()
