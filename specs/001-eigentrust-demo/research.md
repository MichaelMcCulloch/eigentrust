# Research: EigenTrust P2P Trust Algorithm Demonstration

**Feature**: 001-eigentrust-demo
**Phase**: 0 - Research
**Date**: 2025-11-15

## Purpose

This document consolidates research decisions for implementing the EigenTrust peer-to-peer trust algorithm demonstration application. All technical unknowns from the planning phase have been resolved through investigation of best practices, algorithm specifications, and library capabilities.

---

## 1. EigenTrust Algorithm Implementation

### Decision

Implement EigenTrust using PyTorch's eigenvector computation (`torch.linalg.eig`) with power iteration method for large matrices. Follow the algorithm as specified in Kamvar et al. 2003 paper "The EigenTrust Algorithm for Reputation Management in P2P Networks".

### Rationale

**Algorithm Specification**:
- EigenTrust computes global trust as the principal eigenvector of the normalized trust matrix
- Formula: `t = (C^T)^n * p` where C is column-stochastic trust matrix, p is pre-trust vector
- Convergence when `||t_new - t_old|| < epsilon` (typically epsilon = 0.001)

**PyTorch Choice**:
- `torch.linalg.eig` computes eigenvalues and eigenvectors efficiently
- Power iteration: `t_{k+1} = C^T * t_k` is more stable for large sparse matrices
- PyTorch tensors enable GPU acceleration if needed (deferred per YAGNI principle)
- Native support for batch operations useful for iterative visualization

**Implementation Approach**:
```python
# Pseudocode for EigenTrust core
def compute_global_trust(local_trust_matrix, pre_trust, max_iterations=100, epsilon=0.001):
    C = normalize_columns(local_trust_matrix)  # Column-stochastic
    t = pre_trust  # Initial trust vector (uniform or biased)

    for i in range(max_iterations):
        t_new = C.T @ t  # Power iteration
        if torch.norm(t_new - t) < epsilon:
            return t_new, i  # Converged
        t = t_new

    raise ConvergenceError(f"Did not converge after {max_iterations} iterations")
```

### Alternatives Considered

1. **NumPy's `np.linalg.eig`**: Rejected because NumPy lacks GPU support and has slower tensor operations for iterative algorithms
2. **NetworkX PageRank**: Rejected because it's specific to PageRank, not EigenTrust (different damping factor semantics)
3. **SciPy sparse eigensolvers**: Considered but deferred to later optimization; PyTorch sufficient for networks <500 peers
4. **Custom C++ eigensolver**: Rejected as premature optimization violating YAGNI

### References

- Kamvar, S. D., Schlosser, M. T., & Garcia-Molina, H. (2003). The eigentrust algorithm for reputation management in p2p networks. *WWW '03*.
- PyTorch documentation: `torch.linalg.eig` - https://pytorch.org/docs/stable/generated/torch.linalg.eig.html

---

## 2. Peer Behavior Simulation

### Decision

Model peer behavior using probabilistic outcome functions based on competence and maliciousness parameters. Interaction success probability: `P(success) = (1 - competence) * (1 - maliciousness) + random_noise`.

### Rationale

**Orthogonal Characteristics**:
- Competence (0.0-1.0): 0.0 = hypercompetent (always succeeds technically), 1.0 = incompetent (always fails)
- Maliciousness (0.0-1.0): 0.0 = altruistic (tries to help), 1.0 = malicious (tries to harm)

**Behavior Matrix**:
| Peer Type        | Competence | Maliciousness | Behavior                              |
|------------------|------------|---------------|---------------------------------------|
| [0.0, 0.0]       | 0.0        | 0.0           | Hypercompetent & Altruistic (ideal)   |
| [0.0, 1.0]       | 0.0        | 1.0           | Hypercompetent & Malicious (dangerous)|
| [1.0, 0.0]       | 1.0        | 0.0           | Incompetent & Altruistic (well-meaning but harmful) |
| [1.0, 1.0]       | 1.0        | 1.0           | Incompetent & Malicious (worst)       |
| [0.5, 0.5]       | 0.5        | 0.5           | Morally neutral, average competence   |

