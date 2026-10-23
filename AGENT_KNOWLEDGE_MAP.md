# Father / MindForge — Agent Knowledge Map

This repository is the current shared evidence and knowledge substrate for the Father agent ecosystem.

## Current physical layout

- `KNOWLEDGE_CORE` — common evidence engine, graph/index, decision machinery and domain knowledge under construction.
- `security-core/` — Security Knowledge domain.
- `learning-core/` and programming-related records — Programming Knowledge domain under construction.

## Logical ownership

| Agent | Primary knowledge | Supporting knowledge |
|---|---|---|
| Analyst / Research | research, algorithms, evidence, benchmarks, knowledge-growth methodology | programming, architecture, security, product |
| Architect | architecture, system design | programming, security, DevSecOps, product |
| Programming Agent | programming, algorithms, languages | architecture, security, DevSecOps |
| Security Agent | regulations, requirements, threats, controls, assurance | architecture, programming, DevSecOps, research |
| Pentest Agent | authorized verification, weaknesses, checks, findings | threats, controls, external mappings |
| DevSecOps Agent | delivery, CI/CD, runtime, supply chain | programming, security, architecture |
| Product Agent | product, requirements, prioritization | research, architecture, security |

## Knowledge Growth Analyst specialization

`Knowledge Growth Analyst / Agent Knowledge Engineer` is a specialization of `analyst_research_agent`, not a new authority domain.

Its mission is to grow bounded professional knowledge products for consuming agents:

`scope → sources → atomic knowledge → relations/conflicts → decision logic → retrieval/routing → reproducible cases → independent review → outcomes → reassessment`.

The specialization may research across domains and propose updates, but it does **not** gain automatic authority to promote another domain's canonical truth. Domain-owner review remains mandatory where required by `.ai/agent-knowledge-access-policy.yaml`.

Role maturity is defined in:

- `father/domain-knowledge/KNOWLEDGE_GROWTH_ANALYST_MATURITY_MODEL.yaml`
- `father/domain-knowledge/KNOWLEDGE_GROWTH_ANALYST_ROLE.md`

The target senior capability is bounded: lead a knowledge slice from M0 through a valid M5 readiness process while preserving independent senior review and skeptical red-team separation.

## Stable rule

Physical repository boundaries may change later. Stable IDs and graph relationships must not.

A later split may produce repositories such as `PROGRAMMING_KB`, `SECURITY_KB`, `ARCHITECTURE_KB`, `DEVSECOPS_KB`, `PRODUCT_KB`, `RESEARCH_KB`, `OSINT_KB` and `AI_AGENTS_KB`. Father should still consume them through the same logical query/routing layer.

## Agent access pattern

```text
Task
  ↓
Father / Orchestrator
  ↓
Agent role
  ↓
Knowledge routing registry
  ↓
Knowledge Graph Index
  ↓
Evidence Health + Context Match + Contradictions
  ↓
Canonical records in the relevant domain
  ↓
Decision / Action
  ↓
Outcome / Evidence
  ↓
Knowledge update
```

The agent must not treat its model weights as the primary authority when an evidence-backed domain record exists.
