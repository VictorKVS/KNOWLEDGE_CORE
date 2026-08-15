import json
from pathlib import Path

FIXTURES = Path('security-knowledge/legal-consequences/pdn-koap-13-11-routing-regression-v1.json')


def route(f):
    r = f.get('route')
    if r in {'13.11.1', '13.11.2', '13.11.6'}:
        cs = f.get('criminal_signs')
        if cs == 'unknown':
            return 'NEEDS_CRIMINAL_SIGNS_REVIEW'
        if cs == 'present':
            return 'CRIMINAL_ROUTE_REVIEW'
    if r == '13.11.3':
        if f.get('biometric_context') is True:
            if f.get('security_measures_missing'):
                return 'KOAP_13_11_3_PART_3'
            if f.get('auth_processing') and f.get('accreditation') in {'absent', 'suspended', 'terminated'}:
                return 'KOAP_13_11_3_PART_4'
        elif f.get('biometric_context') is False:
            return 'NEEDS_APPLICABILITY_REVIEW'
        if f.get('policy_missing'):
            return 'KOAP_13_11_PART_3'
    if r == '13.11.6' and f.get('offline_security_breach'):
        return 'KOAP_13_11_PART_6'
    if r == '13.11.8' and f.get('localization_breach'):
        return 'KOAP_13_11_PART_9' if f.get('repeat') else 'KOAP_13_11_PART_8'
    if r == '272.1':
        if f.get('illegal_resource'):
            return 'UK_272_1_PART_6_REVIEW'
        if f.get('illegal_pdn_computer_info'):
            if f.get('crossborder'):
                return 'UK_272_1_PART_4_REVIEW'
            if f.get('official_position'):
                return 'UK_272_1_PART_3_REVIEW'
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
