#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / 'security-knowledge/standards/gost-iso-27000-digital-redaction-storage-ediscovery-routing-v1.yaml'
FIXTURES = ROOT / 'security-knowledge/standards/gost-iso-27000-digital-redaction-storage-ediscovery-routing-regression-v1.json'
OBS = ROOT / 'security-knowledge/evidence/gost-iso-27000-digital-redaction-storage-ediscovery-routing-observation-2026-09-02.yaml'
MASTER = ROOT / 'security-knowledge/corpus/master-source-inventory.yaml'

model = json.loads(MODEL.read_text(encoding='utf-8'))
fixtures = json.loads(FIXTURES.read_text(encoding='utf-8'))
obs = json.loads(OBS.read_text(encoding='utf-8'))
master = MASTER.read_text(encoding='utf-8')

assert model['id'] == fixtures['model_id'] == obs['model_id']
assert len(model['routes']) == model['counts']['selected_routes'] == 5
assert sum(x['jurisdiction'] == 'RU_NATIONAL' for x in model['routes']) == model['counts']['ru_national_routes'] == 2
assert sum(x['jurisdiction'] == 'INTERNATIONAL_ONLY_IN_THIS_MODEL' for x in model['routes']) == model['counts']['international_only_routes'] == 3
assert [x['order'] for x in model['decision_gates']] == list(range(1, 9))
assert len(model['scenarios']) == 8
assert len(model['red_team_attacks']) == 12 and all(x['result'] == 'BLOCKED' for x in model['red_team_attacks'])
assert len(model['evidence_artifacts']) == len(model['evidence_nodes']) == len(obs['evidence_nodes']) == 18
assert len(model['control_rules']) == len(fixtures['cases']) == 64
assert {x['id'] for x in model['control_rules']} == {x['rule_id'] for x in fixtures['cases']}
assert all(model['boundaries'].values())
for key, value in fixtures['expected_counts'].items():
    assert model['counts'][key] == value

routes = {x['id']: x for x in model['routes']}
assert routes['GOST_R_ISO_IEC_27038_2016']['national_source_iso'] == 'ISO/IEC 27038:2014'
assert routes['GOST_R_ISO_IEC_27038_2016']['scope_boundary'] == 'DIGITAL_DOCUMENTS_ONLY_DATABASE_REDACTION_EXCLUDED'
assert routes['ISO_IEC_27040_2024']['predecessor'] == 'ISO/IEC 27040:2015'
assert routes['GOST_R_ISO_IEC_27050_1_2019']['national_source_iso'] == 'ISO/IEC 27050-1:2016'
assert routes['GOST_R_ISO_IEC_27050_1_2019']['current_international'] == 'ISO/IEC 27050-1:2019'
assert routes['ISO_IEC_27050_2_2018']['national_status'].startswith('PENDING_')
assert routes['ISO_IEC_27050_3_2020']['predecessor'] == 'ISO/IEC 27050-3:2017'

actual = {x['id']: x['rule'] for x in model['control_rules']}
for case in fixtures['cases']:
    assert actual[case['rule_id']] == case['expected']
assert len(fixtures['adversarial_cases']) == 12 and all(x['expect'] == 'BLOCKED' for x in fixtures['adversarial_cases'])
for path in (MODEL, FIXTURES, OBS):
    assert str(path.relative_to(ROOT)) in master
print('PASS: 5 routes; 2 Russian and 3 ISO-only; 1 national edition divergence; 2 international replacements; 64/64 rules/cases; red-team 12/12; evidence 18/18')
