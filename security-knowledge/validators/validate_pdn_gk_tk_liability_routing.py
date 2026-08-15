import json
from pathlib import Path

FIXTURES = Path('security-knowledge/legal-consequences/pdn-gk-tk-liability-routing-regression-v1.json')


def route(f):
    if f.get('regulator_notification_due') and f.get('disciplinary_action'):
        return 'REGULATOR_CLOCK_INDEPENDENT_DISCIPLINE_PENDING'

    if f.get('pdn_rights_violation') and f.get('moral_harm_claim'):
        return 'CIVIL_MORAL_HARM_REVIEW'

    if f.get('employee_caused_harm') and f.get('in_course_of_duties'):
        return 'EMPLOYER_CIVIL_LIABILITY_REVIEW'

    if f.get('property_damage'):
        return 'CIVIL_DAMAGE_REVIEW'

    if f.get('disciplinary_action'):
        if not f.get('assigned_duty') or not f.get('fault_proven'):
            return 'NEEDS_DUTY_AND_FAULT_PROOF'
        if not f.get('written_explanation_requested'):
            return 'NEEDS_DISCIPLINARY_PROCEDURE'
        if f.get('disciplinary_month_deadline_ok') is False:
            return 'DISCIPLINARY_DEADLINE_REVIEW'
        return 'DISCIPLINARY_SANCTION_REVIEW'

    if f.get('employee_recovery'):
        if f.get('lost_profit_only'):
            return 'NOT_RECOVERABLE_AS_EMPLOYEE_MATERIAL_DAMAGE'
        if not f.get('direct_actual_damage_proven'):
            return 'NEEDS_DIRECT_ACTUAL_DAMAGE_PROOF'
        if f.get('org_fine_only') and not f.get('full_liability_ground'):
            return 'NEEDS_DAMAGE_CAUSATION_REVIEW'
        if not f.get('full_liability_ground'):
            return 'LIMITED_MATERIAL_LIABILITY'
        gt = f.get('ground_type')
        if gt == 'administrative_offense' and not f.get('administrative_offense_established'):
            return 'NEEDS_FULL_LIABILITY_GROUND_PROOF'
        if gt == 'crime' and not f.get('court_judgment_established'):
            return 'NEEDS_FULL_LIABILITY_GROUND_PROOF'
        return 'FULL_MATERIAL_LIABILITY_REVIEW'

    return 'NEEDS_LEGAL_REVIEW'


def main():
    data = json.loads(FIXTURES.read_text(encoding='utf-8'))
    failed = []
    for case in data['cases']:
        actual = route(case['facts'])
        if actual != case['expected']:
            failed.append((case['id'], case['expected'], actual))
    if failed:
        for row in failed:
            print('FAIL', *row)
        raise SystemExit(1)
    print(f"PASS {len(data['cases'])} cases")


if __name__ == '__main__':
    main()
