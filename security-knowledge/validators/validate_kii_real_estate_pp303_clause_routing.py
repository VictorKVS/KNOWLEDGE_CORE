#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
M=ROOT/'security-knowledge/classification/kii-real-estate-pp303-clause-routing-v1.yaml'
R=ROOT/'security-knowledge/classification/kii-real-estate-pp303-clause-routing-regression-v1.json'
O=ROOT/'security-knowledge/evidence/kii-real-estate-pp303-observation-2026-09-01.yaml'
I=ROOT/'security-knowledge/corpus/master-source-inventory.yaml'
m=json.loads(M.read_text(encoding='utf-8')); r=json.loads(R.read_text(encoding='utf-8')); o=json.loads(O.read_text(encoding='utf-8')); inv=I.read_text(encoding='utf-8')
assert m['id']==r['model_id']==o['model_id']
assert len(m['clauses'])==14 and [x['id'] for x in m['clauses']]==[f'P{i}' for i in range(1,15)]
assert m['temporal']['effective_from']=='2026-04-01'
assert m['subject_scope']['included']==['Federal Service for State Registration, Cadastre and Cartography (Rosreestr)','public-law company Roskadastr']
assert [x['pp127_position'] for x in m['pp127_indicator_routes']]==['5(a)','5(b)','6','9']
assert len(m['formulas'])==3
assert 'Тпу − Тпростоя' in m['formulas'][0]['printed'] and '/ Тпу' in m['formulas'][0]['printed']
assert m['formulas'][0]['mandatory_post_rule']=='THIS_VALUE_IS_ACCEPTED_EQUAL_TO_INDICATOR_1'
assert 'ΔДБ / Бср' in m['formulas'][1]['printed'] and 'ГУ / 365 суток' in m['formulas'][2]['printed']
assert m['preserved_pdf']['sha256']==o['source_boundary']['preserved_pdf_sha256']
assert o['source_boundary']['immutable_primary_pdf_hash']=='PENDING_OFFICIAL_TRANSPORT'
assert len(m['decision_gates'])==len(m['scenarios'])==8
assert len(m['red_team_attacks'])==12 and all(x['blocked'] for x in m['red_team_attacks'])
assert len(m['evidence_nodes'])==len(o['claims'])==18
assert len(m['control_rule_matrix']['gates'])*len(m['control_rule_matrix']['checks_per_gate'])==64
assert len(r['case_matrix']['gate_ids'])*len(r['case_matrix']['case_kinds'])==64
assert all(x['expected']=='BLOCKED' for x in r['adversarial_cases']) and all(m['boundaries'].values())
for k,v in r['expected_counts'].items(): assert m['counts'][k]==v
for marker in ['KII_REAL_ESTATE_PP303_CLAUSE_ROUTING','kii-real-estate-pp303-clause-routing-v1.yaml','kii-real-estate-pp303-clause-routing-regression-v1.json']: assert marker in inv
print('PASS: PP303 points 1-14, 4 indicator routes, 3 formulas, point-11 equality, 8 gates/scenarios, 18 evidence nodes, 12/12 attacks, 64/64 matrix rules/cases; official primary hash pending')
