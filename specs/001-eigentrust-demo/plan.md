# Implementation Plan: EigenTrust P2P Trust Algorithm Demonstration

**Branch**: `001-eigentrust-demo` | **Date**: 2025-11-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-eigentrust-demo/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a CLI application that demonstrates the EigenTrust peer-to-peer trust algorithm through simulation and visualization. The application will simulate a network of peers with configurable characteristics (competence and maliciousness on [0,1] scales), execute the EigenTrust algorithm to compute global trust scores, and visualize results through matrix displays and directed graph representations. The system must support iterative algorithm execution to demonstrate convergence properties, handle edge cases gracefully, and provide educational insights into how trust propagates through peer networks.

**Technical Approach**: Use PyTorch for tensor-based matrix operations (EigenTrust eigenvector computation with power iteration method), NetworkX for graph modeling and algorithms, NumPy for numerical operations, and Typer for CLI interface. Visualizations will be generated using Matplotlib for matrix heatmaps, graph rendering, and convergence plots. The EigenTrust implementation includes PageRank-style damping factor (α=0.15) with quality-based pre-trust, and supports Barabási-Albert preferential attachment for realistic network formation. The application follows a single-project structure with domain-driven design, separating simulation logic, algorithm computation, and visualization concerns.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- PyTorch 2.0+ (tensor operations, eigenvector computation, optional GPU acceleration)
- Typer 0.9+ (CLI interface with rich flag support)
- NumPy 1.24+ (numerical operations, array manipulation)
- NetworkX 3.1+ (graph data structures, graph algorithms)
- Matplotlib 3.7+ (visualization: heatmaps, graph plots)
- scikit-learn 1.3+ (optional: additional metrics, utilities)
- Triton 2.0+ (optional: GPU kernel optimization for large-scale operations)

**Storage**: File-based (JSON/pickle for saving/loading simulation state, output visualization files as PNG/SVG)
**Testing**: pytest 7.4+, pytest-cov for coverage, torch.profiler for performance analysis
**Target Platform**: Linux/macOS/Windows desktop (CPU primary, GPU optional)
**Project Type**: Single project (CLI application)
**Performance Goals**:
- Networks up to 100 peers: <5 minutes for full simulation cycle
- Algorithm convergence: <100 iterations for 99% of 50-peer networks
- Visualization rendering: <10 seconds for 50-peer graphs
- Matrix visualization: Auto-annotation threshold at 20×20 for performance

**Constraints**:
- Minimal dependencies (PyTorch, NumPy, NetworkX, Matplotlib, Typer as core)
- No external services or databases
- Single entry point CLI with comprehensive flags
- Algorithm must follow EigenTrust paper formulation exactly

**Scale/Scope**:
- Support networks: 2-100 peers (primary), up to 500 peers (stretch)
- Interaction history: thousands of simulated interactions per network
- Visualization output: matrix heatmaps up to 50×50, graphs up to 100 nodes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Domain-Driven Design ✅ PASS

**Ubiquitous Language**:
- Domain terms: Peer, Interaction, Trust Score, Trust Matrix, Local Trust, Global Trust, Convergence, Competence, Maliciousness
- All code and documentation will use these terms consistently
- No leakage of technical abstractions (tensors, graphs) into domain layer

**Bounded Contexts**:
- Simulation Context: Peer creation, characteristic assignment, interaction simulation
- Algorithm Context: EigenTrust computation, convergence detection, score normalization
- Visualization Context: Matrix rendering, graph layout, visual encoding

**Status**: PASS - Clear domain vocabulary, explicit context boundaries

### II. SOLID Principles ✅ PASS

**Single Responsibility**:
- PeerSimulator: manages peer state and characteristics
- InteractionEngine: simulates peer-to-peer interactions
- EigenTrustComputer: computes trust scores
- TrustMatrixBuilder: constructs normalized trust matrix
- MatrixVisualizer: renders matrix heatmaps
- GraphVisualizer: renders trust graphs
- CLI: orchestrates components, handles user input

**Open/Closed**:
- Visualizers implement common interface, new visualizers added via inheritance
- Interaction outcomes use strategy pattern (competence/maliciousness influence pluggable)

**Liskov Substitution**:
- All visualizers substitutable via common protocol
- Simulation engines interchangeable

**Interface Segregation**:
- Separate interfaces: Simulatable, Computable, Visualizable
- CLI depends only on high-level orchestration interfaces

**Dependency Inversion**:
- High-level CLI depends on abstractions (protocols/abstract classes)
- Low-level implementations (PyTorch tensor ops) hidden behind interfaces

