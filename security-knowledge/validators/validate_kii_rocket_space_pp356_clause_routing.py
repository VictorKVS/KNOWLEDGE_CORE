#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
M=ROOT/'security-knowledge/classification/kii-rocket-space-pp356-clause-routing-v1.yaml'
R=ROOT/'security-knowledge/classification/kii-rocket-space-pp356-clause-routing-regression-v1.json'
O=ROOT/'security-knowledge/evidence/kii-rocket-space-pp356-observation-2026-09-01.yaml'
I=ROOT/'security-knowledge/corpus/master-source-inventory.yaml'
m=json.loads(M.read_text(encoding='utf-8')); r=json.loads(R.read_text(encoding='utf-8')); o=json.loads(O.read_text(encoding='utf-8')); inv=I.read_text(encoding='utf-8')
assert m['id']==r['model_id']==o['model_id']
assert len(m['clauses'])==15 and [x['id'] for x in m['clauses']]==[f'P{i}' for i in range(1,16)]
assert m['temporal']['effective_from']=='2026-04-09'
assert [x['position'] for x in m['pp127_indicator_routes']]==['1','8','9','11','13','13.1']
assert m['pp127_indicator_routes'][4]['calculation']==m['pp127_indicator_routes'][5]['calculation']=='DELEGATED_TO_DEFENSE_INDUSTRY_SECTOR_FEATURES'
assert len(m['formulas'])==4
assert [x['period'] for x in m['formulas']]==['previous five-year average','previous five-year average','previous three-year average','previous three-year average']
assert all('Rгод' in x['printed'] for x in m['formulas'])
assert 'tустр − tрегл' in m['formulas'][1]['printed'] and 'tустр − tрегл' in m['formulas'][3]['printed']
assert 'use tрегл' in m['formulas'][1]['negative_difference_rule'] and 'use tрегл' in m['formulas'][3]['negative_difference_rule']
assert m['preserved_pdf']['sha256']==o['source_boundary']['preserved_pdf_sha256']
assert o['source_boundary']['official_transport_response']=='HTTP_502_HTML_NOT_PDF'
assert o['source_boundary']['immutable_primary_pdf_hash']=='PENDING_OFFICIAL_TRANSPORT'
assert len(m['decision_gates'])==len(m['scenarios'])==8
assert len(m['red_team_attacks'])==12 and all(x['blocked'] for x in m['red_team_attacks'])
assert len(m['evidence_nodes'])==len(o['claims'])==18
assert len(m['control_rule_matrix']['gates'])*len(m['control_rule_matrix']['checks_per_gate'])==64
assert len(r['case_matrix']['gate_ids'])*len(r['case_matrix']['case_kinds'])==64
assert all(x['expected']=='BLOCKED' for x in r['adversarial_cases']) and all(m['boundaries'].values())
for k,v in r['expected_counts'].items(): assert m['counts'][k]==v
for marker in ['KII_ROCKET_SPACE_PP356_CLAUSE_ROUTING','kii-rocket-space-pp356-clause-routing-v1.yaml','kii-rocket-space-pp356-clause-routing-regression-v1.json']: assert marker in inv
print('PASS: PP356 points 1-15, 6 indicator routes, 4 formula occurrences, 5y/3y periods, PP796 delegation, 8 gates/scenarios, 18 evidence nodes, 12/12 attacks, 64/64 matrix rules/cases; official primary hash pending')
