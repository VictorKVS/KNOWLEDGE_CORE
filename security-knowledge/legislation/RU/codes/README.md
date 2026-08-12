# Russian Federation Codes — Security Knowledge Layer

This directory stores code-level legal sources whose provisions create liability, procedural consequences or other legal context relevant to information security.

Current corpus:

- `UK-RF/` — Criminal Code of the Russian Federation, source `SEC-SRC-RU-CODE-UK`;
- `KOAP-RF/` — Code of Administrative Offences of the Russian Federation, source `SEC-SRC-RU-CODE-KOAP`.

## Modeling rule

Codes are not treated as substitutes for substantive security regulation.

The graph distinguishes:

`SUBSTANTIVE DUTY (law / decree / government resolution / regulator order)`

from:

`LIABILITY / CONSEQUENCE (UK RF / KOAP RF / civil or disciplinary consequences)`.

Desired traceability example:

`152-FZ SEC-REQ → violated duty → KOAP 13.11 liability node → risk/consequence`

and:

`187-FZ / KII duty → prohibited/culpable conduct → UK RF 274.1 liability node`.

Every liability node must preserve the exact article/part, source version, effective dates, subject, act/omission, required consequence/result where relevant, qualifying circumstances and sanction. Until that atomization and review are complete, nodes remain `PROPOSED`.
