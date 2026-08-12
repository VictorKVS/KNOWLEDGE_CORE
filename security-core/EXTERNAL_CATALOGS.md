# External Security Catalogs

External catalogs enrich the internal Security Knowledge Graph. They are adapters, not foundations.

## Internal-first rule

The canonical internal path is:

`SEC-SRC -> SEC-REQ -> SEC-ASSET -> SEC-THREAT -> SEC-WEAK -> SEC-CTRL -> SEC-CHECK -> SEC-FIND`

External mappings attach to this graph only after the internal meaning is understood.

## Intended adapters

| Catalog family | Typical attachment point | Must not be treated as |
|---|---|---|
| CWE | SEC-WEAK | observed finding or legal requirement |
| OWASP risk lists | SEC-WEAK / SEC-THREAT / learning views | exhaustive vulnerability inventory |
| MITRE ATT&CK | SEC-THREAT / adversary behavior | normative control requirement |
| CAPEC | SEC-THREAT / SEC-WEAK | proof of exploitability |
| CVE | SEC-FIND / component vulnerability instance | generic weakness class |
| CVSS | SEC-FIND severity context | business risk or legal obligation |
| CIS/vendor hardening | SEC-CTRL / configuration guidance | universal mandatory baseline |

## Many-to-many is normal

A single internal weakness may map to several external entries. One external category may also correspond to several internal weaknesses, threats or checks. Mapping records therefore require an explicit relation type and rationale.

## Top-100 design

The future TOP-100 must be a view over the graph, not a hand-maintained isolated list. A ranked entry should be explainable through internal weakness/threat/control/check nodes, evidence, observed outcomes, exposure context and the external catalogs that enrich it.

## Pentest integration

External catalogs may help select tests, but a pentest check remains an internal `SEC-CHECK` with authorization scope, safety limits, expected evidence, pass/fail semantics and links back to the controls or weaknesses it validates.
