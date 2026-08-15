from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / 'security-knowledge/provenance/official-publication-precedence-regression-v1.yaml'
SHA256_RE = re.compile(r'^[0-9a-fA-F]{64}$')


def evaluate(case):
    direct = case.get('direct_publication_id')
    aggregate = case.get('aggregate_publication_id')
    pinned = case.get('pinned_publication_id')

    if direct is None and pinned:
        return 'RETAIN_PINNED_METADATA_PENDING_REOBSERVATION'
    if direct and pinned and direct != pinned:
        return 'NEEDS_PROVENANCE_REVIEW'
    if direct and aggregate and direct != aggregate:
        return 'NEEDS_PROVENANCE_REVIEW'

    exact_bytes = case.get('exact_bytes') is True
    retrieved_at = case.get('retrieved_at')
    sha256 = case.get('sha256')

    if exact_bytes:
        if retrieved_at and isinstance(sha256, str) and SHA256_RE.fullmatch(sha256):
            return 'IMMUTABLE_PRIMARY'
        return 'NOT_IMMUTABLE_PRIMARY'

    return 'AUTHORITATIVE_PUBLICATION_METADATA_VERIFIED'


def main():
    data = yaml.safe_load(FIXTURES.read_text(encoding='utf-8'))
    cases = data.get('cases', [])
    if not cases:
        raise SystemExit('No provenance regression cases found')

    failures = []
    for case in cases:
        got = evaluate(case)
        expected = case['expected']
        if got != expected:
            failures.append(f"{case['id']}: expected {expected}, got {got}")

    if failures:
        raise SystemExit('\n'.join(failures))
    print(f'PASS: {len(cases)} official-publication provenance regression cases')


if __name__ == '__main__':
    main()
