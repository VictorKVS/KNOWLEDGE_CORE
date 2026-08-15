import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "security-knowledge" / "legal-consequences" / "pdn-incident-consequence-router-regression-v1.json"


def route(f):
    out = []
    if not f.get("personal_data_involved", False):
        return ["NOT_APPLICABLE_PDN_ROUTER"]
    if f.get("event_date", "MISSING") is None:
        out.append("NEEDS_EVENT_DATE")

    gated_admin_fact = any([
        f.get("processing_without_legal_basis"),
        f.get("written_consent_required_and_missing"),
        f.get("nonautomated_media_security_failure"),
    ])
    uk_fact = f.get("unlawfully_obtained_personal_data") and f.get("unlawful_use_transfer_collection_storage")

    if gated_admin_fact and not f.get("criminal_signs_assessed", False):
        out.append("NEEDS_CRIMINAL_SIGNS_REVIEW")
    elif f.get("criminal_signs_assessed", False) and f.get("criminal_signs_present", False) and uk_fact:
        out.append("ROUTE_UK_272_1_REVIEW")
    elif f.get("criminal_signs_assessed", False) and not f.get("criminal_signs_present", False) and gated_admin_fact:
        out.append("ROUTE_ADMINISTRATIVE_REVIEW")

    # Large/special/biometric breach facts are not enough by themselves for UK 272.1.
    if (f.get("breach_or_leak") and (f.get("special_category_data") or f.get("biometric_data"))) and not f.get("criminal_signs_assessed", False):
        if "NEEDS_CRIMINAL_SIGNS_REVIEW" not in out:
            out.append("NEEDS_CRIMINAL_SIGNS_REVIEW")

    if f.get("biometric_ebs_context") and f.get("biometric_security_failure"):
        out.append("ROUTE_ADMINISTRATIVE_REVIEW")

    if f.get("subject_rights_harm") or f.get("property_damage"):
        out.append("ROUTE_CIVIL_REVIEW")

    if f.get("employee_action_in_course_of_duties"):
        ready = all([
            f.get("employee_duty_defined"),
            f.get("employee_breach_proven"),
            f.get("employee_fault_proven"),
            f.get("written_explanation_requested"),
        ])
        out.append("DISCIPLINARY_REVIEW_READY" if ready else "NEEDS_EMPLOYEE_DUTY_FACT_FAULT_AND_PROCEDURE")

    if f.get("employer_seeks_recovery_from_employee"):
        if f.get("direct_actual_damage") and f.get("full_material_liability_ground"):
            out.append("MATERIAL_LIABILITY_REVIEW_READY")
        else:
            out.append("NEEDS_DIRECT_ACTUAL_DAMAGE_AND_LIABILITY_GROUND")

    substantive = [x for x in out if x not in {"NEEDS_EVENT_DATE"}]
    if not substantive:
        out.append("NEEDS_FACTS")
    return list(dict.fromkeys(out))


def main():
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = route(case["facts"])
        expected = case["expected"]
        for item in expected.get("contains", []):
            if item not in actual:
                failures.append(f"{case['id']}: missing {item}; actual={actual}")
        for item in expected.get("must_not_contain", []):
            if item in actual:
                failures.append(f"{case['id']}: forbidden {item}; actual={actual}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"PASS: {len(data['cases'])} PDn consequence-router regression cases")


if __name__ == "__main__":
    main()
