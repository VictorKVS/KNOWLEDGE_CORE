#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/subscriber-database-is-orm-current-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/subscriber-database-is-orm-current-regression-v1.json")


def version(value):
    d = date.fromisoformat(value)
    if d < date(2018, 12, 30):
        return "PRE_ORDER573"
    if d < date(2024, 3, 1):
        return "ORDER573_ORIGINAL"
    if d < date(2026, 3, 15):
        return "ORDER573_ORDER630"
    if d < date(2030, 3, 1):
        return "ORDER573_ORDER630_ORDER1196"
    return "ORDER573_EXPIRED"


def evaluate(c, model):
    q = c["query"]
    if q == "version":
        return version(c["date"])
    if q == "repealed":
        if not c["claim_current"]:
            return "HISTORICAL_ONLY"
        if date.fromisoformat(c["date"]) >= date(2026, 3, 15):
            return "BLOCK_REPEALED_POINT5_13" if c["item"] == "POINT5_13" else "BLOCK_REPEALED_APPENDIX10_ROW13"
    if q == "service":
        if c["service"] == "DATA_TRANSMISSION_FOR_VOICE" and date.fromisoformat(c["date"]) >= date(2026, 3, 15):
            return "BLOCK_REPEALED_SERVICE"
        return "PASS" if c["service"] in model["applicability"]["current_point5_service_routes"] else "BLOCK_SCOPE"
    if q == "certification":
        return "PASS" if c["pp113_item"] == 30 and c["pp1387"] else "BLOCK_CERTIFICATION_ROUTE"
    if q == "placement":
        return "PASS" if c["in_russia"] and c["operator_node"] else "BLOCK_PLACEMENT"
    if q == "channels":
        return "PASS" if c["channels"] == ["KPD1", "KPD2", "KPD3", "KPD4", "KPD5"] else "BLOCK_CHANNEL_SET"
    if q == "information_family":
        return "PASS" if c["family"] == "FAILED_CONNECTION_ATTEMPTS" else "BLOCK_INFORMATION_FAMILY"
    if q == "other_information":
        return "PASS" if c["federal_law_basis"] else "BLOCK_NO_FEDERAL_LAW_BASIS"
    if q == "security_actors":
        return "PASS" if c["count"] == 4 else "BLOCK_ACTOR_SET"
    if q == "unauthorized_attempts":
        return "PASS" if c["count"] == 5 else "BLOCK_ATTEMPT_SET"
    if q == "remote_access":
        return "PASS" if c["continuous"] and c["authorized"] else "BLOCK_REMOTE_ACCESS"
    if q == "modernization":
        return "PASS" if c["preserves_data"] else "BLOCK_DATA_LOSS"
    if q == "order86_integration":
        return "PASS" if c["additional_record"] and c["description"] else "BLOCK_INTEGRATION_EVIDENCE"
    if q == "retention":
        if c["kind"] == "CAPACITY":
            return "BLOCK_CAPACITY_SOURCE"
        expected = "UP_TO_SIX_MONTHS" if c["kind"] == "CONTENT" else "THREE_YEARS"
        if c["kind"] == "CONTENT" and c["duration"] == "SIX_MONTHS_EXACT":
            return "BLOCK_OVERSTATEMENT"
        return "PASS" if c["duration"] == expected else "BLOCK_RETENTION"
    if q == "content_clock":
        return "PASS" if c["clock"] == "END_OF_RECEIPT_TRANSMISSION_DELIVERY_OR_PROCESSING" else "BLOCK_CLOCK"
    if q == "deletion":
        return "PASS" if c["automatic"] and c["source"] == "PP445_POINT8" else "BLOCK_DELETION_ROUTE"
    if q == "data_families":
        return "PASS" if c["count"] == 11 else "BLOCK_DATA_FAMILY_COUNT"
    if q == "telephone_families":
        return "PASS" if c["count"] == 4 else "BLOCK_TELEPHONE_FAMILY_COUNT"
    if q == "aggregation":
        return "PASS" if c["minutes"] == 5 and c["same_ip_pair"] and c["same_ports"] else "BLOCK_AGGREGATION_WINDOW"
    if q == "vowifi":
        return "PASS" if c["telephone_statistics"] and c["location"] in {"COORDINATES", "IP_AND_PORT"} else "BLOCK_VOWIFI_ROUTE"
    if q == "tls":
        return "PASS" if c["mutual"] and c["version"] == "1.2" else "BLOCK_INVENTED_TLS_VERSION"
    if q == "filters":
        expected = {"IP_OR_SUBNET", "VLAN", "MPLS_LABEL", "SNI_OR_URL"}
        return "PASS" if set(c["criteria"]) == expected and c["record_all_without_rules"] else "BLOCK_FILTER_ROUTE"
    if q == "preprocessing":
        limits = {"SUBSCRIBER_IDENTIFIER": 5, "ACCESS_CARD_IDENTIFIER": 5, "SMS_IDENTIFIER": 30,
                  "TEMPORARY_IDENTIFIER": 30, "NETWORK_CHANGE": 30, "TELEPHONE_OR_LOCATION": 300,
                  "DATA_NETWORK_CONNECTION": 600}
        return "PASS" if c["seconds"] <= limits[c["route"]] else "BLOCK_PREPROCESSING_TIME"
    if q == "direct_search":
        limits = {"IDENTIFIER_OWNERSHIP": 1, "PAYMENT_CARD": 1, "REGISTERED_IDENTIFIERS": 3,
                  "BALANCE_REPLENISHMENT": 1}
        return "PASS" if c["seconds"] <= limits[c["route"]] else "BLOCK_SEARCH_TIME"
    if q == "simultaneous_search":
        return "PASS" if c["count"] >= 100 else "BLOCK_SEARCH_CAPACITY"
    if q == "deep_table":
        return "PASS" if c["immutable_pages_verified"] else "PENDING_FAIL_CLOSED"
    if q == "buffer":
        minimum = 3 if c["route"] == "MOBILE_LOCATION" else 1
        return "PASS" if c["days"] >= minimum else "BLOCK_BUFFER_DURATION"
    if q == "kpd4_location":
        return "PASS" if c["minutes"] <= 5 else "BLOCK_KPD4_DELAY"
    raise AssertionError(q)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({x["id"] for x in model["atomic_rules"]}) == 60
    assert len(model["temporal_model"]) == 5
    assert len(model["evidence_model"]) == len({x["id"] for x in model["evidence_model"]}) == 20
    assert model["sources"]["effective_from"] == "2018-12-30"
    assert model["sources"]["validity_until_exclusive"] == "2030-03-01"
    assert len(model["applicability"]["current_point5_service_routes"]) == 13
    assert len(model["system_functions"]["control_point_channels"]) == 5
    assert model["order630_current_features"]["data_network_connection_families"] == 11
    assert model["order630_current_features"]["telephone_connection_families"] == 4
    assert model["timing_requirements"]["simultaneous_search_tasks_min"] == 100
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert len(fixtures["cases"]) == 66
    failures = []
    for c in fixtures["cases"]:
        actual = evaluate(c, model)
        if actual != c["expected"]:
            failures.append((c["id"], c["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: Order 573 current subscriber-database IS ORM open core; 60 rules, 5 temporal routes, 20 evidence nodes, 66 cases; Orders 630 and 1196 applied; deep ASN.1 and field tables pending")


if __name__ == "__main__":
    main()
