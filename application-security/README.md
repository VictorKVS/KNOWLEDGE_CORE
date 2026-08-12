# Application Security Knowledge

This layer stores reusable security engineering decisions for application code and interfaces.

## Required review dimensions

- trust boundary;
- attacker-controlled inputs;
- parser/serialization exposure;
- authentication and authorization;
- secrets and sensitive data;
- filesystem/process/network access;
- concurrency and resource exhaustion;
- dependency and build provenance;
- logging and error disclosure;
- deployment assumptions;
- regression coverage for discovered vulnerabilities.

## Security decision object

Every meaningful security review should be linkable to:

```text
Problem / ADR
   ↓
Threat or misuse case
   ↓
Control alternatives
   ↓
Evidence / standard / source
   ↓
Verification
   ↓
Residual risk
   ↓
Decision Memory
```

Security advice must remain scoped to the actual environment, versions and trust model. A generic secure-coding rule may generate candidates, but production guidance requires applicability checks.

← [Engineering Knowledge](../README.md)
