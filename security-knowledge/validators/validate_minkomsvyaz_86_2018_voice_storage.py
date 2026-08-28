#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-86-2018/voice-information-storage-current-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-86-2018/voice-information-storage-current-regression-v1.json")

CURRENT_SERVICES = {
    "LOCAL_TELEPHONE", "INTERNATIONAL_INTERCITY_TELEPHONE",
    "TELEPHONE_IN_DEDICATED_NETWORK", "INTRAZONE_TELEPHONE",
    "MOBILE_RADIO_PUBLIC_NETWORK", "MOBILE_RADIO_DEDICATED_NETWORK",
    "MOBILE_RADIOTELEPHONE_INCLUDING_MVNO", "MOBILE_SATELLITE",
}


def version(value):
    d = date.fromisoformat(value)
    if d < date(2018, 4, 9):
        return "PRE_ORDER86"
    if d < date(2023, 9, 1):
        return "ORDER86_ORIGINAL"
    if d < date(2026, 3, 15):
        return "ORDER86_ORDER47"
    if d < date(2029, 9, 1):
        return "ORDER86_ORDER47_ORDER1196"
    return "ORDER86_EXPIRED"


def evaluate(c):
    q = c["query"]
    if q == "version":
        return version(c["date"])
    if q == "deleted_point":
        if not c["claim_current"]:
            return "HISTORICAL_ONLY"
        if c["point"] == "5.7" and date.fromisoformat(c["date"]) >= date(2023, 9, 1):
            return "BLOCK_REPEALED_POINT5_7"
        if c["point"] == "2.9" and date.fromisoformat(c["date"]) >= date(2026, 3, 15):
            return "BLOCK_REPEALED_POINT2_9"
        return "HISTORICAL_CURRENT_FOR_DATE"
    if q == "scope":
        if c["node"] not in {"TERMINAL", "TRANSIT", "TERMINAL_TRANSIT"}:
            return "BLOCK_SCOPE"
        if c["service"] == "DATA_TRANSMISSION_FOR_VOICE" and date.fromisoformat(c["date"]) >= date(2026, 3, 15):
            return "BLOCK_REPEALED_LICENSE_SCOPE"
        return "PASS" if c["service"] in CURRENT_SERVICES else "BLOCK_SCOPE"
    if q == "appendix_row9":
        return "BLOCK_SCOPE_RESTORATION" if c["restore_point2_9"] else "TEXT_REMAINS_WITHOUT_SCOPE_RESTORATION"
    if q == "point4_tension":
        return "BLOCK_INVENTED_RESOLUTION" if c["invent_resolution"] else "PENDING_FAIL_CLOSED"
    if q == "product_route":
        return "PASS_IF_PRODUCT_MATCHES" if c["current_crosswalk"] else "BLOCK_STALE_PRODUCT_ROUTE"
    if q == "passive_collection":
        return "BLOCK_ACTIVE_TRANSMISSION" if c["transmits_to_network"] else "PASS"
    if q == "content_families":
        return "PASS" if c["count"] == 4 else "BLOCK_CONTENT_SET"
    if q == "control_points":
        if c["count"] > 100:
            return "BLOCK_CONTROL_POINT_LIMIT"
        if c["head"] != 1:
            return "BLOCK_HEAD_COUNT"
        return "PASS" if c["is_bd_additional"] else "BLOCK_IS_BD_ROUTE"
    if q == "remote_access":
        return "PASS" if c["control_point"] and c["is_bd_orm"] and c["continuous"] else "BLOCK_REMOTE_ACCESS"
    if q == "connection_metadata":
        keys = ("start_date", "start_time", "duration", "precision_seconds")
        return "PASS" if all(c[k] for k in keys) else "BLOCK_METADATA"
    if q == "failed_connection_duration":
        return "PASS" if c["seconds"] == 0 else "BLOCK_FAILED_DURATION"
    if q == "clock":
        return "PASS" if c["utc_synchronized"] else "BLOCK_CLOCK"
    if q == "content_access":
        return "PASS" if c["seconds_after_end"] <= 10 else "BLOCK_ACCESS_DELAY"
    if q == "query_types":
        return "PASS" if set(c["types"]) == {"STATISTICS", "TEXT", "VOICE_AND_VIDEO"} else "BLOCK_QUERY_TYPES"
    if q == "statistics_unload":
        if c["exact_connection_id"] and not c["statistics"]:
            return "PASS_EXCEPTION"
        return "PASS" if c["statistics"] else "BLOCK_MISSING_STATISTICS"
    if q == "filters":
        return "PASS" if c["multiple"] and c["logic"] == "AND" else "BLOCK_FILTER_LOGIC"
    if q == "wildcard":
        expected = {"*": "ANY_SEQUENCE_INCLUDING_EMPTY", "?": "EXACTLY_ONE_CHARACTER"}
        return "PASS" if expected.get(c["symbol"]) == c["meaning"] else "BLOCK_WILDCARD"
    if q == "phone_format":
        return "PASS" if c["format"] == "E164" else "BLOCK_PHONE_FORMAT"
    if q == "vpn":
        return "BLOCK_OVERSTATEMENT" if c["treat_recommendation_as_absolute"] else "RECOMMENDATION_ONLY"
    if q == "retention":
        if c["clock_start"] != "CONNECTION_OR_MESSAGE_TRANSFER_END":
            return "BLOCK_CLOCK_START"
        return "PASS" if c["duration_source"] == "PP445" else "BLOCK_INVENTED_DURATION"
    if q == "capacity":
        n, mbps = c["subscribers_thousands"], c["mbps"]
        if c["table"] == "MOBILE":
            required = 4 if n <= 10 else 10 if n <= 100 else 100 if n <= 1000 else 300 if n <= 10000 else 500
        else:
            if n == 100:
                return "PENDING_FIXED_100_THOUSAND_BOUNDARY"
            required = 4 if n <= 10 else 10 if n < 100 else 100
        return "PASS" if mbps >= required else "BLOCK_CAPACITY"
    if q == "query_rate":
        return "PASS" if c["percent"] <= 70 else "BLOCK_RATE_CEILING"
    if q == "fixed_storage":
        return "PASS" if c["text"] and c["voice"] and c["video"] else "BLOCK_FIXED_STORAGE"
    if q == "mobile_storage":
        if c["video"]:
            return "BLOCK_INVENTED_VIDEO_STORAGE"
        return "PASS" if c["text"] and c["voice"] else "BLOCK_MOBILE_STORAGE"
    if q == "simultaneous_queries":
        if c["count"] < 100:
            return "BLOCK_QUERY_CAPACITY"
        return "PASS" if c["count"] == 100 or not c["claim_timed"] else "BLOCK_TIMING_ABOVE100"
    if q == "identifier_time":
        if c["identifier"] in {"DPC_OPC", "BASE_STATION"}:
            required = 420
        else:
            required = {"1_DAY": 3, "1_MONTH": 5, "6_MONTHS": 15}[c["interval"]]
        return "PASS" if c["seconds"] <= required else "BLOCK_QUERY_TIME"
    if q == "result_start":
        return "PASS" if c["seconds"] <= 2 * c["days"] else "BLOCK_RESULT_START"
    if q == "content_start":
        return "PASS" if c["seconds"] <= 10 else "BLOCK_CONTENT_START"
    raise AssertionError(q)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({x["id"] for x in model["atomic_rules"]}) == 54
    assert len(model["temporal_model"]) == 5
    assert len(model["evidence_model"]) == len({x["id"] for x in model["evidence_model"]}) == 20
    assert model["sources"]["effective_from"] == "2018-04-09"
    assert model["sources"]["validity_until_exclusive"] == "2029-09-01"
    assert len(model["applicability"]["current_license_services"]) == 8
    assert model["common_requirements"]["distributed_node"]["control_points_max"] == 100
    assert model["common_requirements"]["content_access_max_seconds_after_connection_end"] == 10
    assert model["common_requirements"]["query_transfer_total_rate_max_percent_of_control_channel"] == 70
    assert len(model["channel_capacity_tables"]["mobile_and_historical_voice_data_table1"]["subscriber_base_thousands_to_min_mbps"]) == 5
    assert len(model["channel_capacity_tables"]["fixed_table2"]["subscriber_base_thousands_to_min_mbps"]) == 3
    assert model["appendices_open_core"]["appendix1"]["interface_entries"] == 25
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert len(fixtures["cases"]) == 64
    failures = []
    for c in fixtures["cases"]:
        actual = evaluate(c)
        if actual != c["expected"]:
            failures.append((c["id"], c["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: Order 86 current voice-storage open core; 54 rules, 5 temporal routes, 20 evidence nodes, 64 cases; Order 47 and Order 1196 deltas applied; deep protocol tables pending")


if __name__ == "__main__":
    main()