**Interaction Outcome Formula**:
```python
def compute_interaction_outcome(peer, partner):
    # Base success rate inversely related to incompetence
    technical_success = 1.0 - peer.competence

    # Maliciousness reduces likelihood of helping partner
    cooperation_factor = 1.0 - peer.maliciousness

    # Combined probability
    success_prob = technical_success * cooperation_factor

    # Add small random noise to prevent determinism
    noise = random.gauss(0, 0.05)
    final_prob = max(0.0, min(1.0, success_prob + noise))

    return random.random() < final_prob  # True = success, False = failure
```

**Local Trust Update**:
```python
def update_local_trust(peer_i, peer_j, interaction_outcome):
    # Successful interaction increases trust, failure decreases
    if interaction_outcome:
        trust_delta = +0.1  # Positive feedback
    else:
        trust_delta = -0.1  # Negative feedback

    peer_i.local_trust[peer_j.id] = max(0.0, min(1.0,
        peer_i.local_trust[peer_j.id] + trust_delta))
```

### Alternatives Considered

1. **Deterministic outcomes**: Rejected because it makes simulation unrealistic and predictable
2. **Complex multi-factor models**: Rejected per YAGNI; simple model sufficient for demonstration
3. **Learning behavior (adaptive maliciousness)**: Deferred to future iteration; spec mentions [0.5, 0.5] "ready to learn" but implementation deferred
4. **Game-theoretic strategies**: Rejected as beyond scope; this is reputation system demo, not game theory

### References

- Josang, A., Ismail, R., & Boyd, C. (2007). A survey of trust and reputation systems for online service provision. *Decision Support Systems*.

---

## 3. Visualization Best Practices

### Decision

Use Matplotlib for both matrix heatmaps and graph visualizations. Matrix: `plt.imshow` with colorbar. Graph: NetworkX spring layout with Matplotlib rendering, color-coded nodes and weighted edges.

### Rationale

**Matrix Visualization**:
```python
def visualize_trust_matrix(matrix, peer_ids):
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(matrix, cmap='viridis', aspect='auto', vmin=0, vmax=1)

    # Labels
    ax.set_xticks(range(len(peer_ids)))
    ax.set_yticks(range(len(peer_ids)))
    ax.set_xticklabels(peer_ids, rotation=45)
    ax.set_yticklabels(peer_ids)

    # Colorbar
    plt.colorbar(im, label='Trust Score')

    # Annotations (for small matrices <20x20)
    if len(peer_ids) < 20:
        for i in range(len(peer_ids)):
            for j in range(len(peer_ids)):
                text = ax.text(j, i, f'{matrix[i, j]:.2f}',
                              ha="center", va="center", color="white")

    plt.savefig('trust_matrix.png', dpi=300, bbox_inches='tight')
```

**Graph Visualization**:
```python
def visualize_trust_graph(peers, trust_matrix):
    G = nx.DiGraph()

    # Add nodes with attributes
    for peer in peers:
        G.add_node(peer.id,
                   competence=peer.competence,
                   maliciousness=peer.maliciousness,
                   trust_score=peer.global_trust)

    # Add edges with weights
    for i, peer_i in enumerate(peers):
        for j, peer_j in enumerate(peers):
            if i != j and trust_matrix[i, j] > 0.01:  # Threshold for visibility
                G.add_edge(peer_i.id, peer_j.id, weight=trust_matrix[i, j])

    # Layout
    pos = nx.spring_layout(G, k=1.5, iterations=50)

    # Node colors based on characteristics
    node_colors = []
    for peer in peers:
        # Green for altruistic (low maliciousness), Red for malicious
        # Size indicates competence (larger = more competent)
        r = peer.maliciousness
        g = 1.0 - peer.maliciousness
        b = 0.5
        node_colors.append((r, g, b))

    # Draw
    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                           node_size=[(1-p.competence)*1000 for p in peers])
    nx.draw_networkx_edges(G, pos, width=[G[u][v]['weight']*5 for u,v in G.edges()])
    nx.draw_networkx_labels(G, pos, font_size=8)

    plt.savefig('trust_graph.png', dpi=300, bbox_inches='tight')
```

