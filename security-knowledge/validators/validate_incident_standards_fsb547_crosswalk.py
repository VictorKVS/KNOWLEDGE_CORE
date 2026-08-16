import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "security-knowledge/standards/incident-management-fsb547-crosswalk-regression-v1.json"


def route(c):
    s = c.get("standard")
    if s == "ГОСТ Р ИСО/МЭК ТО 18044-2007" and c.get("auto_supersede_by") and not c.get("replacement_evidence"):
        return "BLOCK_AUTO_SUPERSESSION"
    if c.get("fsb547_applicable") == "UNKNOWN":
        return "NEEDS_APPLICABILITY_REVIEW"
    if s == "ГОСТ Р 59548-2022":
        if c.get("requested_output") == "storage_format" and not c.get("clause_evidence"):
            return "BLOCK_FIELD_INVENTION"
        if c.get("requested_output") == "mandatory_event_fields" and not c.get("clause_evidence"):
            return "NEEDS_CLAUSE_EVIDENCE"
        if c.get("local_event_log") and not c.get("delivery_confirmation"):
            return "NOTIFICATION_NOT_PROVEN"
    if c.get("incident_registered") and c.get("outgoing_notification_timestamp") is None:
        return "REGISTRATION_NOT_NOTIFICATION"
    ext = c.get("fsb547_deadline_hours")
    internal = c.get("internal_process_deadline_hours")
    if ext is not None and internal is not None:
        if internal > ext:
            return "INVALID_INTERNAL_EXTENSION"
        return "VALID_STRICTER_INTERNAL_TARGET"
    binding = c.get("binding_edge", False)
    applicable = c.get("fsb547_applicable", False)
    if binding and applicable:
        return "BINDING_STANDARD_PLUS_FSB547_OBLIGATION"
    if binding and not applicable:
        return "BINDING_STANDARD_NO_FSB547_DEADLINE"
    if not binding and applicable:
        return "GUIDANCE_PLUS_FSB547_OBLIGATION"
    return "GUIDANCE_ONLY"


def main():
    data = json.loads(FIX.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        got = route(case)
        if got != case["expected"]:
            failures.append((case["id"], case["expected"], got))
    if failures:
        for f in failures:
            print("FAIL", *f)
        raise SystemExit(1)
    print(f"PASS {len(data['cases'])} incident standards/FSB547 crosswalk cases")


if __name__ == "__main__":
    main()
