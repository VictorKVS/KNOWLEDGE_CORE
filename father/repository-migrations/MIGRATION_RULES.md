# KNOWLEDGE_CORE repository structure migration rules

Status: ACTIVE
Registry: `REPOSITORY_STRUCTURE_PROTECTION.yaml`

Protected knowledge surfaces are structure-stable during generic GitHub cleanup or repository
reorganization. Their content remains actively editable and may mature normally.

Any approved structural migration must have a dedicated record under this directory and preserve:
- logical knowledge-space identity;
- source/provenance references;
- historical snapshot and audit identity;
- cross-repository references from PX00;
- old-to-new path mapping and compatibility period where needed;
- rollback plan and independent review;
- green knowledge-quality and relevant specialized gates.

`security-knowledge/` remains canonical Security truth in KNOWLEDGE_CORE. Repository restructuring
must not move that truth into PX00. Likewise, PX00 runtime/governance truth must not be duplicated here.

Historical snapshots and audit records are not rewritten merely to make a new repository layout look
as if it had always existed.