**Color Encoding**:
- **Nodes**: RGB gradient where Red = maliciousness, Green = altruism (1-maliciousness)
- **Node size**: Proportional to competence (larger = more competent)
- **Edge thickness**: Proportional to trust weight
- **Edge direction**: Arrows show who trusts whom

### Alternatives Considered

1. **Plotly for interactive graphs**: Deferred per YAGNI; static images sufficient for initial demo
2. **Graphviz for graph layout**: Rejected because NetworkX spring layout more suitable for trust networks
3. **Seaborn for heatmaps**: Rejected because Matplotlib `imshow` simpler and more controllable
4. **D3.js web visualization**: Rejected as this is CLI application, not web app

### References

- Matplotlib documentation: https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html
- NetworkX visualization: https://networkx.org/documentation/stable/reference/drawing.html

---

## 4. CLI Interface Design with Typer

### Decision

Single entry point using Typer with subcommands for different operations: `create`, `run`, `visualize`, `simulate`. Rich formatting for output.

### Rationale

**Command Structure**:
```bash
eigentrust create --peers 20 --output simulation.json
eigentrust simulate --input simulation.json --interactions 100 --output sim_with_history.json
eigentrust run --input sim_with_history.json --max-iterations 100 --epsilon 0.001
eigentrust visualize matrix --input results.json --output matrix.png
eigentrust visualize graph --input results.json --output graph.png
eigentrust all --peers 20 --interactions 100  # Convenience: run full pipeline
```

**Typer Implementation**:
```python
import typer
from typing_extensions import Annotated

app = typer.Typer()

@app.command()
def create(
    peers: Annotated[int, typer.Option(help="Number of peers in network")] = 10,
    output: Annotated[str, typer.Option(help="Output file path")] = "simulation.json",
    seed: Annotated[int, typer.Option(help="Random seed for reproducibility")] = None,
):
    """Create a new peer network simulation."""
    # Implementation

@app.command()
def simulate(
    input: Annotated[str, typer.Option(help="Input simulation file")],
    interactions: Annotated[int, typer.Option(help="Number of interactions to simulate")] = 100,
    output: Annotated[str, typer.Option(help="Output file path")] = "sim_results.json",
):
    """Simulate peer-to-peer interactions."""
    # Implementation

@app.command()
def run(
    input: Annotated[str, typer.Option(help="Input simulation file")],
    max_iterations: Annotated[int, typer.Option(help="Max EigenTrust iterations")] = 100,
    epsilon: Annotated[float, typer.Option(help="Convergence threshold")] = 0.001,
    output: Annotated[str, typer.Option(help="Output file path")] = "results.json",
):
    """Run EigenTrust algorithm on simulation."""
    # Implementation
```

**Flags to Expose** (per user requirement):
- `--peers`: Number of peers
- `--interactions`: Number of simulated interactions
- `--max-iterations`: EigenTrust max iterations
- `--epsilon`: Convergence threshold
- `--seed`: Random seed for reproducibility
- `--output`: Output file path
- `--input`: Input file path
- `--verbose`: Enable debug logging
- `--gpu`: Enable GPU acceleration (optional, deferred)
- `--profile`: Enable torch.profiler performance analysis

### Alternatives Considered

1. **Click**: Rejected because Typer is more modern, has better type hints integration
2. **argparse**: Rejected because Typer provides better UX with less boilerplate
3. **Fire**: Rejected because it's too magical; Typer gives better control
4. **Multiple entry points**: Rejected; single entry point with subcommands cleaner

### References

- Typer documentation: https://typer.tiangolo.com/
- Best practices: https://clig.dev/ (Command Line Interface Guidelines)

---

## 5. Testing Strategy with pytest and torch.profiler

### Decision

