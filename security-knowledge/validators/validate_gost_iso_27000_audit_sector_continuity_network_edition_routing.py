#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / 'security-knowledge/standards/gost-iso-27000-audit-sector-continuity-network-edition-routing-v1.yaml'
FIXTURES = ROOT / 'security-knowledge/standards/gost-iso-27000-audit-sector-continuity-network-edition-routing-regression-v1.json'
OBS = ROOT / 'security-knowledge/evidence/gost-iso-27000-audit-sector-continuity-network-edition-routing-observation-2026-09-02.yaml'
MASTER = ROOT / 'security-knowledge/corpus/master-source-inventory.yaml'

model = json.loads(MODEL.read_text(encoding='utf-8'))
fixtures = json.loads(FIXTURES.read_text(encoding='utf-8'))
obs = json.loads(OBS.read_text(encoding='utf-8'))
master = MASTER.read_text(encoding='utf-8')

assert model['id'] == fixtures['model_id'] == obs['model_id']
assert len(model['standards']) == model['counts']['selected_standards'] == 6
assert sum(not x['divergence'].startswith('ALIGNED_') for x in model['standards']) == 4
assert sum(x['divergence'].startswith('ALIGNED_') for x in model['standards']) == 2
assert sum('AMENDMENT_1_2021_NOT_ADOPTED' in x['divergence'] for x in model['standards']) == 1
assert [x['order'] for x in model['decision_gates']] == list(range(1, 9))
assert len(model['scenarios']) == 8
assert len(model['red_team_attacks']) == 12 and all(x['result'] == 'BLOCKED' for x in model['red_team_attacks'])
assert len(model['evidence_artifacts']) == len(model['evidence_nodes']) == len(obs['evidence_nodes']) == 18
assert len(model['control_rules']) == len(fixtures['cases']) == 64
assert {x['id'] for x in model['control_rules']} == {x['rule_id'] for x in fixtures['cases']}
assert all(model['boundaries'].values())
for key, value in fixtures['expected_counts'].items():
    assert model['counts'][key] == value
actual = {x['id']: x['rule'] for x in model['control_rules']}
for case in fixtures['cases']:
    assert actual[case['rule_id']] == case['expected']
for path in (MODEL, FIXTURES, OBS):
    assert str(path.relative_to(ROOT)) in master
print('PASS: 6 selected routes; 4 edition/amendment divergences; 64/64 rules/cases; red-team 12/12; evidence 18/18')
