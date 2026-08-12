# Father / MindForge — Agent Knowledge Map

This repository is the current shared evidence and knowledge substrate for the Father agent ecosystem.

## Current physical layout

- `KNOWLEDGE_CORE` — common evidence engine, graph/index, decision machinery and domain knowledge under construction.
- `security-core/` — Security Knowledge domain.
- `learning-core/` and programming-related records — Programming Knowledge domain under construction.

## Logical ownership

| Agent | Primary knowledge | Supporting knowledge |
|---|---|---|
| Analyst / Research | research, algorithms, evidence, benchmarks | programming, architecture, security, product |
| Architect | architecture, system design | programming, security, DevSecOps, product |
| Programming Agent | programming, algorithms, languages | architecture, security, DevSecOps |
| Security Agent | regulations, requirements, threats, controls, assurance | architecture, programming, DevSecOps, research |
| Pentest Agent | authorized verification, weaknesses, checks, findings | threats, controls, external mappings |
| DevSecOps Agent | delivery, CI/CD, runtime, supply chain | programming, security, architecture |
| Product Agent | product, requirements, prioritization | research, architecture, security |

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
