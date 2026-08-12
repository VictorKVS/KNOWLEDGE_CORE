# Build and Packaging Engineering

Build and packaging choices are part of architecture because they determine reproducibility, deployment friction, dependency boundaries and incident recovery.

## Core questions

- What artifact is produced?
- Can it be rebuilt from source predictably?
- Which toolchain versions matter?
- Which dependencies are resolved at build time vs runtime?
- How are artifacts signed, checksummed or otherwise verified where required?
- What is the rollback unit?
- Can development, CI and production builds diverge silently?

## Language-specific concerns

### Python
- virtual environments and isolated tooling;
- dependency lock/constraint strategy;
- wheel/source distribution behaviour;
- native extension boundaries;
- reproducible runtime/container selection.

### Go
- module versions and checksums;
- static vs dynamic/environment-dependent assumptions;
- build tags and platform targets;
- reproducible binary metadata where required.

### C++
- compiler/toolchain version;
- ABI compatibility;
- build-system configuration;
- linker/runtime dependencies;
- sanitizer/release build separation;
- package-manager and third-party library provenance.

## Default rule

Prefer a boring, repeatable build over a clever build pipeline. Build complexity must have a concrete payoff.

## Level interpretation

**Junior:** reproduce the documented build and package flow.  
**Middle:** maintain component build configuration and dependency compatibility.  
**Senior:** design artifact boundaries, reproducibility, rollback and multi-platform/toolchain strategy.

← [Engineering Knowledge](../README.md)