**Status**: PASS - Clear separation of concerns, dependency injection ready

### III. Test-Driven Development ✅ PASS

**Red-Green-Refactor**:
- All algorithm components will be test-first
- Characterization tests for EigenTrust paper examples before implementation
- Acceptance tests derived directly from spec scenarios

**Test Naming**:
- Format: `test_should_<behavior>_when_<condition>`
- Example: `test_should_assign_higher_trust_when_peer_is_competent_and_altruistic`

**One Assert Per Concept**:
- Each test verifies single logical behavior
- Matrix normalization, convergence detection, score computation tested separately

**Status**: PASS - TDD workflow planned, test structure defined

### IV. Working Effectively with Legacy Code ✅ PASS (N/A - Greenfield)

**Status**: PASS - New project, no legacy code. Will follow seam-based development for future modifications.

### V. Three-Tier Testing Strategy ✅ PASS

**Unit Tests** (tests/unit/):
- Peer characteristic assignment
- Interaction outcome computation
- Trust score normalization
- Convergence detection logic
- Matrix operations (mocked PyTorch)
- Target: 80%+ coverage

**Integration Tests** (tests/integration/):
- Full EigenTrust algorithm execution (real PyTorch)
- CLI command execution end-to-end
- File I/O (simulation save/load)
- Visualization generation (output file creation)
- Target: All critical paths covered

**Performance Tests** (tests/performance/):
- Algorithm execution time vs. network size
- Memory usage profiling with torch.profiler
- Convergence iteration counts across scenarios
- Visualization rendering latency
- Target: All user-facing operations measured
- **Note**: These tests are informational only, do NOT fail builds

**Status**: PASS - Clear test tier separation, coverage targets defined

### VI. Simplicity and YAGNI ✅ PASS

**Start Simple**:
- Initial implementation: CPU-only, no Triton optimization
- Basic Matplotlib visualizations (no interactive plots initially)
- File-based state persistence (no database)

**Refactor Toward Patterns**:
- Strategy pattern emerges if multiple interaction models needed
- Factory pattern for visualizers if needed

**Defer Decisions**:
- GPU acceleration deferred until performance tests show need
- Triton kernels optional based on profiling results
- Interactive visualization deferred to future iteration

**Status**: PASS - Minimal initial scope, complexity justified by need

### VII. Observability and Debuggability ✅ PASS

**Structured Logging**:
- Python logging module with JSON formatter
- Log levels: DEBUG (matrix operations), INFO (algorithm progress), WARNING (convergence issues), ERROR (failures)
- Correlation IDs for simulation runs

**Explicit Error Context**:
- All exceptions include: operation attempted, peer IDs, current state (iteration, convergence status)
- Custom exceptions: ConvergenceError, InvalidPeerCharacteristics, MatrixNormalizationError

**Operational Metrics**:
- CLI output includes: iteration count, convergence time, peer count, final trust score distribution
- Performance test output: latency percentiles (p50, p95, p99), throughput (peers/second)

**Status**: PASS - Logging strategy defined, error handling comprehensive

### Constitutional Compliance Summary

**All Gates**: ✅ PASS

No constitutional violations. Project follows all principles:
- Domain-driven design with clear bounded contexts
- SOLID architecture with dependency inversion
- TDD workflow with three-tier testing
- Simple initial design with justified complexity
- Comprehensive observability

## Project Structure

### Documentation (this feature)

