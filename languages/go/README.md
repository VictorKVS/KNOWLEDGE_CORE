# Go Engineering Knowledge

**Role in the ecosystem:** concurrent network services, infrastructure components, security tooling, collectors, CLIs and operationally simple services.

## Knowledge map

- Types and zero values
- Slices, arrays and maps
- Interfaces and composition
- Errors and failure handling
- Goroutines and channels
- Context and cancellation
- Memory allocation and escape analysis
- Networking and HTTP
- Testing and benchmarks
- Modules and builds
- Profiling and performance
- Secure coding
- Production reliability
- Common pitfalls
- Cross-language alternatives

## Decision questions

Typical cards should answer:

- slice vs array vs map?
- channel vs mutex?
- goroutine-per-task vs bounded worker pool?
- interface vs concrete type?
- Go service vs Python service vs C++ component?

## Evidence priority

1. Go specification and official Go documentation;
2. official proposals, release notes and Go team technical material;
3. standards/RFCs relevant to the problem;
4. peer-reviewed research and recognized systems literature;
5. reproducible benchmarks and experiments;
6. mature project documentation and community sources as secondary evidence.

[← Languages](../README.md)
