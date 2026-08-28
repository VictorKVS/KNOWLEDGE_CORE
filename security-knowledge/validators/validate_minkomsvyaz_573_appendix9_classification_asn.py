#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-classification-asn-oid-registry-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-classification-asn-oid-registry-regression-v1.json")


def flatten(model):
    return {
        symbol: value
        for group in model["registry"].values()
        for symbol, value in group.items()
    }


def evaluate(case, model, symbols):
    if date.fromisoformat(case["date"]) < date(2024, 3, 1):
        return "HISTORICAL_PRE_REPLACEMENT"
    if case["query"] == "semantic_type":
        return "PASS_OBJECT_DESCRIPTOR_NOT_OBJECT_IDENTIFIER"
    if case["query"] == "symbol":
        symbol = case["symbol"]
        if "presence" in symbol and "presense" not in symbol:
            return "BLOCK_NORMALIZED_ALIAS_NOT_LITERAL"
        value = symbols.get(symbol)
        if value is None:
            return "BLOCK_UNKNOWN_SYMBOL"
        if value == "PENDING_PRIMARY_PDF":
            return value
        return f"PASS:{value}"
    if case["query"] == "oid":
        if case["oid"] == "163":
            return "ABSENT_NOT_ASSIGNABLE"
        match = [symbol for symbol, value in symbols.items() if value == case["oid"]]
        return f"PASS:{match[0]}" if len(match) == 1 else "BLOCK_UNKNOWN_OR_AMBIGUOUS_OID"
    raise AssertionError(case["query"])


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    symbols = flatten(model)
    executable = {symbol: value for symbol, value in symbols.items() if value != "PENDING_PRIMARY_PDF"}

    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 32
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 15
    assert len(symbols) == model["counts"]["declared_symbols"] == 101
    assert len(executable) == model["counts"]["safely_executable_values"] == 100
    assert len(set(executable.values())) == 100
    assert symbols["sorm-request-identifier-pstn"] == "PENDING_PRIMARY_PDF"
    assert model["source_anomalies"][0]["observed_open_text_token"] == '141"'
    assert "163" not in executable.values()
    assert symbols["sorm-request-connection-mobile"] == "162"
    assert symbols["sorm-request-connection-aaa-login"] == "164"
    assert sum("presense" in symbol for symbol in symbols) == 6
    assert not any("presence" in symbol for symbol in symbols)
    assert model["asn1_module"]["oid_alias"]["semantic_type"] == "OBJECT_DESCRIPTOR"
    assert model["asn1_module"]["oid_alias"]["prohibited_interpretation"] == "ASN1_OBJECT_IDENTIFIER"
    assert model["temporal_model"]["effective_from"] == "2024-03-01"
    assert symbols["sorm-message-session"] == "280"
    assert symbols["sorm-report-abonent-abonent"] == "40"
    assert symbols["sorm-request-payment-express-pays"] == "221"
    assert symbols["sorm-report-payment-bank-account-transfer"] == "89"
    assert symbols["sorm-report-data-content-raw"] == "50"
    prohibited_normalizations = {
        "sorm-session", "sorm-report-abonent", "sorm-report-service",
        "sorm-request-payment-express-payment", "sorm-report-raw-content",
    }
    assert prohibited_normalizations.isdisjoint(symbols)
    assert len(fixtures["cases"]) == 64
    assert len({case["id"] for case in fixtures["cases"]}) == 64

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case, model, symbols)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print(
        "PASS: Order 573 appendix 9 Classification.asn; 32 rules, 15 evidence nodes, "
        "101 symbols, 100 executable values, 64 cases; PSTN141, gap163 and presense fail-closed"
    )


if __name__ == "__main__":
    main()
