# Tasks: EigenTrust P2P Trust Algorithm Demonstration

**Input**: Design documents from `/specs/001-eigentrust-demo/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Following constitutional TDD principles, tests MUST be written before implementation (Red-Green-Refactor cycle).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure per plan.md (src/eigentrust/, tests/)
- [X] T002 Initialize pyproject.toml with Poetry configuration for Python 3.11+
- [X] T003 [P] Add core dependencies to pyproject.toml (PyTorch 2.0+, Typer 0.9+, NumPy 1.24+, NetworkX 3.1+, Matplotlib 3.7+)
- [X] T004 [P] Add dev dependencies to pyproject.toml (pytest 7.4+, pytest-cov, pytest-mock, black, mypy, ruff)
- [X] T005 [P] Add optional dependencies to pyproject.toml (scikit-learn 1.3+, Triton 2.0+) with extras configuration
- [X] T006 Create .gitignore file with Python, PyTorch, IDE patterns
- [X] T007 [P] Create README.md with project overview and installation instructions
- [X] T008 [P] Create src/eigentrust/__init__.py package file
- [X] T009 [P] Create all subdirectory __init__.py files (domain, algorithms, simulation, visualization, cli, utils)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T010 [P] Create structured logging setup in src/eigentrust/utils/logging.py with JSON formatter
- [X] T011 [P] Create custom exceptions in src/eigentrust/domain/__init__.py (ConvergenceError, InvalidPeerCharacteristics, MatrixNormalizationError, etc.)
- [X] T012 [P] Create base test configuration in pyproject.toml (pytest settings, coverage targets 80%+)
- [X] T013 [P] Create file I/O utilities in src/eigentrust/utils/io.py (save/load JSON, pickle support)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and Configure Peer Network (Priority: P1) 🎯 MVP

**Goal**: Create a network with peers having configurable [competence, maliciousness] characteristics

**Independent Test**: Create network with specified peers, assign characteristics, verify storage and display

### Tests for User Story 1 (TDD - Write First) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T014 [P] [US1] Unit test for Peer entity validation in tests/unit/domain/test_peer.py
- [X] T015 [P] [US1] Unit test for Peer characteristic assignment in tests/unit/domain/test_peer.py
- [X] T016 [P] [US1] Unit test for Simulation entity creation in tests/unit/domain/test_simulation.py
- [X] T017 [P] [US1] Unit test for adding peers to simulation in tests/unit/domain/test_simulation.py
- [X] T018 [P] [US1] Unit test for network creation in tests/unit/simulation/test_network.py
- [X] T019 [P] [US1] Integration test for CLI create command in tests/integration/test_cli_commands.py

### Implementation for User Story 1

- [X] T020 [P] [US1] Create Peer entity in src/eigentrust/domain/peer.py with competence and maliciousness attributes
- [X] T021 [P] [US1] Create InteractionOutcome enum in src/eigentrust/domain/interaction.py
- [X] T022 [P] [US1] Create SimulationState enum in src/eigentrust/domain/simulation.py
- [X] T023 [US1] Create Simulation aggregate root in src/eigentrust/domain/simulation.py (depends on T020, T021, T022)
- [X] T024 [P] [US1] Implement peer behavior probability model in src/eigentrust/simulation/behaviors.py
- [X] T025 [US1] Implement network creation in src/eigentrust/simulation/network.py (creates peers with characteristics)
- [X] T026 [US1] Implement CLI create command in src/eigentrust/cli/main.py using Typer
- [X] T027 [US1] Add peer presets (random, uniform, adversarial) to network creation
- [X] T028 [US1] Add validation for peer characteristics (0.0-1.0 range) with error handling
- [X] T029 [US1] Add JSON serialization/deserialization for Simulation in utils/io.py

**Checkpoint**: User Story 1 complete - Can create and configure peer networks independently

---

## Phase 4: User Story 2 - Run EigenTrust Algorithm (Priority: P2)

**Goal**: Execute EigenTrust algorithm and view computed global trust scores

**Independent Test**: Load pre-configured network, run algorithm, verify trust scores between 0-1 and sum to 1.0

### Tests for User Story 2 (TDD - Write First) ⚠️

- [X] T030 [P] [US2] Unit test for Interaction value object in tests/unit/domain/test_interaction.py
- [X] T031 [P] [US2] Unit test for TrustMatrix entity creation in tests/unit/domain/test_trust_matrix.py
- [X] T032 [P] [US2] Unit test for trust matrix column normalization in tests/unit/algorithms/test_normalization.py
- [X] T033 [P] [US2] Unit test for EigenTrust power iteration in tests/unit/algorithms/test_eigentrust.py
- [X] T034 [P] [US2] Unit test for convergence detection in tests/unit/algorithms/test_convergence.py
- [X] T035 [P] [US2] Unit test for interaction outcome computation in tests/unit/simulation/test_interactions.py
- [X] T036 [P] [US2] Integration test for full algorithm execution in tests/integration/test_full_simulation.py
- [X] T037 [P] [US2] Integration test for CLI run command in tests/integration/test_cli_commands.py

### Implementation for User Story 2

- [X] T038 [P] [US2] Create Interaction value object in src/eigentrust/domain/interaction.py
- [X] T039 [P] [US2] Create TrustScores value object in src/eigentrust/domain/__init__.py
- [X] T040 [P] [US2] Create TrustMatrix entity in src/eigentrust/domain/trust_matrix.py
- [X] T041 [US2] Implement interaction simulation in src/eigentrust/simulation/interactions.py (uses peer behaviors)
- [X] T042 [US2] Implement local trust update logic in Peer entity (based on interaction outcomes)
- [X] T043 [US2] Implement trust matrix builder in TrustMatrix (construct from peer local trust)
- [X] T044 [P] [US2] Implement column normalization in src/eigentrust/algorithms/normalization.py
- [X] T045 [P] [US2] Implement convergence detection in src/eigentrust/algorithms/convergence.py
- [X] T046 [US2] Implement EigenTrust power iteration in src/eigentrust/algorithms/eigentrust.py (uses PyTorch)
- [X] T047 [US2] Implement ConvergenceSnapshot value object for iteration tracking
- [X] T048 [US2] Add simulate method to Simulation aggregate root (generates interactions)
- [X] T049 [US2] Add run_algorithm method to Simulation aggregate root (executes EigenTrust)
- [X] T050 [US2] Implement CLI simulate command in src/eigentrust/cli/main.py
- [X] T051 [US2] Implement CLI run command in src/eigentrust/cli/main.py
- [X] T052 [US2] Add CLI info command to display simulation state and trust scores

**Checkpoint**: User Story 2 complete - Can execute algorithm and view trust scores independently

---

## Phase 5: User Story 3 - Visualize Trust Matrix (Priority: P3)

**Goal**: Display N×N trust matrix as heatmap with annotations

**Independent Test**: Run algorithm on known network, display matrix, verify cell values match calculations and row sums equal 1.0

### Tests for User Story 3 (TDD - Write First) ⚠️

- [ ] T053 [P] [US3] Unit test for matrix heatmap generation in tests/unit/visualization/test_matrix_viz.py
- [ ] T054 [P] [US3] Unit test for matrix annotation logic in tests/unit/visualization/test_matrix_viz.py
- [ ] T055 [P] [US3] Integration test for matrix visualization output in tests/integration/test_visualization_output.py
- [ ] T056 [P] [US3] Integration test for CLI visualize matrix command in tests/integration/test_cli_commands.py

### Implementation for User Story 3

- [X] T057 [P] [US3] Create MatrixVisualizer class in src/eigentrust/visualization/matrix_viz.py
- [X] T058 [US3] Implement heatmap rendering with matplotlib.pyplot.imshow
- [X] T059 [US3] Implement cell annotation for matrices <20×20 peers
- [X] T060 [US3] Implement colorbar and axis labels for matrix visualization
- [X] T061 [US3] Add CLI visualize matrix subcommand in src/eigentrust/cli/main.py
- [X] T062 [US3] Add configurable colormap and DPI options to matrix visualizer

**Checkpoint**: User Story 3 complete - Can visualize trust matrix independently

---

## Phase 6: User Story 4 - Visualize Trust Graph (Priority: P4)

**Goal**: Render peer network as directed graph with visual encoding for peer characteristics

**Independent Test**: Create simple network, visualize graph, verify node colors/sizes reflect characteristics and edges show trust

### Tests for User Story 4 (TDD - Write First) ⚠️

- [ ] T063 [P] [US4] Unit test for graph construction from simulation in tests/unit/visualization/test_graph_viz.py
- [ ] T064 [P] [US4] Unit test for node color encoding in tests/unit/visualization/test_graph_viz.py
- [ ] T065 [P] [US4] Unit test for edge weight encoding in tests/unit/visualization/test_graph_viz.py
- [ ] T066 [P] [US4] Integration test for graph visualization output in tests/integration/test_visualization_output.py
- [ ] T067 [P] [US4] Integration test for CLI visualize graph command in tests/integration/test_cli_commands.py

### Implementation for User Story 4

- [X] T068 [P] [US4] Create GraphVisualizer class in src/eigentrust/visualization/graph_viz.py
- [X] T069 [US4] Implement NetworkX DiGraph construction from Simulation
- [X] T070 [US4] Implement node color encoding (RGB: R=maliciousness, G=1-maliciousness)
- [X] T071 [US4] Implement node size encoding (proportional to 1-competence)
- [X] T072 [US4] Implement edge thickness encoding (proportional to trust weight)
- [X] T073 [US4] Implement graph layout using NetworkX spring_layout
- [X] T074 [US4] Add CLI visualize graph subcommand in src/eigentrust/cli/main.py
- [X] T075 [US4] Add configurable layout and edge threshold options

**Checkpoint**: User Story 4 complete - Can visualize trust graph independently

---

## Phase 7: User Story 5 - Simulate Interactions and Convergence (Priority: P5)

**Goal**: Demonstrate algorithm convergence by tracking trust evolution over iterations

**Independent Test**: Configure network, simulate interactions, run algorithm iteratively, verify convergence and score evolution

### Tests for User Story 5 (TDD - Write First) ⚠️

- [ ] T076 [P] [US5] Unit test for convergence history tracking in tests/unit/domain/test_simulation.py
- [ ] T077 [P] [US5] Unit test for ConvergenceSnapshot creation in tests/unit/domain/test_simulation.py
- [ ] T078 [P] [US5] Unit test for convergence plot generation in tests/unit/visualization/test_formatters.py
- [ ] T079 [P] [US5] Integration test for iterative algorithm execution in tests/integration/test_full_simulation.py
- [ ] T080 [P] [US5] Integration test for CLI visualize convergence command in tests/integration/test_cli_commands.py

### Implementation for User Story 5

- [X] T081 [P] [US5] Extend EigenTrust algorithm to track iteration-by-iteration trust scores
- [X] T082 [US5] Add convergence history to Simulation aggregate root
- [X] T083 [US5] Implement convergence plot in visualization/formatters.py (trust scores over iterations)
- [X] T084 [US5] Implement delta subplot for convergence visualization
- [X] T085 [US5] Add CLI visualize convergence subcommand in src/eigentrust/cli/main.py
- [X] T086 [US5] Add verbose logging to run command showing iteration progress
- [X] T087 [US5] Add CLI all command that runs complete pipeline (create → simulate → run → visualize)

**Checkpoint**: All user stories complete - Full application functionality implemented

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, performance, and quality

- [ ] T088 [P] Add comprehensive docstrings to all domain entities following Google style
- [ ] T089 [P] Add comprehensive docstrings to all algorithm functions
- [ ] T090 [P] Add type hints to all functions and classes for mypy validation
- [ ] T091 [P] Create performance tests in tests/performance/test_algorithm_scaling.py (torch.profiler)
- [ ] T092 [P] Create performance tests in tests/performance/test_convergence_speed.py
- [ ] T093 [P] Create performance tests in tests/performance/test_visualization_latency.py
- [ ] T094 Run black formatter on all source files
- [ ] T095 Run mypy type checker and fix any type errors
- [ ] T096 Run ruff linter and fix any issues
- [ ] T097 Run full test suite with pytest --cov and verify 80%+ coverage
- [ ] T098 [P] Add edge case handling for isolated peers (no interactions)
- [ ] T099 [P] Add edge case handling for uniform networks (all peers identical)
- [ ] T100 [P] Add edge case handling for cold start (zero trust matrix)
- [ ] T101 Create CLI entry point script configuration in pyproject.toml
- [ ] T102 Test installation with `poetry install` and verify `eigentrust --help` works
- [ ] T103 Run quickstart.md validation (execute all example commands, verify outputs)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Depends on US1 domain entities but can be worked in parallel
  - User Story 3 (P3): Can start after Foundational - Depends on US2 algorithm output
  - User Story 4 (P4): Can start after Foundational - Depends on US2 algorithm output
  - User Story 5 (P5): Can start after Foundational - Depends on US2 algorithm, extends it
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation - creates domain model and network
- **User Story 2 (P2)**: Extends US1 with algorithm execution (needs Peer, Simulation from US1)
- **User Story 3 (P3)**: Extends US2 with matrix visualization (needs TrustMatrix from US2)
- **User Story 4 (P4)**: Extends US2 with graph visualization (needs TrustScores from US2)
- **User Story 5 (P5)**: Extends US2 with convergence tracking (needs EigenTrust from US2)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD - Red-Green-Refactor)
- Domain entities before services
- Services before CLI commands
- Core implementation before visualization
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup (Phase 1)**: T003, T004, T005, T007, T008, T009 can run in parallel
- **Foundational (Phase 2)**: T010, T011, T012, T013 can run in parallel
- **Within Each User Story**: All test tasks marked [P] can run in parallel (after tests written, before implementation)
- **Implementation**: Tasks marked [P] within same phase can run in parallel if they affect different files

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (write first):
Task T014: "Unit test for Peer entity validation"
Task T015: "Unit test for Peer characteristic assignment"
Task T016: "Unit test for Simulation entity creation"
Task T017: "Unit test for adding peers to simulation"
Task T018: "Unit test for network creation"
Task T019: "Integration test for CLI create command"

# Launch all domain entities for User Story 1 together (after tests fail):
Task T020: "Create Peer entity"
Task T021: "Create InteractionOutcome enum"
Task T022: "Create SimulationState enum"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (tests → implementation)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Verify can create networks with configurable peer characteristics

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deliverable: Network creation tool
3. Add User Story 2 → Test independently → Deliverable: EigenTrust algorithm demo
4. Add User Story 3 → Test independently → Deliverable: Matrix visualization
5. Add User Story 4 → Test independently → Deliverable: Graph visualization
6. Add User Story 5 → Test independently → Deliverable: Convergence animation
7. Polish → Final release

### Parallel Team Strategy

With multiple developers after Foundational phase completes:

- **Developer A**: User Story 1 (Network creation)
- **Developer B**: User Story 2 (Algorithm - needs US1 entities, coordinate integration)
- **Developer C**: Can start on test infrastructure, documentation, or wait for US2

Stories 3, 4, 5 can proceed in parallel after Story 2 completes (all need algorithm output).

---

## TDD Workflow (Constitutional Requirement)

For each task marked with a test:

1. **Red**: Write failing test (e.g., T014-T019 for US1)
2. **Verify**: Run pytest, confirm test fails with expected error
3. **Green**: Implement minimal code to pass test (e.g., T020-T029 for US1)
4. **Verify**: Run pytest, confirm test passes
5. **Refactor**: Clean up implementation, ensure tests still pass
6. **Commit**: Atomic commit with test + implementation

Example for T014 → T020:

```bash
# Red: Write test first
# Edit tests/unit/domain/test_peer.py
pytest tests/unit/domain/test_peer.py::test_should_validate_competence_range
# Expected: FAILED (module 'peer' not found)

