#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "security-knowledge" / "evidence" / "pdn-koap-4-1-3-4-2-mitigation-regression-v1.json"


def mitigation_gate(inp):
    if inp.get("target_part") not in {15, 18}:
        return "UNSUPPORTED_PART"
    if inp.get("conditions_before_decision") is False:
        return "NOT_ELIGIBLE"
    required = [
        "three_years_verified",
        "licenses_verified",
        "compliance_confirmation_verified",
        "aggravating_absent_verified",
        "conditions_before_decision",
    ]
    if not all(inp.get(k) is True for k in required):
        return "NEEDS_EVIDENCE"
    return "ELIGIBLE_FOR_STATUTORY_REDUCTION"


def expense_ratio(inp):
    years = inp.get("years") or []
    if len(years) != 3:
        return "NEEDS_THREE_YEAR_HISTORY"
    if inp.get("licenses_verified") is not True:
        return "NEEDS_LICENSE_EVIDENCE"
    for row in years:
        expense = row.get("expense")
        denominator = row.get("denominator")
        if expense is None or denominator in (None, 0):
            return "NEEDS_DENOMINATOR_EVIDENCE"
        if expense / denominator < 0.001:
            return "BELOW_STATUTORY_RATIO"
    return "VERIFIED"


def ordinary_minimum(target_part, base_amount):
    if target_part == 15:
        floor = 20_000_000
    elif target_part == 18:
        floor = 25_000_000
    else:
        return None
    minimum = max(int(base_amount * 0.01), floor)
    return min(minimum, 500_000_000)


def reduced_fine(inp):
    if inp.get("mitigation_state") != "ELIGIBLE_FOR_STATUTORY_REDUCTION":
        return {"state": "BLOCKED_MITIGATION_EVIDENCE"}
    minimum = ordinary_minimum(inp.get("target_part"), inp.get("base_amount"))
    if minimum is None:
        return {"state": "UNSUPPORTED_PART"}
    amount = minimum // 10
    amount = max(amount, 15_000_000)
    amount = min(amount, 50_000_000)
    return {"state": "STATUTORY_REDUCED_FINE", "amount_rub": amount}


def evaluate(case):
    kind = case.get("type", "mitigation_gate")
    if kind == "mitigation_gate":
        return mitigation_gate(case["input"])
    if kind == "expense_ratio":
        return expense_ratio(case["input"])
    if kind == "reduced_fine":
        return reduced_fine(case["input"])
    raise ValueError(f"unknown fixture type: {kind}")


def main():
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for cid, expected, actual in failures:
            print(f"FAIL {cid}: expected={expected!r}, actual={actual!r}")
        raise SystemExit(1)
    print(f"PASS: {len(data['cases'])} KoAP 4.1 part 3.4-2 mitigation fixtures")


if __name__ == "__main__":
    main()
