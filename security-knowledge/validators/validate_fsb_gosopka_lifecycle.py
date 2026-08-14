#!/usr/bin/env python3
from datetime import date
from pathlib import Path
import re
import sys

EFFECTIVE_FROM = {
    539: date(2026, 1, 30),
    546: date(2026, 1, 30),
    547: date(2026, 1, 30),
    548: date(2026, 1, 30),
    553: date(2026, 1, 10),
    554: date(2026, 1, 10),
}

FIXTURE = Path(__file__).resolve().parents[1] / "roles-deadlines-responsibility" / "fsb-gosopka-lifecycle-regression-v1.yaml"


def parse_cases(text: str):
    chunks = re.split(r"\n\s*- id: ", text)[1:]
    for chunk in chunks:
        cid = chunk.splitlines()[0].strip()
        d = re.search(r'event_date:\s*"([0-9-]+)"', chunk)
        act = re.search(r'act:\s*(\d+)', chunk)
        expected = re.search(r'expected_state:\s*([A-Z_]+)', chunk)
        if not (d and act and expected):
            raise ValueError(f"Malformed fixture: {cid}")
        yield cid, date.fromisoformat(d.group(1)), int(act.group(1)), expected.group(1)


def resolve_state(event_date: date, act: int) -> str:
    if act not in EFFECTIVE_FROM:
        return "UNKNOWN_ACT_FAIL_CLOSED"
    return "EFFECTIVE" if event_date >= EFFECTIVE_FROM[act] else "NOT_EFFECTIVE"


def main() -> int:
    text = FIXTURE.read_text(encoding="utf-8")
    failures = []
    count = 0
    for cid, event_date, act, expected in parse_cases(text):
        count += 1
        actual = resolve_state(event_date, act)
        if actual != expected:
            failures.append((cid, expected, actual))
    if failures:
        for cid, expected, actual in failures:
            print(f"FAIL {cid}: expected={expected} actual={actual}")
        return 1
    print(f"PASS: {count} FSB GosSOPKA lifecycle regression cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