Use pytest for all test tiers. Unit tests with mocks (pytest-mock), integration tests with real components, performance tests with torch.profiler and pytest-benchmark.

### Rationale

**Unit Test Example**:
```python
# tests/unit/algorithms/test_eigentrust.py
import pytest
import torch
from unittest.mock import Mock
from eigentrust.algorithms.eigentrust import EigenTrustComputer

def test_should_normalize_trust_matrix_to_column_stochastic():
    """Test that trust matrix columns sum to 1."""
    computer = EigenTrustComputer()
    matrix = torch.tensor([[1.0, 2.0], [3.0, 4.0]])

    normalized = computer.normalize_columns(matrix)

    col_sums = normalized.sum(dim=0)
    assert torch.allclose(col_sums, torch.ones(2), atol=1e-6)

def test_should_converge_when_iterations_stabilize():
    """Test convergence detection."""
    computer = EigenTrustComputer()
    trust_matrix = torch.tensor([[0.0, 0.7, 0.3],
                                  [0.5, 0.0, 0.5],
                                  [0.4, 0.6, 0.0]])
    pre_trust = torch.ones(3) / 3

    global_trust, iterations = computer.compute(trust_matrix, pre_trust, epsilon=0.001)

    assert iterations < 100
    assert torch.allclose(global_trust.sum(), torch.tensor(1.0))
```

**Integration Test Example**:
```python
# tests/integration/test_full_simulation.py
import pytest
from eigentrust.cli.main import app
from typer.testing import CliRunner

def test_should_complete_full_simulation_pipeline():
    """Test full workflow: create -> simulate -> run -> visualize."""
    runner = CliRunner()

    # Create network
    result = runner.invoke(app, ["create", "--peers", "10", "--output", "test_sim.json"])
    assert result.exit_code == 0

    # Simulate interactions
    result = runner.invoke(app, ["simulate", "--input", "test_sim.json",
                                  "--interactions", "50", "--output", "test_history.json"])
    assert result.exit_code == 0

    # Run EigenTrust
    result = runner.invoke(app, ["run", "--input", "test_history.json",
                                  "--output", "test_results.json"])
    assert result.exit_code == 0
    assert "Converged" in result.stdout

    # Visualize
    result = runner.invoke(app, ["visualize", "matrix", "--input", "test_results.json"])
    assert result.exit_code == 0
```

**Performance Test Example**:
```python
# tests/performance/test_algorithm_scaling.py
import pytest
import torch
from eigentrust.algorithms.eigentrust import EigenTrustComputer

def test_algorithm_performance_vs_network_size(benchmark):
    """Measure EigenTrust execution time for different network sizes."""
    sizes = [10, 20, 50, 100]
    results = {}

    for n in sizes:
        trust_matrix = torch.rand(n, n)
        pre_trust = torch.ones(n) / n
        computer = EigenTrustComputer()

        # Use torch.profiler
        with torch.profiler.profile(
            activities=[torch.profiler.ProfilerActivity.CPU],
            record_shapes=True,
        ) as prof:
            global_trust, iters = computer.compute(trust_matrix, pre_trust)

        results[n] = {
            'iterations': iters,
            'cpu_time': prof.key_averages().total_average().cpu_time_total,
        }

    # Print profiling results (informational, doesn't fail)
    print(f"\nPerformance Scaling Results:")
    for n, metrics in results.items():
        print(f"  {n} peers: {metrics['iterations']} iterations, "
              f"{metrics['cpu_time']/1e6:.2f}ms CPU time")

    # Assert performance targets (informational warnings, not failures)
    if results[100]['cpu_time'] / 1e9 > 5.0:  # 5 seconds
        print(f"WARNING: 100-peer network took {results[100]['cpu_time']/1e9:.2f}s "
              f"(target: <5s)")
```

**Coverage Configuration** (pyproject.toml):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--cov=src/eigentrust",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=80",
]

