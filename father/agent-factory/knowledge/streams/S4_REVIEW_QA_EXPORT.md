# S4 — Review, QA, GPT/analyst verification and exports

Mission: prevent unsupported or weakly grounded knowledge from entering KB_READY and make verification machine-readable.

Deliverables:
- evidence package schema for reviewer/GPT/Chief Analyst;
- verdict lifecycle: APPROVE, REVISE, REJECT, ESCALATE;
- deterministic checks: evidence present, source anchor resolvable, translation present where required, no empty claim, no orphan node/edge, score vector complete;
- review provenance: model/reviewer, prompt/profile revision, input node revision, timestamp;
- KB_READY promotion rules;
- JSONL exports for documents, fragments, translations, nodes, edges, evidence, reviews, scores and role views;
- round-trip regression fixture;
- machine-readable failure report.

Acceptance gate: unsupported nodes are blocked from KB_READY; approved nodes can be reconstructed with exact evidence, review history and graph relations from export alone.