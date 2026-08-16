import json
import sys
from pathlib import Path


def classify(case: dict) -> str:
    if not case["facts_complete"]:
        return "NOT_PROVEN"

    if not case["protected_cii_information"]:
        return "OUTSIDE_ARTICLE_274_1_PROVEN_SCOPE"

    harmful_result = any(
        case[name]
        for name in ("destruction", "blocking", "modification", "copying")
    )

    part2_actor = case["unlawful_access"] or case["malware_for_cii_impact"]
    part3_actor = case["rules_violation"]

    if not part2_actor and not part3_actor:
        if harmful_result:
            return "ELEMENTS_NOT_COMPLETE"
        return "NO_ARTICLE_274_1_TRIGGER_FACTS"

    if not harmful_result:
        return "ELEMENTS_NOT_COMPLETE"

    if part2_actor and part3_actor:
        return "MULTIPLE_POTENTIAL_ROUTES_REQUIRE_LEGAL_ASSESSMENT"
    if part2_actor:
        return "POTENTIAL_PART_2_REQUIRES_LEGAL_ASSESSMENT"
    if part3_actor:
        return "POTENTIAL_PART_3_REQUIRES_LEGAL_ASSESSMENT"

    return "NOT_PROVEN"


def main(path: str) -> None:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = classify(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))

    if failures:
        for case_id, expected, actual in failures:
            print(f"FAIL {case_id}: expected={expected} actual={actual}")
        raise SystemExit(1)

    print(f"PASS {len(data['cases'])} UK 274.1 consequence-routing cases")


if __name__ == "__main__":
    main(sys.argv[1])
