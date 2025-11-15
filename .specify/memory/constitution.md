<!--
SYNC IMPACT REPORT
==================
Version Change: [INITIAL] → 1.0.0
Modified Principles: N/A (Initial creation)
Added Sections:
  - Core Principles (7 principles based on SOLID, DDD, TDD, Legacy Code)
  - Testing Standards (Three-tier testing strategy)
  - Development Workflow (Seam-based development)
  - Governance
Removed Sections: N/A
Templates Requiring Updates:
  - ✅ plan-template.md - Constitution Check section ready
  - ✅ spec-template.md - User scenarios align with testable acceptance criteria
  - ✅ tasks-template.md - Task organization supports TDD workflow and test tiers
  - ✅ speckit.plan.md - References constitution for gate checks
  - ✅ speckit.tasks.md - Task generation supports test-first approach
  - ✅ speckit.implement.md - Implementation flow supports TDD cycle
Follow-up TODOs: None
-->

# EigenTrust Constitution

## Core Principles

### I. Domain-Driven Design (NON-NEGOTIABLE)

**Ubiquitous Language**: All code, documentation, and communication MUST use domain terminology consistently. Models MUST reflect the problem domain, not the solution domain. Avoid technical abstractions that obscure domain meaning.

**Bounded Contexts**: Each subsystem MUST have clearly defined boundaries. Cross-context communication MUST use explicit translation layers. Domain models MUST NOT leak across context boundaries.

**Rationale**: Domain-driven design ensures that code remains comprehensible to domain experts and maintainable as business requirements evolve. Ubiquitous language eliminates translation overhead and reduces defects from misunderstanding.

### II. SOLID Principles (NON-NEGOTIABLE)

**Single Responsibility**: Each class/module MUST have one reason to change. If a change to business logic requires modifying infrastructure code, the design violates SRP.

**Open/Closed**: Entities MUST be open for extension, closed for modification. New features SHOULD be added via composition or inheritance, not by modifying existing code.

**Liskov Substitution**: Subtypes MUST be substitutable for their base types without breaking correctness. Overridden methods MUST NOT weaken preconditions or strengthen postconditions.

**Interface Segregation**: Clients MUST NOT depend on interfaces they don't use. Prefer many small, focused interfaces over monolithic ones.

**Dependency Inversion**: High-level modules MUST NOT depend on low-level modules. Both MUST depend on abstractions. Abstractions MUST NOT depend on details.

**Rationale**: SOLID principles create code that is testable, maintainable, and resilient to change. They enable safe refactoring and prevent architectural decay.

### III. Test-Driven Development (NON-NEGOTIABLE)

**Red-Green-Refactor Cycle**: Tests MUST be written before implementation. Tests MUST fail initially (Red), then pass with minimal code (Green), then be refactored for clarity and design (Refactor). Implementation without failing tests is strictly forbidden.

**Test Naming**: Test names MUST describe behavior, not implementation. Use `should_<behavior>_when_<condition>` format. Tests are executable specifications.

**One Assert Per Concept**: Each test MUST verify one logical concept. Multiple assertions are acceptable if they verify the same concept from different angles.

**Rationale**: TDD ensures requirements are testable before code is written, creates a safety net for refactoring, and produces cleaner designs through the discipline of writing testable code first.

### IV. Working Effectively with Legacy Code

**Seam Identification**: Before changing legacy code, identify seams—places where behavior can be altered without editing the code itself. Dependency injection points, virtual methods, and interface boundaries are primary seams.

**Characterization Tests**: When behavior is unknown or documentation is missing, write characterization tests that capture current behavior before refactoring. These tests document "what the code does" not "what it should do."

**Incremental Refactoring**: Large refactorings MUST be broken into small, safe steps. Each step MUST be verified by tests. Avoid simultaneous changes to structure and behavior.

**Dependency Breaking**: When code is too coupled to test, use dependency-breaking techniques: Extract Interface, Parameterize Constructor, Subclass and Override Method. Preserve existing behavior during extraction.

**Rationale**: Legacy code lacks tests by definition. These techniques allow safe modification without breaking existing functionality, gradually bringing code under test coverage.

### V. Three-Tier Testing Strategy (NON-NEGOTIABLE)

**Unit Tests** (Test Details):
- MUST test individual components in isolation
- MUST use test doubles (mocks, stubs, fakes) for dependencies
- MUST execute in milliseconds
- MUST NOT touch databases, networks, or filesystems
- Target: 80%+ code coverage for business logic
- Purpose: Verify component correctness and enable rapid feedback

**Integration Tests** (Test Assembly):
- MUST verify components work together correctly
- MUST test real collaborations between modules
- MUST include database interactions, API contracts, message passing
- MAY use test databases or containers
- Target: All critical integration points covered
- Purpose: Catch interface mismatches and configuration errors

