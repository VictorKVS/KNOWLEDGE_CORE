import json
import sys
from pathlib import Path

CANONICAL = {
    "539": ("84782", "0001202512260014"),
    "546": ("84870", "0001202512300066"),
    "547": ("84871", "0001202512300064"),
    "548": ("84872", "0001202512300058"),
    "553": ("84873", "0001202512300059"),
    "554": ("84874", "0001202512300063"),
}


def classify(case: dict) -> str:
    expected = CANONICAL.get(case["order_number"])
    if expected is None:
        return "UNKNOWN"
    registration, publication = expected
    if (
        case["registration_number"] == registration
        and case["publication_number"] == publication
    ):
        return "PASS"
    return "FAIL"


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

    print(f"PASS {len(data['cases'])} FSB/GosSOPKA publication-anchor cases")


if __name__ == "__main__":
    main(sys.argv[1])
