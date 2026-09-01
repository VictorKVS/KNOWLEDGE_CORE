#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
M=ROOT/'security-knowledge/classification/kii-atomic-pp4-clause-routing-v1.yaml'; R=ROOT/'security-knowledge/classification/kii-atomic-pp4-clause-routing-regression-v1.json'; O=ROOT/'security-knowledge/evidence/kii-atomic-pp4-observation-2026-09-01.yaml'; I=ROOT/'security-knowledge/corpus/master-source-inventory.yaml'
m=json.loads(M.read_text(encoding='utf-8')); r=json.loads(R.read_text(encoding='utf-8')); o=json.loads(O.read_text(encoding='utf-8')); inv=I.read_text(encoding='utf-8')
assert m['id']==r['model_id']==o['model_id']
assert len(m['clauses'])==23 and [x['id'] for x in m['clauses']]==[f'P{i}' for i in range(1,24)]
assert m['temporal']['effective_from']=='2026-01-24'
assert m['excluded_pp127_positions']==['4','10','10.1','10.2','10.3','10.4','10.5','10.6','10.7','14']
assert len(m['indicator_routes'])==6 and len(m['methods'])==4
assert m['formulas'][0]['formula']=='P8 = delta_D / D_avg * 100'
assert m['formulas'][1]['formula']=='P9 = delta_FB / B_avg * 100'
assert m['preserved_pdf']['sha256']==o['source_boundary']['preserved_pdf_sha256']
assert o['source_boundary']['immutable_primary_pdf_hash']=='PENDING_OFFICIAL_TRANSPORT'
assert len(m['decision_gates'])==len(m['scenarios'])==8
assert len(m['red_team_attacks'])==12 and all(x['blocked'] for x in m['red_team_attacks'])
assert len(m['evidence_nodes'])==len(o['claims'])==18
assert len(m['control_rules'])==len(r['cases'])==64
assert {x['id'] for x in m['control_rules']}=={x['rule_id'] for x in r['cases']}
assert all(x['expected']=='BLOCKED' for x in r['adversarial_cases']) and all(m['boundaries'].values())
for k,v in r['expected_counts'].items(): assert m['counts'][k]==v
for marker in ['KII_ATOMIC_PP4_CLAUSE_ROUTING','kii-atomic-pp4-clause-routing-v1.yaml','kii-atomic-pp4-clause-routing-regression-v1.json']: assert marker in inv
print('PASS: PP4 points 1-23, 6 indicator routes, 10 exclusions, 4 methods, 2 formulas, 8 gates/scenarios, 18 evidence nodes, 12/12 attacks, 64/64 rules/cases; official primary hash pending')
