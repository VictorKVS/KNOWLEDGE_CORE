#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
M=ROOT/'security-knowledge/classification/kii-defense-industry-pp796-clause-routing-v1.yaml'
R=ROOT/'security-knowledge/classification/kii-defense-industry-pp796-clause-routing-regression-v1.json'
O=ROOT/'security-knowledge/evidence/kii-defense-industry-pp796-observation-2026-09-01.yaml'
I=ROOT/'security-knowledge/corpus/master-source-inventory.yaml'
m=json.loads(M.read_text(encoding='utf-8')); r=json.loads(R.read_text(encoding='utf-8')); o=json.loads(O.read_text(encoding='utf-8')); inv=I.read_text(encoding='utf-8')
assert m['id']==r['model_id']==o['model_id']
assert len(m['clauses'])==40 and [x['id'] for x in m['clauses']]==[f'P{i}' for i in range(1,41)]
assert m['temporal']['published']=='2026-06-29' and m['temporal']['effective_from']=='2026-07-07'
positions=['1','2','3','4','6','7','8','9','10','10.1','10.2','10.3','10.4','10.5','10.6','10.7','11','12','13','13.1']
assert [x['position'] for x in m['pp127_indicator_routes']]==positions and '5' not in positions
assert m['pp127_indicator_routes'][2]['calculation']=='DELEGATED_TRANSPORT_FEATURES_PENDING_ADOPTED_ACT'
assert m['pp127_indicator_routes'][3]['calculation']=='DELEGATED_PP402'
assert all(x['calculation']=='DELEGATED_PP92' for x in m['pp127_indicator_routes'][8:16])
assert len(m['formulas'])==15 and m['formulas'][6]['printed']=='Nуср = (Σ[i=1..n+2] N_i) / b'
assert m['formulas'][6]['integrity_state']=='PRINTED_EXACTLY_SEMANTIC_CONSISTENCY_PENDING_NO_SILENT_REPAIR'
assert m['formula_guards'][0]['effect']=='STOP_POINT_34_CALCULATION' and m['formula_guards'][1]['effect']=='DO_NOT_CALCULATE_POINTS_37_AND_38'
assert m['preserved_pdf']['sha256']==o['source_boundary']['preserved_pdf_sha256']
assert m['preserved_pdf']['pages']==16 and m['preserved_pdf']['text_layer']=='ABSENT'
assert o['source_boundary']['official_transport_response']=='HTTP_502_HTML_NOT_PDF'
assert o['source_boundary']['immutable_primary_pdf_hash']=='PENDING_OFFICIAL_TRANSPORT'
assert len(m['decision_gates'])==len(m['scenarios'])==8
assert len(m['red_team_attacks'])==12 and all(x['blocked'] for x in m['red_team_attacks'])
assert len(m['evidence_nodes'])==len(o['claims'])==18
assert len(m['control_rule_matrix']['gates'])*len(m['control_rule_matrix']['checks_per_gate'])==64
assert len(r['case_matrix']['gate_ids'])*len(r['case_matrix']['case_kinds'])==64
assert all(x['expected']=='BLOCKED' for x in r['adversarial_cases']) and all(m['boundaries'].values())
for k,v in r['expected_counts'].items(): assert m['counts'][k]==v
for marker in ['KII_DEFENSE_INDUSTRY_PP796_CLAUSE_ROUTING','kii-defense-industry-pp796-clause-routing-v1.yaml','kii-defense-industry-pp796-clause-routing-regression-v1.json']: assert marker in inv
print('PASS: PP796 points 1-40, 20 indicator routes, position 5 excluded, 15 formulas, 2 stop guards, printed point-25 anomaly preserved, 8 gates/scenarios, 18 evidence nodes, 12/12 attacks, 64/64 matrix rules/cases; official primary hash pending')