[tool.coverage.run]
branch = true
source = ["src/eigentrust"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

### Alternatives Considered

1. **unittest**: Rejected because pytest is more Pythonic and has better fixture support
2. **nose**: Rejected because it's deprecated
3. **cProfile for profiling**: Considered but torch.profiler is more suitable for PyTorch ops
4. **Manual benchmarking**: Rejected because pytest-benchmark provides better statistics

### References

- pytest documentation: https://docs.pytest.org/
- pytest-cov: https://pytest-cov.readthedocs.io/
- torch.profiler: https://pytorch.org/tutorials/recipes/recipes/profiler_recipe.html

---

## 6. Dependency Management and Project Setup

### Decision

Use Poetry for dependency management. Python 3.11+ with type hints throughout. Black for formatting, mypy for type checking, ruff for linting.

### Rationale

**pyproject.toml** (Poetry configuration):
```toml
[tool.poetry]
name = "eigentrust-demo"
version = "0.1.0"
description = "EigenTrust P2P trust algorithm demonstration"
authors = ["Your Name <you@example.com>"]
readme = "README.md"
packages = [{include = "eigentrust", from = "src"}]

[tool.poetry.dependencies]
python = "^3.11"
torch = "^2.0.0"
typer = {extras = ["all"], version = "^0.9.0"}
numpy = "^1.24.0"
networkx = "^3.1"
matplotlib = "^3.7.0"
scikit-learn = {version = "^1.3.0", optional = true}
triton = {version = "^2.0.0", optional = true}

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
pytest-mock = "^3.11.0"
pytest-benchmark = "^4.0.0"
black = "^23.7.0"
mypy = "^1.4.0"
ruff = "^0.0.285"

[tool.poetry.extras]
scikit = ["scikit-learn"]
triton = ["triton"]

[tool.poetry.scripts]
eigentrust = "eigentrust.cli.main:app"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

**Rationale for Tools**:
- **Poetry**: Better dependency resolution than pip, lock files for reproducibility
- **Black**: Opinionated formatter eliminates style debates
- **mypy**: Type checking catches bugs early (constitutional observability principle)
- **ruff**: Fast linter replacing flake8, isort, etc.
- **Type hints**: Required for mypy, improves IDE support and documentation

**Development Setup**:
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Install with optional extras
poetry install --extras "scikit triton"

# Run CLI
poetry run eigentrust --help

# Run tests
poetry run pytest

# Format code
poetry run black src/ tests/

# Type check
poetry run mypy src/

# Lint
poetry run ruff check src/
```

### Alternatives Considered

1. **pip + requirements.txt**: Rejected because Poetry provides better dependency resolution
2. **conda**: Rejected because Poetry is more standard for pure Python projects
3. **pipenv**: Rejected because Poetry is more actively maintained
4. **setuptools**: Rejected because Poetry has better UX

### References

- Poetry documentation: https://python-poetry.org/docs/
- Black: https://black.readthedocs.io/
- mypy: https://mypy.readthedocs.io/
- ruff: https://beta.ruff.rs/docs/

---

## Summary of Research Decisions

| Topic | Decision | Rationale |
|-------|----------|-----------|
| **EigenTrust Algorithm** | PyTorch power iteration with `torch.linalg.eig` | Efficient, GPU-ready, follows Kamvar et al. 2003 paper |
| **Peer Behavior** | Probabilistic outcomes based on competence/maliciousness | Realistic simulation with orthogonal characteristics |
| **Matrix Visualization** | Matplotlib `imshow` with colorbar | Standard, annotatable, publication-quality |
| **Graph Visualization** | NetworkX spring layout + Matplotlib | Color-coded nodes, weighted edges, clear trust flow |
| **CLI Framework** | Typer with subcommands | Type-safe, modern, excellent UX |
| **Testing** | pytest (unit/integration), torch.profiler (performance) | Three-tier strategy per constitution |
| **Dependencies** | Poetry, Python 3.11+, minimal deps | Reproducible, type-checked, maintainable |

All NEEDS CLARIFICATION items from Technical Context have been resolved. Ready to proceed to Phase 1 (Design & Contracts).
