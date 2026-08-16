import json
from datetime import date
from pathlib import Path

P = Path('security-knowledge/evidence/nkcki-reporting-format-authority-regression-v1.json')


def _d(s):
    return date.fromisoformat(s) if s else None


def route(c):
    q = c.get('query')
    if q == 'authority_current':
        event = _d(c.get('event_date'))
        eff = _d(c.get('fsb540_effective_from'))
        if not event or not eff or event < eff:
            return 'NEEDS_PREDECESSOR_REVIEW'
        return 'ALLOW_AUTHORITY_CHAIN' if c.get('authority_edge') and c.get('nkcki_order2_indexed') else 'BLOCK'
    if q == 'exact_field_schema':
        sha = c.get('sha256')
        ok = c.get('artifact_acquired') and c.get('retrieved_at') and isinstance(sha, str) and len(sha) == 64
        return 'ALLOW_IF_ARTIFACT_IDENTITY_MATCHES' if ok else 'BLOCK'
    if q == 'universal_mandatory_threshold':
        return 'ALLOW' if c.get('binding_edge') else 'BLOCK'
    if q == 'mandatory_reporting_format':
        ok = c.get('authority_edge') and c.get('binding_npa_edge') and c.get('applicable_version')
        return 'ALLOW_BINDING_ROUTING' if ok else 'BLOCK'
    if q == 'method_can_extend_deadline':
        return 'BLOCK'
    if q == 'guessed_parameter_is_current':
        return 'ALLOW' if c.get('exact_clause_evidence') else 'BLOCK'
    if q == 'historical_use_of_2026_chain':
        return 'NEEDS_PREDECESSOR_REVIEW' if _d(c.get('event_date')) < date(2026, 1, 30) else 'NEEDS_REVIEW'
    if q == 'index_purpose_claim':
        return 'ALLOW_INDEX_LEVEL_ONLY' if c.get('nkcki_order2_indexed') else 'BLOCK'
    if q == 'immutable_primary':
        sha = c.get('sha256')
        ok = c.get('artifact_acquired') and c.get('retrieved_at') and isinstance(sha, str) and len(sha) == 64
        return 'ALLOW_IF_ARTIFACT_IDENTITY_MATCHES' if ok else 'BLOCK'
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
