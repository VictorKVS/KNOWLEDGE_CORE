import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "security-knowledge" / "legal-consequences" / "pdn-incident-consequence-router-regression-v2.json"


def route(f):
    out = []
    if not f.get("personal_data_involved", False):
        return ["NOT_APPLICABLE_PDN_ROUTER"]

    if f.get("intent_notice_failure"):
        out.append("KOAP_13_11_P10_REVIEW")
    if f.get("breach_notice_failure"):
        out.append("KOAP_13_11_P11_REVIEW")

    breach = f.get("breach_or_leak", False)
    special = f.get("special_category_data", False)
    biometric = f.get("biometric_data", False)
    ebs = f.get("biometric_ebs_context", False)

    if ebs and f.get("biometric_security_failure"):
        out.append("KOAP_13_11_3_REVIEW")
    elif breach and biometric:
        out.append("KOAP_13_11_P17_REVIEW")
    elif breach and special:
        out.append("KOAP_13_11_P16_REVIEW")
    elif breach:
        subjects = f.get("affected_subject_count")
        identifiers = f.get("identifier_count")
        if subjects is None and identifiers is None:
            out.append("NEEDS_BREACH_SCOPE_FACTS")
        else:
            p = None
            if (subjects is not None and subjects > 100000) or (identifiers is not None and identifiers > 1000000):
                p = 14
            elif (subjects is not None and subjects >= 10000) or (identifiers is not None and identifiers >= 100000):
                p = 13
            elif (subjects is not None and subjects >= 1000) or (identifiers is not None and identifiers >= 10000):
                p = 12
            if p:
                out.append(f"KOAP_13_11_P{p}_CANDIDATE")
                if not f.get("criminal_signs_assessed", False):
                    out.append("NEEDS_CRIMINAL_SIGNS_REVIEW")
                elif f.get("criminal_signs_present", False):
                    uk_fact = f.get("unlawfully_obtained_personal_data") and f.get("unlawful_use_transfer_collection_storage")
                    if uk_fact:
                        out.append("ROUTE_UK_272_1_REVIEW")
                    else:
                        out.append("NEEDS_CRIMINAL_QUALIFICATION")
                else:
                    out.append(f"KOAP_13_11_P{p}_REVIEW")

    if f.get("repeat_predicate_proven", False):
        if "KOAP_13_11_P16_REVIEW" in out or "KOAP_13_11_P17_REVIEW" in out:
            out.append("KOAP_13_11_P18_REVIEW")
        elif any(x in out for x in ["KOAP_13_11_P12_REVIEW", "KOAP_13_11_P13_REVIEW", "KOAP_13_11_P14_REVIEW"]):
            out.append("KOAP_13_11_P15_REVIEW")

    return list(dict.fromkeys(out))


def main():
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = route(case["facts"])
        for item in case["expected"].get("contains", []):
            if item not in actual:
                failures.append(f"{case['id']}: missing {item}; actual={actual}")
        for item in case["expected"].get("must_not_contain", []):
            if item in actual:
                failures.append(f"{case['id']}: forbidden {item}; actual={actual}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"PASS: {len(data['cases'])} PDn consequence-router v2 regression cases")


if __name__ == "__main__":
    main()
