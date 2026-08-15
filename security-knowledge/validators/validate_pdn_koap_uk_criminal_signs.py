#!/usr/bin/env python3
import json
from pathlib import Path

FIXTURES = Path('security-knowledge/legal-consequences/pdn-koap-uk-criminal-signs-regression-v1.yaml')

EXCLUSION_ROUTES = {'13.11(12)', '13.11(13)', '13.11(14)', '13.11(16)', '13.11(17)'}
RECURRENCE_ROUTES = {'13.11(15)', '13.11(18)'}
ADMIN_ROUTES = {
    '13.11(10)', '13.11(11)', '13.11(12)', '13.11(13)', '13.11(14)',
    '13.11(15)', '13.11(16)', '13.11(17)', '13.11(18)'
}


def route(case):
    data = case['input']
    target = data.get('route')
    criminal = data.get('criminal_signs')

    if target == 'UK272.1':
        if not data.get('computer_pd'):
            return 'NEEDS_FACTS'
        if data.get('illegal_source_or_access') != 'confirmed':
            return 'NEEDS_FACTS'
        return 'NEEDS_CRIMINAL_LAW_REVIEW'

    if target not in ADMIN_ROUTES:
        return 'OUT_OF_SCOPE'

    if target in EXCLUSION_ROUTES and criminal in {'unknown', 'possible', 'confirmed'}:
        return 'NEEDS_CRIMINAL_LAW_REVIEW'

    if target in RECURRENCE_ROUTES and data.get('prior_admin_punishment') != 'confirmed':
        return 'NEEDS_RECURRENCE_EVIDENCE'

    if target == '13.11(17)' and data.get('article_13_11_3_scope') == 'unknown':
        return 'NEEDS_BIOMETRIC_SCOPE_REVIEW'

    return 'ADMIN_ROUTE_AVAILABLE'


def main():
    suite = json.loads(FIXTURES.read_text(encoding='utf-8'))
    failures = []
    for case in suite['cases']:
        actual = route(case)
        if actual != case['expected']:
            failures.append((case['id'], case['expected'], actual))
    if failures:
        for cid, expected, actual in failures:
            print(f'FAIL {cid}: expected={expected} actual={actual}')
        raise SystemExit(1)
    print(f"PASS {len(suite['cases'])} PDn KoAP/UK criminal-signs routing cases")


if __name__ == '__main__':
    main()
