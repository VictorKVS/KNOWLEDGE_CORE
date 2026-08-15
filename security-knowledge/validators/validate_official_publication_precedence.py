from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / 'security-knowledge/provenance/official-publication-precedence-regression-v1.yaml'
MANIFEST = ROOT / 'security-knowledge/provenance/fsb-2025-gosopka-artifact-acquisition-manifest-v1.yaml'
SHA256_RE = re.compile(r'^[0-9a-fA-F]{64}$')
PUB_ID_RE = re.compile(r'^\d{16}$')


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


def validate_manifest():
    manifest = yaml.safe_load(MANIFEST.read_text(encoding='utf-8'))
    artifacts = manifest.get('artifacts', [])
    if not artifacts:
        return ['Manifest contains no artifacts']

    failures = []
    seen_ids = set()
    for artifact in artifacts:
        aid = artifact.get('artifact_id', '<missing-artifact-id>')
        pub_id = str(artifact.get('official_publication_id', ''))
        url = artifact.get('official_document_url', '')
        if not PUB_ID_RE.fullmatch(pub_id):
            failures.append(f'{aid}: invalid official_publication_id {pub_id!r}')
        if pub_id in seen_ids:
            failures.append(f'{aid}: duplicate official_publication_id {pub_id}')
        seen_ids.add(pub_id)
        expected_suffix = f'/document/{pub_id}'
        if not url.startswith('https://publication.pravo.gov.ru/') or expected_suffix not in url:
            failures.append(f'{aid}: official_document_url does not bind to pinned publication id {pub_id}')

        immutable = artifact.get('immutable_status') == 'IMMUTABLE_PRIMARY'
        bytes_preserved = artifact.get('bytes_preserved') is True
        sha256 = artifact.get('sha256')
        retrieved_at = artifact.get('retrieved_at')
        if immutable and not (
            bytes_preserved
            and retrieved_at
            and isinstance(sha256, str)
            and SHA256_RE.fullmatch(sha256)
        ):
            failures.append(f'{aid}: IMMUTABLE_PRIMARY without bytes + retrieved_at + valid SHA-256')
    return failures


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

    failures.extend(validate_manifest())

    if failures:
        raise SystemExit('\n'.join(failures))
    print(f'PASS: {len(cases)} provenance cases + pinned manifest identity checks')


if __name__ == '__main__':
    main()
