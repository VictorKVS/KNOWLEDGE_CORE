#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-268-2012/appendices5-to11-protocol-core-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-268-2012/appendices5-to11-protocol-core-regression-v1.json")

COMMAND_CODES = {i: f"{i:02X}H" for i in range(1, 18)}
KPD1_CODES = {i: f"{0x20 + i:02X}H" for i in range(1, 13)}
KPD2_CODES = {
    "1.1": "41H", "1.2": "42H", "1.3": "43H", "1.4": "44H",
    "2.1": "51H", "2.2": "52H", "2.3": "53H",
}
MESSAGE8_STATUS = {
    "00H": "COMMAND_EXECUTED",
    "01H": "COMMAND_NOT_EXECUTED",
    "03H": "WRONG_PASSWORD",
    "05H": "WRONG_TECHNICAL_MEANS_NUMBER",
    "07H": "NOT_EXECUTED_TECHNICAL_MEANS_ALREADY_STARTED",
}


def evaluate(case):
    query = case["query"]
    if query == "command_code":
        return COMMAND_CODES[case["number"]]
    if query == "sequence":
        if not case.get("started", True) or not case.get("format_valid", True):
            return "MESSAGE7_COMMAND_REJECTED"
        if not case.get("password_valid", True) or not case.get("number_valid", True):
            return "ACCEPT_NOT_EXECUTE_MESSAGES7_8_6"
        if case["command"] in {2, 7, 8, 13, 14}:
            return "ACCEPT_PRIORITY"
        if not case.get("prior_complete", True):
            return "WAIT_PREVIOUS_RESULT"
        return "ACCEPT_SERIAL"
    if query == "inactivity":
        if case["minutes"] >= 10 and not case["valid_non_start_command_received"]:
            return "STOP_KPD_DESTROY_UNSENT_DO_NOT_BLOCK_CONTENT"
        return "CONTINUE"
    if query == "kpd1_header":
        if not 1 <= case["content_length"] <= 245:
            return "BLOCK_CONTENT_LENGTH"
        if not 1 <= case["total"] <= 65535:
            return "BLOCK_FRAGMENT_COUNT"
        if not 1 <= case["current"] <= case["total"]:
            return "BLOCK_FRAGMENT_NUMBER"
        return "PASS" if case["version"] == "02H" else "BLOCK_VERSION"
    if query == "kpd1_code":
        return KPD1_CODES[case["number"]]
    if query == "message7_latency":
        return "PASS" if case["milliseconds"] <= 400 else "BLOCK_LATE_MESSAGE7"
    if query == "message8_status":
        return MESSAGE8_STATUS.get(case["code"], "BLOCK_UNKNOWN_STATUS")
    if query == "message9_latency":
        if case["trigger"] != "COMMAND14":
            return "BLOCK_WRONG_TRIGGER"
        return "PASS" if case["milliseconds"] <= 200 else "BLOCK_LATE_MESSAGE9"
    if query == "kpd2_header":
        return "PASS" if (case["bytes"], case["preamble"], case["call_rollover"]) == (12, "CCH", "FFFEH_TO_0000H") else "BLOCK_KPD2_HEADER"
    if query == "kpd2_code":
        return KPD2_CODES[case["number"]]
    if query == "kpd2_mobile_only_code":
        return "BLOCK_NOT_IN_ORDER268_REGISTRY" if case["code"] in {"45H", "46H"} else "REVIEW_CODE"
    if query == "boundary":
        if case["claim_deep_table"] and not case["immutable_page_review"]:
            return "BLOCK_UNVERIFIED_DEEP_TABLE"
        return "PASS_IF_ARTIFACT_BOUND" if case["claim_deep_table"] else "PENDING_FAIL_CLOSED"
    if query == "unit_semantics":
        return "BLOCK_NOT_RETENTION" if case.get("treat_as_retention") else "PASS"
    raise AssertionError(f"Unhandled query {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({r["id"] for r in model["atomic_rules"]}) == 36
    assert len(model["temporal_model"]) == 2
    assert len(model["evidence_model"]) == len({e["id"] for e in model["evidence_model"]}) == 18
    assert model["sources"]["minjust_pdf_pages"] == 61
    assert model["command_header"]["bytes"] == 10
    assert len(model["command_codes"]) == 17
    assert [x["code"] for x in model["command_codes"]] == [COMMAND_CODES[i] for i in range(1, 18)]
    assert model["sequence_rules"]["priority_commands"]["numbers"] == [2, 7, 8, 13, 14]
    assert model["sequence_rules"]["inactivity"]["threshold_minutes"] == 10
    assert model["sequence_rules"]["inactivity"]["controlled_connection_content_blocked"] is False
    assert model["kpd1_header"]["bytes"] == 10
    assert model["kpd1_header"]["content_max_bytes"] == 245
    assert len(model["kpd1_message_codes"]) == 12
    assert [x["code"] for x in model["kpd1_message_codes"]] == [KPD1_CODES[i] for i in range(1, 13)]
    assert model["kpd1_exact_controls"]["message7_max_latency_ms"] == 400
    assert model["kpd1_exact_controls"]["message9_max_latency_ms"] == 200
    assert model["kpd2_header"]["bytes"] == 12
    assert len(model["kpd2_message_codes"]) == 7
    assert {x["number"]: x["code"] for x in model["kpd2_message_codes"]} == KPD2_CODES
    assert {"45H", "46H"}.isdisjoint({x["code"] for x in model["kpd2_message_codes"]})
    assert model["verification_boundary"]["minjust_official_pdf_complete_bytes_and_hash"] == "PENDING_DOWNLOAD_RATE_LIMIT"
    assert model["verification_boundary"]["deep_per_command_and_per_message_field_bit_tables"] == "PENDING_IMMUTABLE_PAGE_REVIEW"
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert len(fixtures["cases"]) == 52
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: Order 268 appendices 5-11 protocol core; 36 rules, 2 temporal routes, 17 commands, 12 KPD1 messages, 7 KPD2 messages, 18 evidence nodes, 52 cases; deep tables and complete official PDF bytes pending")


if __name__ == "__main__":
    main()
