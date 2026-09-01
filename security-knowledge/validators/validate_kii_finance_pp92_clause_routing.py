#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
M=ROOT/'security-knowledge/classification/kii-finance-pp92-clause-routing-v1.yaml'; R=ROOT/'security-knowledge/classification/kii-finance-pp92-clause-routing-regression-v1.json'; O=ROOT/'security-knowledge/evidence/kii-finance-pp92-observation-2026-09-01.yaml'; I=ROOT/'security-knowledge/corpus/master-source-inventory.yaml'
m=json.loads(M.read_text(encoding='utf-8')); r=json.loads(R.read_text(encoding='utf-8')); o=json.loads(O.read_text(encoding='utf-8')); inv=I.read_text(encoding='utf-8')
assert m['id']==r['model_id']==o['model_id']
assert len(m['clauses'])==55 and [x['id'] for x in m['clauses']]==[f'P{i}' for i in range(1,56)]
assert m['temporal']['effective_from']=='2026-02-15'
assert len(m['indicator_routes'])==21 and m['indicator_routes'][0]['pp127_positions']==['9']
assert m['deadlines'][0]['limit']=='10_WORKING_DAYS_FROM_RECEIPT'
assert m['deadlines'][1]['limit']=='NO_LATER_THAN_TENTH_WORKING_DAY_OF_CALENDAR_YEAR'
assert set(m['recipients'])=={'MINFIN','BANK_OF_RUSSIA','guard'}
assert m['formula_status']['state']=='VERIFIED_VISUAL_TRANSCRIPTION_PRESERVED_PDF_PRIMARY_HASH_PENDING'
expected_formulas={
41:'P9 = (Pavg/(365*24) * Cmax/D + 0.2*U/D) * 100',42:'Pavg = (SUM_i^n Si)/n',
47:'K10 = Qo/365',48:'K10^1 = Ao/365',49:'K10^2 = Qo/365',
50:'K10^3 = PA_npf + PR_npf',51:'K10^4 = Va',52:'K10^5 = Qc',53:'K10^6 = VL',54:'K10^7 = Qch'}
assert {x['point']:x['formula'] for x in m['formula_status']['transcriptions']}==expected_formulas
assert {x['point']:x['formula'] for x in r['formula_expectations']}==expected_formulas
assert m['formula_status']['transcriptions'][1]['lower_index_guard']=='printed i; do not add =1'
assert o['source_boundary']['immutable_primary_pdf_hash']=='PENDING_OFFICIAL_TRANSPORT'
assert len(m['decision_gates'])==len(m['scenarios'])==8
assert len(m['red_team_attacks'])==12 and all(x['blocked'] for x in m['red_team_attacks'])
assert len(m['evidence_nodes'])==len(o['claims'])==18
assert len(m['control_rules'])==len(r['cases'])==64
assert {x['id'] for x in m['control_rules']}=={x['rule_id'] for x in r['cases']}
assert all(x['expected']=='BLOCKED' for x in r['adversarial_cases']) and all(m['boundaries'].values())
for k,v in r['expected_counts'].items(): assert m['counts'][k]==v
for marker in ['KII_FINANCE_PP92_CLAUSE_ROUTING','kii-finance-pp92-clause-routing-v1.yaml','kii-finance-pp92-clause-routing-regression-v1.json']: assert marker in inv
print('PASS: PP92 points 1-55, 21 indicator routes, 10 formulas visually transcribed, 2 deadlines/2 recipients, 8 gates/scenarios, 18 evidence nodes, 12/12 attacks, 64/64 rules/cases; primary PDF hash pending')
