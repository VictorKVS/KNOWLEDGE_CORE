import json
from pathlib import Path

FIXTURES = Path('security-knowledge/evidence/nkcki-incident-evidence-node-contract-regression-v1.json')


def evaluate(i):
    if i.get('submission') is False and i.get('delivery') is True:
        return 'INCONSISTENT_EVIDENCE_REQUIRES_REVIEW'
    if i.get('requested_claim') == 'FIELD_LEVEL_COMPLETE':
        if not i.get('exact_schema_hash_bound', False):
            return 'BLOCK_FIELD_LEVEL_COMPLETENESS'
        return 'REQUIRES_FIELD_VALIDATION_NOT_AUTO_PASS'
    if i.get('attack_type_basis') == 'EXAMPLE_THRESHOLD_ONLY':
        return 'DO_NOT_TREAT_AS_NORMATIVE_CLASSIFICATION'
    if i.get('submission') and i.get('supplement'):
        return 'PRESERVE_ORIGINAL_SUBMISSION_TIMESTAMP'
    if 'available_materials_count' in i:
        if i['available_materials_count'] > 0 and i.get('missing_materials_count', 0) > 0:
            return 'SEND_AVAILABLE_MATERIALS'
        if i['available_materials_count'] == 0 and i.get('missing_materials_count', 0) > 0:
            return 'NO_AVAILABLE_MATERIALS_REQUIRES_REVIEW'
    if i.get('submission') and i.get('delivery'):
        if i.get('field_schema_known') is False:
            return 'DELIVERY_CONFIRMED_BUT_COMPLETENESS_UNKNOWN'
        return 'DELIVERY_CONFIRMED'
    if i.get('submission') and not i.get('delivery'):
        if i.get('local_ticket_closed'):
            return 'DELIVERY_STILL_UNCONFIRMED'
        return 'SUBMITTED_WITHOUT_CONFIRMED_DELIVERY'
    if i.get('internal_detection') and not i.get('submission'):
        return 'NOT_REGULATOR_NOTIFIED'
    raise AssertionError(f'Unhandled fixture input: {i}')


def main():
    data = json.loads(FIXTURES.read_text(encoding='utf-8'))
    failures = []
    for case in data['cases']:
        actual = evaluate(case['input'])
        if actual != case['expected']:
            failures.append((case['id'], case['expected'], actual))
    if failures:
        for f in failures:
            print('FAIL', f)
        raise SystemExit(1)
    print(f"PASS {len(data['cases'])} NKTsKI evidence-node regression cases")


if __name__ == '__main__':
    main()