```text
specs/001-eigentrust-demo/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── cli-interface.md # CLI command and flag specifications
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── eigentrust/
│   ├── __init__.py
│   ├── domain/              # Domain models (DDD)
│   │   ├── __init__.py
│   │   ├── peer.py          # Peer entity
│   │   ├── interaction.py   # Interaction value object
│   │   ├── trust_matrix.py  # Trust matrix entity
│   │   └── simulation.py    # Simulation aggregate root
│   ├── algorithms/          # EigenTrust computation
│   │   ├── __init__.py
│   │   ├── eigentrust.py    # Core EigenTrust algorithm
│   │   ├── convergence.py   # Convergence detection
│   │   └── normalization.py # Trust score normalization
│   ├── simulation/          # Simulation engine
│   │   ├── __init__.py
│   │   ├── network.py       # Network creation and management
│   │   ├── interactions.py  # Interaction simulation
│   │   └── behaviors.py     # Peer behavior models (competence/maliciousness)
│   ├── visualization/       # Visualization components
│   │   ├── __init__.py
│   │   ├── matrix_viz.py    # Matrix heatmap rendering
│   │   ├── graph_viz.py     # Graph visualization
│   │   └── formatters.py    # Output formatters (JSON, text)
│   ├── cli/                 # CLI interface
│   │   ├── __init__.py
│   │   └── main.py          # Typer CLI entry point
│   └── utils/               # Shared utilities
│       ├── __init__.py
│       ├── logging.py       # Structured logging setup
│       └── io.py            # File I/O (save/load simulations)

tests/
├── unit/                    # Unit tests (isolated, mocked)
│   ├── __init__.py
│   ├── domain/
│   │   ├── test_peer.py
│   │   ├── test_interaction.py
│   │   └── test_trust_matrix.py
│   ├── algorithms/
│   │   ├── test_eigentrust.py
│   │   ├── test_convergence.py
│   │   └── test_normalization.py
│   └── simulation/
│       ├── test_network.py
│       ├── test_interactions.py
│       └── test_behaviors.py
├── integration/             # Integration tests (real components)
│   ├── __init__.py
│   ├── test_full_simulation.py
│   ├── test_cli_commands.py
│   └── test_visualization_output.py
└── performance/             # Performance tests (torch.profiler)
    ├── __init__.py
    ├── test_algorithm_scaling.py
    ├── test_convergence_speed.py
    └── test_visualization_latency.py

pyproject.toml               # Poetry/pip project config
README.md                    # Project overview and quickstart
.gitignore                   # Python, PyTorch, IDE ignores
```

**Structure Decision**: Single project structure selected. This is a CLI application with no frontend/backend separation. The domain-driven design is reflected in the `src/eigentrust/domain/` module containing pure domain entities (Peer, Interaction, TrustMatrix, Simulation). Algorithm logic is isolated in `algorithms/`, simulation engine in `simulation/`, and visualization in `visualization/`. The CLI serves as the application layer orchestrating these components. Tests are organized by tier (unit/integration/performance) as per constitutional requirements.

## Implementation Features

### CLI Commands (8 Total)

**1. `create` - Create Network Simulation**
- `--peers` (default: 10): Number of peers in network (2-500)
- `--output` (default: simulation.json): Output file path
- `--seed`: Random seed for reproducibility
- `--preset` (default: "random"): Peer distribution preset
  - `random`: Uniform random characteristics [0.0, 1.0]
  - `uniform`: All peers at (0.5, 0.5) - morally neutral
  - `adversarial`: Mixed population (30% good, 40% neutral, 30% bad)
- `--verbose`: Enable verbose logging

**2. `simulate` - Simulate Peer Interactions**
- `--input`: Input simulation file (required)
- `--interactions` (default: 100): Number of interactions to simulate
- `--output` (default: simulation_with_interactions.json): Output file path
- `--preferential-attachment`: Use Barabási-Albert preferential attachment (scale-free network)
- `--random`: Use uniform random target selection (default)
- `--verbose`: Enable verbose logging

**3. `run` - Execute EigenTrust Algorithm**
- `--input`: Input simulation file (required)
- `--max-iterations` (default: 100): Maximum algorithm iterations
- `--epsilon` (default: 0.001): Convergence threshold
- `--output` (default: simulation_results.json): Output file path
- `--track-history`: Track iteration-by-iteration convergence history (required for convergence visualization)
- `--verbose`: Enable verbose logging

**4. `info` - Display Simulation Information**
- `--input`: Input simulation file (required)
- `--format` (default: "text"): Output format ("text" or "json")

**5. `visualize-matrix` - Generate Trust Matrix Heatmap**
- `--input`: Input simulation file (required)
- `--output` (default: trust_matrix.png): Output image path
- `--title`: Custom plot title
- `--colormap` (default: "viridis"): Matplotlib colormap (viridis, plasma, inferno, magma, cividis, coolwarm, etc.)
- `--dpi` (default: 300): Image resolution in DPI
- `--annotate`: Force show/hide cell value annotations (auto-detects based on matrix size ≤20×20)
- `--verbose`: Enable verbose logging

**6. `visualize-graph` - Generate Trust Network Graph**
- `--input`: Input simulation file (required)
- `--output` (default: trust_graph.png): Output image path
- `--title`: Custom plot title
- `--layout` (default: "spring"): Graph layout algorithm
  - `spring`: Force-directed layout (weight-aware)
  - `circular`: Circular layout
  - `kamada_kawai`: Kamada-Kawai layout (weight-aware)
