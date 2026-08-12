# Dependency and Software Supply Chain Engineering

Dependencies are engineering commitments. Every library, module, container image, compiler, action or package adds capability and also maintenance, provenance and attack-surface obligations.

## Admission questions

- Can the standard library or existing dependency solve this sufficiently?
- What unique value does the new dependency add?
- Is the project maintained and versioned predictably?
- What transitive dependency tree appears?
- What license and operational constraints exist?
- How will vulnerabilities, abandoned packages or breaking changes be handled?
- Is the build reproducible enough for the risk level?

## Required controls by risk

- pin or constrain versions appropriately;
- preserve lockfiles/checksums where supported;
- review provenance of packages, images and CI actions;
- scan dependencies and container images;
- minimize unnecessary transitive dependencies;
- document critical dependency ownership and replacement paths;
- avoid secrets in package/build configuration;
- update intentionally rather than blindly.

## Default rule

Prefer fewer, well-understood dependencies over a larger dependency graph when both satisfy the requirement. Do not reimplement mature security-sensitive primitives merely to reduce dependency count.

## Level interpretation

**Junior:** use approved dependencies and versions.  
**Middle:** evaluate local dependency value, compatibility and test impact.  
**Senior:** account for provenance, supply-chain risk, replacement cost, reproducibility and long-term ownership.

← [Engineering Knowledge](../README.md)
