#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-abonents-party-details-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-abonents-party-details-regression-v1.json")

def named(items, name):
    return next((item for item in items if item["name"] == name), None)

def evaluate(case, model):
    query = case["query"]
    types = model["types"]
    if query == "temporal":
        observed = date.fromisoformat(case["date"])
        if observed < date(2024, 3, 1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_PARTY_DETAILS_VERSION" if observed < date(2030, 3, 1) else "EXPIRED_ROUTE"
    if query == "open-type":
        return "PASS_REQUIRED_FIELDS_RENDERED_BINDING_PENDING" if all(not x["optional"] for x in model["open_type"]["fields"]) else "BLOCK_OPEN_TYPE"
    if query == "variant":
        item = named(model["variants"], case["name"])
        if item is None: return "BLOCK_UNKNOWN_VARIANT"
        return "PASS" if item["oid"] == case["oid"] and item["data_type"] == case["data_type"] else "BLOCK_VARIANT_BINDING_MISMATCH"
    if query == "field":
        item = named(types[case["type"]]["fields"], case["name"])
        if item is None: return "BLOCK_UNKNOWN_FIELD"
        if item.get("tag") != case["tag"]: return "BLOCK_TAG_MISMATCH"
        return "PASS_OPTIONAL" if item["optional"] else "PASS_REQUIRED"
    if query == "boundary-field":
        item = named(types[case["type"]]["fields"], case["name"])
        if "size_min" in item:
            return "PASS" if item["size_min"] <= case["value"] <= item["size_max"] else "BLOCK_SIZE"
        return "PASS" if item["value_min"] <= case["value"] <= item["value_max"] else "BLOCK_RANGE"
    if query == "choice":
        item = named(types[case["type"]]["branches"], case["name"])
        return "PASS" if item and item["tag"] == case["tag"] else "BLOCK_CHOICE"
    if query == "boundary-choice":
        item = named(types[case["type"]]["branches"], case["name"])
        return "PASS" if item["size_min"] <= case["value"] <= item["size_max"] else "BLOCK_SIZE"
    if query == "field-count":
        fields = types[case["type"]]["fields"]
        return "PASS" if len(fields) == case["count"] and sum(not x["optional"] for x in fields) == case["required"] else "BLOCK_FIELD_CONTRACT"
    if query == "literal-type":
        return "PASS_LITERAL_RENDERED_NAME" if case["name"] in types else "BLOCK_UNKNOWN_TYPE"
    if query == "sequence-of":
        item = types[case["type"]]
        return "PASS_LITERAL_RENDERED_ELEMENT" if item["kind"] == "SEQUENCE OF" and item["rendered_element_type"] == case["rendered_element_type"] else "BLOCK_TYPE_MISMATCH"
    if query == "syntax": return "PENDING_PRIMARY_PDF"
    if query == "semantic": return "NOT_SPECIFIED_NO_OVERRIDE"
    raise AssertionError(query)

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules, evidence, types = model["atomic_rules"], model["evidence_model"], model["types"]
    assert len(rules) == len({x["id"] for x in rules}) == 64
    assert [x["id"] for x in rules] == [f"MK573RAP-R{i:03d}" for i in range(1,65)]
    assert len(evidence) == len({x["id"] for x in evidence}) == 18
    assert [r for node in evidence for r in node["proves"]] == [x["id"] for x in rules]
    assert [(x["name"],x["oid"],x["data_type"]) for x in model["variants"]] == [
        ("abonentPerson","sorm-report-abonent-person","AbonentPerson"),
        ("abonentOrganization","sorm-report-abonent-organization","AbonentOrganization")]
    person = types["AbonentPerson"]["fields"]
    assert len(person) == 9 and sum(not x["optional"] for x in person) == 2
    assert [(x["name"],x["tag"]) for x in person if x["tag"] is not None] == [("bank",1),("bank-account",2),("e-mail",3),("phone-contact",4),("ssid",5),("mac",6)]
    assert [(x["name"],x["tag"]) for x in types["PersonNameInfoReport"]["branches"]] == [("struct-name",0),("unstruct-name",1)]
    names = types["PersonStructNameInfoReport"]["fields"]
    assert [x["name"] for x in names] == ["given-name","initial","family-name"] and all(not x["optional"] for x in names)
    assert types["PassportInfoReportm"]["referenced_name"] == "PassportInfoReport" and types["PassportInfoReportm"]["name_link_status"] == "PENDING_PRIMARY_PDF"
    assert [(x["name"],x["tag"]) for x in types["IdentCardInfoReport"]["branches"]] == [("struct-info",0),("unstruct-info",1)]
    org = types["AbonentOrganization"]["fields"]
    assert len(org) == 10 and sum(not x["optional"] for x in org) == 2
    assert [(x["name"],x["tag"]) for x in org if x["optional"]] == [("contact",0),("phone-fax",1),("internal-users",2),("bank",3),("bank-account",4),("e-mail",5),("ssid",6),("mac",7)]
    iu = types["InternalUsers"]
    assert iu["rendered_element_type"] == "IntemalUsersRecord" and iu["declared_element_type"] == "InternalUsersRecord" and iu["count_constraint"] is None
    iuf = types["InternalUsersRecord"]["fields"]
    assert [x["name"] for x in iuf] == ["user-name","internal-number"] and all(not x["optional"] for x in iuf)
    assert len(fixtures["cases"]) == len({x["id"] for x in fixtures["cases"]}) == 64
    failures = [(c["id"],c["expected"],evaluate(c,model)) for c in fixtures["cases"] if evaluate(c,model) != c["expected"]]
    if failures:
        print(*failures,sep="\n"); raise SystemExit(1)
    assert not model["verification_boundary"]["critical_gap_created"] and not model["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 ReportsAbonents party details; 64 rules, 18 evidence nodes, 2 variants, 9 person fields, 10 organization fields, 64 cases")

if __name__ == "__main__": main()