# Green: Implement Peer entity
# Edit src/eigentrust/domain/peer.py
pytest tests/unit/domain/test_peer.py::test_should_validate_competence_range
# Expected: PASSED

# Refactor: Clean up, run all tests
pytest tests/unit/domain/test_peer.py
# Expected: ALL PASSED

# Commit
git add tests/unit/domain/test_peer.py src/eigentrust/domain/peer.py
git commit -m "feat(domain): add Peer entity with characteristic validation

Implements:
- Peer entity with competence and maliciousness attributes
- Validation for [0.0, 1.0] range
- Unit tests for characteristic assignment

TDD: Red-Green-Refactor cycle followed
Tests: tests/unit/domain/test_peer.py"
```

---

## Notes

- [P] tasks = different files, no dependencies within same phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests FAIL before implementing (Red-Green-Refactor)
- Commit after each logical group of related tasks
- Stop at any checkpoint to validate story independently
- Performance tests (Phase 8, T091-T093) are informational only, do NOT fail builds
- Constitution requires 80%+ unit test coverage for business logic
- All tasks follow checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

---

## Task Statistics

- **Total Tasks**: 103
- **Phase 1 (Setup)**: 9 tasks
- **Phase 2 (Foundational)**: 4 tasks (BLOCKING)
- **Phase 3 (US1 - Network Creation)**: 16 tasks (6 tests + 10 implementation)
- **Phase 4 (US2 - Algorithm)**: 23 tasks (8 tests + 15 implementation)
- **Phase 5 (US3 - Matrix Viz)**: 10 tasks (4 tests + 6 implementation)
- **Phase 6 (US4 - Graph Viz)**: 13 tasks (5 tests + 8 implementation)
- **Phase 7 (US5 - Convergence)**: 12 tasks (5 tests + 7 implementation)
- **Phase 8 (Polish)**: 16 tasks

**Parallel Opportunities**: 47 tasks marked [P] (45% of total)

**Test Tasks**: 28 unit/integration tests + 3 performance tests = 31 total test tasks (30% of tasks)

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 29 tasks for minimal viable product