- `--edge-threshold` (default: 0.01): Minimum trust value to display edge
- `--dpi` (default: 300): Image resolution in DPI
- `--show-labels` (default: True): Show peer names as node labels
- `--verbose`: Enable verbose logging

**Visual Encoding**:
- **Node color**: Red (malicious) ↔ Green (altruistic) based on maliciousness score
- **Node size**: Proportional to global trust score
- **Edge width**: Proportional to local trust value
- **Edge direction**: Arrow shows trust direction (A→B means A trusts B)

**7. `visualize-convergence` - Generate Convergence History Plot**
- `--input`: Input simulation file (required, must have convergence history from `run --track-history`)
- `--output` (default: convergence.png): Output image path
- `--title`: Custom plot title
- `--top-n` (default: 5): Number of top peers to highlight in evolution plot
- `--dpi` (default: 300): Image resolution in DPI
- `--verbose`: Enable verbose logging

**Plot Structure**:
- **Top subplot**: Trust score evolution for top-N peers + average of remaining peers
- **Bottom subplot**: Convergence delta (log scale) with epsilon threshold line and convergence point annotation

**8. `all` - Complete Pipeline**
Executes full workflow: create → simulate → run → visualize (matrix + graph + convergence)

- `--peers` (default: 10): Number of peers
- `--interactions` (default: 100): Number of interactions to simulate
- `--max-iterations` (default: 100): Maximum EigenTrust iterations
- `--epsilon` (default: 0.001): Convergence threshold
- `--preset` (default: "random"): Peer distribution preset (random/uniform/adversarial)
- `--output-dir` (default: .): Output directory for all generated files
- `--seed`: Random seed for reproducibility
- `--preferential-attachment`: Use preferential attachment model
- `--random`: Use random interaction model (default)

**Generated files**: `simulation.json`, `simulation_with_interactions.json`, `simulation_results.json`, `trust_matrix.png`, `trust_graph.png`, `convergence.png`

### Advanced Algorithm Features

**1. Damping Factor with Pre-Trust (PageRank-style)**
- **Damping parameter**: α = 0.15 (configurable, default in code)
- **Algorithm formula**: `t_{k+1} = (1 - α) * C^T * t_k + α * p`
  - `C`: Column-stochastic trust matrix
  - `t_k`: Trust vector at iteration k
  - `p`: Pre-trust vector (quality-based prior)
- **Pre-trust calculation**: Derived from interaction success rates
  - Peers with higher success rates receive higher pre-trust
  - Normalized to sum to 1.0
- **Purpose**: Prevents rank sink and convergence to uniform distribution
- **Disable**: Set α = 0.0 for pure EigenTrust without damping

**2. Convergence Detection**
- **Norm types**: L1 and L2 distance metrics
- **Threshold**: Configurable epsilon (default: 0.001)
- **Detection**: `||t_{k+1} - t_k|| < epsilon`
- **Output**: Convergence status, final delta, iteration count

**3. History Tracking**
- **Optional feature**: Enabled via `--track-history` flag
- **Data captured**:
  - Trust scores at each iteration
  - Delta magnitude at each iteration
  - Timestamps for each snapshot
- **Storage**: Embedded in simulation JSON file
- **Required for**: Convergence visualization

**4. Column-Stochastic Normalization**
- **Method**: Normalize each column to sum to 1.0
- **Zero-column handling**: Peers with no incoming trust → uniform distribution (1/N)
- **Invariant**: Matrix columns always sum to 1.0 after normalization

### Network Topology Models

**1. Peer Distribution Presets**

- **Random** (default):
  - Competence: Uniform [0.0, 1.0]
  - Maliciousness: Uniform [0.0, 1.0]

- **Uniform**:
  - All peers: (0.5, 0.5) - morally neutral, ready to learn

- **Adversarial**:
  - 30% good peers: competence [0.0-0.2], maliciousness [0.0-0.2]
  - 40% neutral peers: competence [0.4-0.6], maliciousness [0.4-0.6]
  - 30% bad peers: competence [0.8-1.0], maliciousness [0.8-1.0]

**2. Interaction Models**

- **Random Selection** (default, `--random` flag):
  - Source peer: Uniformly random
  - Target peer: Uniformly random (excluding source)
  - Creates Erdős-Rényi random graph properties

- **Barabási-Albert Preferential Attachment** (`--preferential-attachment` flag):
  - Source peer: Uniformly random
  - Target peer: Weighted by cumulative successful interactions
  - Selection probability ∝ (successful_interactions + 1)
  - Creates scale-free, small-world network properties
  - Base count (+1) prevents zero-probability peers
  - **Purpose**: Models realistic peer selection dynamics (popular peers attract more interactions)

