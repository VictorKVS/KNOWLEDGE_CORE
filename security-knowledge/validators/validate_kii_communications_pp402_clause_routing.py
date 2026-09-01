#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
M=ROOT/'security-knowledge/classification/kii-communications-pp402-clause-routing-v1.yaml'; R=ROOT/'security-knowledge/classification/kii-communications-pp402-clause-routing-regression-v1.json'; O=ROOT/'security-knowledge/evidence/kii-communications-pp402-observation-2026-09-01.yaml'; I=ROOT/'security-knowledge/corpus/master-source-inventory.yaml'
m=json.loads(M.read_text(encoding='utf-8')); r=json.loads(R.read_text(encoding='utf-8')); o=json.loads(O.read_text(encoding='utf-8')); inv=I.read_text(encoding='utf-8')
assert m['id']==r['model_id']==o['model_id']
assert len(m['clauses'])==19 and [x['id'] for x in m['clauses']]==[f'P{i}' for i in range(1,20)]
assert m['temporal']['effective_from']=='2026-09-01' and m['temporal']['end_boundary_inclusivity']=='NOT_INFERRED'
assert len(m['indicator_applicability_matrix'])==5
assert {x['indicator'] for x in m['indicator_applicability_matrix']}=={'PP127_POSITION_4A','PP127_POSITION_4B','PP127_POSITION_6','PP127_POSITION_8','PP127_POSITION_9'}
assert all(x['state']=='PENDING_PRIMARY_PDF_FORMULA_TRANSCRIPTION' for x in m['formula_status'].values() if isinstance(x,dict))
assert m['point17_recovery_fallback']['documents_and_statistics_absent']=='USE_10_DAYS'
assert len(m['decision_gates'])==len(m['scenarios'])==8
assert len(m['red_team_attacks'])==12 and all(x['blocked'] for x in m['red_team_attacks'])
assert len(m['evidence_nodes'])==len(o['claims'])==18
assert len(m['control_rules'])==len(r['cases'])==64
assert {x['id'] for x in m['control_rules']}=={x['rule_id'] for x in r['cases']}
assert all(x['expected']=='BLOCKED' for x in r['adversarial_cases']) and all(m['boundaries'].values())
for k,v in r['expected_counts'].items(): assert m['counts'][k]==v
for marker in ['KII_COMMUNICATIONS_PP402_CLAUSE_ROUTING','kii-communications-pp402-clause-routing-v1.yaml','kii-communications-pp402-clause-routing-regression-v1.json']: assert marker in inv
print('PASS: PP402 points 1-19, 5 indicator routes, 8 gates/scenarios, 18 evidence nodes, 12/12 attacks, 64/64 rules/cases; formulas fail closed')
