# Database Engineering Knowledge

Database selection begins with data semantics, consistency requirements, query patterns, failure modes and operational constraints — not database popularity.

## Core questions

- What are the entities and invariants?
- Which queries dominate the workload?
- What consistency guarantees are required?
- What transaction boundaries exist?
- What scale and growth rate are realistic?
- What retention, backup and recovery objectives exist?
- Which data are sensitive or regulated?
- What latency, availability and durability targets matter?

## Initial decision families

- relational vs document vs key-value vs graph vs time-series;
- normalized vs selectively denormalized schemas;
- strong vs weaker consistency models;
- indexes vs scans vs materialized views;
- database constraints vs application-only validation;
- primary/replica vs sharding vs single-node deployment;
- ORM vs query builder vs direct SQL;
- managed database vs self-hosted database.

## Security and reliability

Records should include authorization boundaries, encryption requirements, injection resistance, backup verification, restore testing, retention, migration safety, resource exhaustion and failure recovery.

← [Engineering Knowledge](../README.md)
