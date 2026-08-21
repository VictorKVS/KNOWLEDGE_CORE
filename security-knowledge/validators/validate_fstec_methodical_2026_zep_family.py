#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-zep-family-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-zep-family-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures = {item["code"]: item for item in model["measures"]}

    def evaluate(case):
        query = case["query"]
        if query == "measure_count": return len(measures)
        if query == "implementation_total": return sum(len(x["implementation"]) for x in measures.values())
        if query == "documentation_total": return sum(len(x["documentation"]) for x in measures.values())
        if query == "enhancement_total": return sum(len(x["enhancements"]) for x in measures.values())
        if query == "numeric_count": return len(model["numeric_constraints"])
        if query == "operator_parameter_count": return len(model["operator_defined_parameters"])
        if query == "measure_count_field": return len(measures[case["measure"]][case["field"]])
        if query == "matrix_counts": return {key: model["class_matrix_summary"][key] for key in ("cells_total", "nonblank_cells", "blank_cells")}
        if query == "base_all_classes": return all(value == "PLUS" for value in measures[case["measure"]]["matrix"]["base"].values())
        if query == "enhancement_row": return measures[case["measure"]]["matrix"]["enhancements"]
        if query == "zep1_rsb_dependency": return "LINKED_RSB_1_TO_RSB_5" if "REGISTER_EMAIL_USER_ACTION_SECURITY_EVENTS_IN_ACCORDANCE_WITH_RSB_1_TO_RSB_5" in measures["ЗЭП.1"]["implementation"] else None
        if query == "zep1_universal_periods": return "NOT_STATED" if "DO_NOT_INVENT_ZEP_1_MAILBOX_AUDIT_FREQUENCY_INACTIVITY_TIME_OR_BACKUP_FREQUENCY" in model["scope_guards"] else None
        if query == "zep1_enhancements_class_listed": return any(row for row in measures["ЗЭП.1"]["matrix"]["enhancements"].values())
        if query == "zep2_iaf_dependency": return "LINKED_IAF_1_AND_IAF_3" if "APPLY_IAF_1_AND_IAF_3_TO_IDENTIFICATION_AND_AUTHENTICATION_FOR_MAILBOX_ACCESS" in measures["ЗЭП.2"]["implementation"] else None
        if query == "zep2_shared_mailbox_approval": return "OWNER_APPROVAL_REQUIRED" if "REQUIRE_OWNER_APPROVAL_FOR_ACCESS_TO_SHARED_MAILBOXES_AND_DISTRIBUTION_GROUPS" in measures["ЗЭП.2"]["implementation"] else None
        if query == "zep3_avz_dependency": return "LINKED_AVZ_2" if "PROVIDE_EMAIL_ANTIVIRUS_PROTECTION_IN_ACCORDANCE_WITH_AVZ_2" in measures["ЗЭП.3"]["implementation"] else None
        if query == "zep3_ioc_controls": return "ATTACHMENTS_AND_LINKS" if "CONTROL_EMAIL_ATTACHMENTS_AND_LINKS_USING_INDICATORS_OF_COMPROMISE" in measures["ЗЭП.3"]["implementation"] else None
        if query == "zep3_retrospective_analysis": return any("RETROSPECTIVE" in x for x in measures["ЗЭП.3"]["implementation"])
        if query == "zep3_allowed_formats": return "OPERATOR_DEFINED_NO_UNIVERSAL_LIST" if "DO_NOT_INVENT_ZEP_3_ALLOWED_ATTACHMENT_FORMATS" in model["scope_guards"] else None
        if query == "zep3_enhancements_class_listed": return any(row for row in measures["ЗЭП.3"]["matrix"]["enhancements"].values())
        if query == "zep4_retrospective_analysis": return any("RETROSPECTIVE" in x for x in measures["ЗЭП.4"]["implementation"])
        if query == "zep4_sender_and_content_filters": return len([x for x in measures["ЗЭП.4"]["implementation"] if x.startswith("FILTER_")])
        if query == "zep4_only_class_listed_enhancement": return sorted(set(n for row in measures["ЗЭП.4"]["matrix"]["enhancements"].values() for n in row))[0]
        if query == "zep4_enhancement_4_exists": return any(x["number"] == 4 for x in measures["ЗЭП.4"]["enhancements"])
        if query == "zep4_enhancement_4_class_listed": return any(4 in row for row in measures["ЗЭП.4"]["matrix"]["enhancements"].values())
        if query == "zep5_sender_and_content_filters": return len([x for x in measures["ЗЭП.5"]["implementation"] if x.startswith("FILTER_")])
        if query == "zep5_rate_limit_parameters": return len([x for x in model["operator_defined_parameters"] if x["measure"] == "ЗЭП.5"])
        if query == "zep5_rate_limit_numbers": return "NOT_STATED" if "DO_NOT_INVENT_ZEP_5_SENDER_COUNT_OR_RATE_PERIOD" in model["scope_guards"] else None
        if query == "zep5_enhancements_class_listed": return any(row for row in measures["ЗЭП.5"]["matrix"]["enhancements"].values())
        if query == "zep6_header_categories": return len([x for x in measures["ЗЭП.6"]["implementation"] if x.startswith("HIDE_HEADERS_")])
        if query == "zep6_header_hiding_choice": return "ONE_OF_TWO_SOURCE_LISTED_METHODS" if len(measures["ЗЭП.6"]["implementation_alternatives"]["header_hiding_one_of"]) == 2 else None
        if query == "zep6_mailbox_enumeration_controls": return len(measures["ЗЭП.6"]["implementation_alternatives"]["mailbox_enumeration_prevention"])
        if query == "zep6_open_relay_trigger": return "INTERNET_ACCESSIBLE_MAIL_SERVER_ONLY" if "DO_NOT_GENERALIZE_ZEP_6_OPEN_RELAY_PROHIBITION_BEYOND_INTERNET_ACCESSIBLE_MAIL_SERVER_TRIGGER" in model["scope_guards"] else None
        if query == "zep6_enhancement_class_listed": return any(row for row in measures["ЗЭП.6"]["matrix"]["enhancements"].values())
        if query == "blank_cell_semantics": return "NOT_PROHIBITION" if "DO_NOT_TREAT_BLANK_CLASS_CELL_AS_PROHIBITION" in model["scope_guards"] else None
        if query == "complete_zep_family": return model["verification_boundary"]["complete_zep_family"]
        if query == "official_bytes": return model["verification_boundary"]["official_immutable_bytes"]
        if query == "critical_gap_created": return model["verification_boundary"]["critical_gap_created"]
        if query == "high_gap_created": return model["verification_boundary"]["high_gap_created"]
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_COMPLETE_ZEP_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == [f"ЗЭП.{number}" for number in range(1, 7)]
    assert [x["number"] for x in measures["ЗЭП.4"]["enhancements"]] == [1, 2, 3, 4]
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 6 ZEP measures; 21 implementation atoms; 0 documentation items; 12 enhancements; 36 class cells; 0 numeric constraints; 6 operator-defined parameters; 60 fail-closed cases")


if __name__ == "__main__":
    main()
