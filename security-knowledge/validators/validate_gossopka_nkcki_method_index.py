import json
from pathlib import Path

P = Path('security-knowledge/evidence/gossopka-nkcki-method-index-regression-v1.json')

def route(c):
    q = c.get('requested_claim')
    if q == 'exact_field_schema':
        return 'ALLOW' if c.get('artifact_acquired') else 'BLOCK'
    if q == 'title_and_index_description':
        return 'ALLOW' if c.get('index_present') else 'BLOCK'
    if q == 'mandatory_for_org':
        return 'ALLOW_WITH_BINDING_SOURCE' if c.get('binding_edge') else 'BLOCK'
    if q == 'delivered_to_NKTsKI':
        return 'ALLOW' if c.get('submission_evidence') and c.get('delivery_evidence') else 'BLOCK'
    if q == 'submitted':
        return 'ALLOW_SUBMISSION_ONLY' if c.get('submission_evidence') else 'BLOCK'
    if q == 'effective_external_deadline_hours':
        vals = [v for v in [c.get('method_deadline_hours'), c.get('regulatory_deadline_hours')] if isinstance(v, (int, float))]
        return min(vals) if vals else 'BLOCK'
    if q == 'attestation_completed':
        return 'BLOCK'
    if q == 'IMMUTABLE_PRIMARY':
        sha = c.get('sha256')
        ok = c.get('bytes_preserved') and c.get('retrieved_at') and isinstance(sha, str) and len(sha) == 64
        return 'ALLOW_IF_IDENTITY_MATCHES' if ok else 'BLOCK'
    if q == 'universal_mandatory_threshold':
        return 'BLOCK' if c.get('attack_type_threshold_source') == 'methodological_example' else 'NEEDS_REVIEW'
    return 'NEEDS_REVIEW'

data = json.loads(P.read_text(encoding='utf-8'))
failed = []
for c in data['cases']:
    actual = route(c)
    if actual != c['expected']:
        failed.append((c['id'], c['expected'], actual))
if failed:
    raise SystemExit(f'FAIL: {failed}')
print(f"PASS: {len(data['cases'])} cases")
