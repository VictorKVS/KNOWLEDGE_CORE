# FATHER Local Library Publication Policy

Status: ACTIVE

## Rule

The local library root `G:\1\OTUS\Библиотека` is **not** mirrored wholesale to GitHub.

GitHub may contain only:
- directory/catalog structure;
- bibliographic metadata;
- stable IDs;
- source/local-path references;
- SHA-256 hashes;
- rights/use status;
- processing/translation/knowledge status;
- schemas, code and non-copyrighted configuration;
- derived knowledge objects that do not reproduce substantial copyrighted text;
- links to authoritative/public sources when redistribution is not appropriate.

GitHub must not receive by default:
- commercial/copyrighted book PDFs/EPUB/DJVU/DOCX;
- full translated books;
- personal or HR documents;
- internal organizational documents;
- credentials, secrets or private correspondence;
- unrelated private archives;
- standards PDFs unless redistribution rights are explicitly verified.

## Canonical flow

`LOCAL ORIGINAL -> SHA256 -> METADATA -> RIGHTS CHECK -> EXTRACT/TRANSLATE LOCAL -> KNOWLEDGE EXTRACTION -> REVIEW -> GITHUB REGISTRY/KNOWLEDGE`

Full originals and full translations stay local unless a specific source is explicitly approved for publication.

## GitHub registry fields

Each source record should include:
- `source_id`
- `title`
- `author_or_issuer`
- `edition_or_revision`
- `year`
- `local_path`
- `sha256`
- `source_type`
- `language`
- `domain`
- `roles`
- `project_stages`
- `rights_status`
- `publication_status`
- `translation_status`
- `knowledge_status`
- `supersedes`
- `superseded_by`
- `official_source_url`

## Safe default

If publication rights or confidentiality are unclear, set:

`publication_status: LOCAL_ONLY`

and publish metadata only.