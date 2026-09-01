#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
M=ROOT/'security-knowledge/classification/kii-science-pp246-clause-routing-v1.yaml'
R=ROOT/'security-knowledge/classification/kii-science-pp246-clause-routing-regression-v1.json'
O=ROOT/'security-knowledge/evidence/kii-science-pp246-observation-2026-09-01.yaml'
I=ROOT/'security-knowledge/corpus/master-source-inventory.yaml'
m=json.loads(M.read_text(encoding='utf-8')); r=json.loads(R.read_text(encoding='utf-8')); o=json.loads(O.read_text(encoding='utf-8')); inv=I.read_text(encoding='utf-8')
assert m['id']==r['model_id']==o['model_id']
assert len(m['clauses'])==21 and [x['id'] for x in m['clauses']]==[f'P{i}' for i in range(1,22)]
assert m['temporal']['effective_from']=='2026-03-15'
assert [x['position'] for x in m['pp127_indicator_routes']]==['1','7','9','11','13.1']
assert m['ugt_gate']['threshold']=='NOT_BELOW_7'
assert m['formulas']==[] and m['formula_status'].startswith('NO_STANDALONE')
assert m['preserved_pdf']['sha256']==o['source_boundary']['preserved_pdf_sha256']
assert o['source_boundary']['immutable_primary_pdf_hash']=='PENDING_OFFICIAL_TRANSPORT'
assert len(m['decision_gates'])==len(m['scenarios'])==8
assert len(m['red_team_attacks'])==12 and all(x['blocked'] for x in m['red_team_attacks'])
assert len(m['evidence_nodes'])==len(o['claims'])==18
assert len(m['control_rules'])==len(r['cases'])==64
assert {x['id'] for x in m['control_rules']}=={x['rule_id'] for x in r['cases']}
assert all(x['expected']=='BLOCKED' for x in r['adversarial_cases']) and all(m['boundaries'].values())
for k,v in r['expected_counts'].items(): assert m['counts'][k]==v
for marker in ['KII_SCIENCE_PP246_CLAUSE_ROUTING','kii-science-pp246-clause-routing-v1.yaml','kii-science-pp246-clause-routing-regression-v1.json']: assert marker in inv
print('PASS: PP246 points 1-21, 5 conditional indicator routes, UGT7 gate, no invented formulas, 8 gates/scenarios, 18 evidence nodes, 12/12 attacks, 64/64 rules/cases; official primary hash pending')