**3. Interaction Outcome Model**

- **Success probability formula**:
  ```
  P(success) = (1 - competence) * (1 - maliciousness) + noise
  ```
  - Gaussian noise: μ=0, σ=0.05
  - Clamped to [0.0, 1.0]

- **Interpretation**:
  - Low competence + low maliciousness → high success rate
  - High competence + high maliciousness → low success rate
  - Noise adds realistic variability

- **Local trust updates**:
  - Success: +0.1 to local trust
  - Failure: -0.1 to local trust
  - Initial trust: 0.5 (neutral)
  - Normalized after each update

### Visualization Capabilities

**1. Trust Matrix Heatmap** (`visualize-matrix`)
- **Format**: N×N heatmap with colorbar
- **Colormaps**: All Matplotlib colormaps supported (viridis, plasma, inferno, magma, cividis, coolwarm, RdYlGn, etc.)
- **Annotations**:
  - Automatic: Shown if matrix size ≤ 20×20
  - Manual override: `--annotate` flag
- **Grid**: White lines separating cells
- **Labels**: Peer display names on both axes
- **Resolution**: Configurable DPI (default: 300)

**2. Trust Network Graph** (`visualize-graph`)
- **Graph type**: Directed graph (NetworkX DiGraph)
- **Visual encoding** (multi-dimensional):
  - **Node color**: Red (malicious=1.0) ↔ Green (altruistic=0.0)
  - **Node size**: Proportional to global trust score (range: 300-3000)
  - **Edge width**: Proportional to local trust value (range: 0.5-5.0)
  - **Edge filtering**: Minimum threshold (default: 0.01) to reduce clutter
- **Layout algorithms**:
  - **Spring** (default): Force-directed, weight-aware (trusted peers cluster)
  - **Circular**: Peers arranged in circle
  - **Kamada-Kawai**: Force-directed, weight-aware, emphasis on distance
- **Labels**: Optional peer names (default: shown)
- **Legend**: Explains color and size encoding
- **Resolution**: Configurable DPI (default: 300)

**3. Convergence Plot** (`visualize-convergence`)
- **Requirements**: Must run `run --track-history` first
- **Two-subplot layout**:

  **Top subplot - Trust Evolution**:
  - X-axis: Iteration number
  - Y-axis: Trust score [0.0, 1.0]
  - Lines: Top-N peers (default: 5) + average of remaining peers
  - Legend: Peer identifiers with final scores

  **Bottom subplot - Convergence Delta**:
  - X-axis: Iteration number (shared with top)
  - Y-axis: Delta magnitude (log scale)
  - Line: Convergence metric (L1 or L2 norm)
  - Threshold: Horizontal line at epsilon
  - Annotation: Marks convergence point with iteration number

- **Purpose**: Shows how trust scores evolve and when algorithm stabilizes
- **Resolution**: Configurable DPI (default: 300)

### Data Persistence

**Format**: JSON (human-readable, version-controllable)

**Simulation State Contents**:
- Simulation metadata (ID, timestamp, state, random seed)
- Peer roster (IDs, display names, competence, maliciousness, trust scores)
- Interaction history (source, target, outcome, timestamp)
- Trust matrix (if computed)
- Convergence history (if tracked)
  - Per-iteration snapshots
  - Trust vectors at each iteration
  - Delta magnitudes
  - Timestamps

**Operations**:
- Save complete simulation to JSON file
- Load simulation from JSON file
- Incremental updates (interactions → trust computation)
- Cross-command pipeline support

### Error Handling and Validation

**Custom Domain Exceptions** (10 total):
- `InvalidPeerCharacteristics`: Competence/maliciousness out of [0.0, 1.0]
- `ConvergenceError`: Algorithm fails to converge within max iterations
- `MatrixNormalizationError`: Trust matrix normalization failures
- `InvalidSimulationState`: State transitions violated
- `InsufficientDataError`: Cannot compute trust with zero interactions
- Additional exceptions for file I/O, visualization, CLI validation

**Invariant Enforcement**:
- Peer characteristics always in [0.0, 1.0]
- Trust scores always in [0.0, 1.0]
- Trust scores sum to 1.0 (normalized)
- Matrix columns sum to 1.0 (column-stochastic)
- Non-negative local trust values

**Context-Rich Errors**:
- Operation attempted
- Peer IDs involved
- Current state (iteration, convergence status)
- Suggested remediation

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations. Complexity tracking table is empty.
