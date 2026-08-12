# Knowledge Runtime

The runtime is the execution boundary between Father/MindForge agents and canonical knowledge records.

## Rule

Agents address knowledge by stable IDs (`CLM-*`, `ADR-*`, `DM-*`, `SEC-*`, etc.), not by repository paths.
Paths are storage details and may change when domain knowledge bases are split into separate repositories.

## Planned flow

```text
Father / Specialist Agent
          |
          v
   Knowledge Query API
          |
    +-----+------+----------------+
    |            |                |
    v            v                v
 Index/Rank   Graph Expand   Canonical Loader
    |            |                |
    +------------+----------------+
                 |
                 v
        Evidence / Context Gates
                 |
          +------+------+------+
          |      |      |      |
         FAST   ADAPT RESEARCH BLOCKED
          |      |      |      |
          +------+------+- ----+
                 |
                 v
              BRIEF-*
```

## Initial operations

- `resolve_context`
- `search_knowledge`
- `explain_candidate`
- `get_record`
- `get_neighborhood`
- `get_impacts`
- `request_decision_brief`
- `submit_outcome`
- `propose_knowledge_change`

The first implementation should remain a local Python library/CLI around the generated index and canonical YAML. HTTP or MCP adapters are transports layered on top; they must not redefine knowledge semantics.

## Design constraints

1. Canonical repository records are source of truth.
2. The generated index is disposable and rebuildable.
3. Every synthesized answer retains stable canonical references.
4. Hard blockers are returned explicitly, never hidden by ranking.
5. Cross-domain writes use proposals/reviews and domain ownership rules.
6. Security execution requires the authorization and scope contracts defined by Security Core.