**Performance Tests** (Deep Analysis):
- MUST NOT fail builds (informational only)
- MUST measure latency (p50, p95, p99) and throughput
- MUST use profiling tools (e.g., torch profiler for Python, perf for systems code)
- MUST track metrics over time to detect regressions
- MUST run against realistic data volumes
- Purpose: Identify bottlenecks, guide optimization, prevent performance degradation

**Test Organization**:
```
tests/
├── unit/          # Isolated component tests
├── integration/   # Component assembly tests
└── performance/   # Latency and throughput analysis
```

**Rationale**: Unit tests provide rapid feedback. Integration tests catch systemic issues. Performance tests prevent surprise degradation. Separating these tiers allows appropriate tooling and execution frequency for each.

### VI. Simplicity and YAGNI

**Start Simple**: Implement the simplest solution that satisfies current requirements. Avoid speculative generality. Complexity MUST be justified by actual need, not anticipated need.

**Refactor Toward Patterns**: Design patterns emerge through refactoring, not upfront design. When duplication or complexity arises, refactor toward appropriate patterns.

**Defer Decisions**: Defer architectural decisions until the last responsible moment. Preserve options by depending on abstractions, not concrete implementations.

**Rationale**: Premature optimization and over-engineering create maintenance burden. Simple code is easier to understand, test, and modify. Let requirements drive complexity.

### VII. Observability and Debuggability

**Structured Logging**: All components MUST emit structured logs (JSON or key-value format). Logs MUST include correlation IDs for distributed tracing. Log levels MUST be configurable at runtime.

**Explicit Error Context**: Errors MUST include full context—what operation was attempted, what inputs were provided, what state existed. Stack traces alone are insufficient.

**Operational Metrics**: Services MUST expose metrics for monitoring: request rates, error rates, latency distributions, resource utilization. Use standard formats (Prometheus, StatsD).

**Rationale**: Systems fail. Observability enables rapid diagnosis and resolution. Structured logs and metrics allow automated analysis and alerting.

## Testing Standards

**Unit Testing Framework**: Use language-standard frameworks (pytest for Python, JUnit for Java, etc.). Tests MUST be discoverable by framework conventions.

**Test Data Builders**: Use builder pattern or factory functions for test data. Avoid brittle setup code. Make test intent clear through data construction.

**Integration Test Isolation**: Each integration test MUST be independent. Use transactions, containers, or database cleanup to ensure test order independence.

**Performance Test Stability**: Performance tests MUST run in isolated environments. Results MUST be reproducible. Use statistical methods to detect meaningful changes vs. noise.

**Coverage Requirements**:
- Unit tests: 80%+ coverage for business logic
- Integration tests: 100% coverage of critical paths (authentication, payment, data integrity)
- Performance tests: All user-facing operations measured

## Development Workflow

**Seam-Based Development**:
1. Identify integration point (seam) for new feature
2. Write characterization tests for existing behavior at the seam
3. Write failing tests for new behavior (Red)
4. Implement minimal code to pass tests (Green)
5. Refactor for clarity and design (Refactor)
6. Repeat for next seam

**TDD Cycle Enforcement**:
- Pre-commit hooks MUST verify tests exist for changed code
- Code reviews MUST verify tests were written before implementation
- Commits SHOULD be atomic: failing test → passing test → refactor

**Refactoring Safety**:
- All refactorings MUST be covered by existing tests
- If tests don't exist, write characterization tests first
- Refactor in small steps with frequent test runs
- Use IDE refactoring tools when available (safer than manual edits)

## Governance

**Constitutional Authority**: This constitution supersedes project conventions, style guides, and individual preferences. When conflicts arise, constitution rules prevail.

**Amendment Process**:
1. Propose amendment with rationale and impact analysis
2. Review with team for consensus
3. Update version number (semantic versioning):
   - MAJOR: Incompatible changes (principle removal/redefinition)
   - MINOR: New principles or material expansions
   - PATCH: Clarifications, wording fixes, non-semantic changes
4. Update dependent templates and documentation
5. Communicate changes to all contributors

**Compliance Reviews**:
- All pull requests MUST verify constitutional compliance
- Design reviews MUST reference specific principles
- Architectural Decision Records (ADRs) MUST justify deviations

**Complexity Justification**: Any violation of simplicity principles MUST be documented in the complexity tracking table with:
- What constitutional principle is violated
- Why the complexity is necessary for current requirements
- What simpler alternatives were considered and why they were insufficient

**Version**: 1.0.0 | **Ratified**: 2025-11-15 | **Last Amended**: 2025-11-15
