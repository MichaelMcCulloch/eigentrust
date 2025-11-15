# CLI Interface Contract: EigenTrust Demonstration

**Feature**: 001-eigentrust-demo
**Phase**: 1 - Design & Contracts
**Date**: 2025-11-15

## Purpose

This document specifies the command-line interface (CLI) contract for the EigenTrust demonstration application. It defines all commands, flags, arguments, output formats, and error handling behavior.

---

## Entry Point

**Command**: `eigentrust`
**Framework**: Typer (Python)
**Installation**: `pip install eigentrust-demo` or `poetry install` + `poetry run eigentrust`

---

## Command Structure

```bash
eigentrust [COMMAND] [OPTIONS]
```

### Available Commands

1. `create` - Create a new peer network simulation
2. `simulate` - Simulate peer-to-peer interactions
3. `run` - Execute EigenTrust algorithm
4. `visualize` - Generate visualizations
5. `all` - Run complete pipeline (convenience command)
6. `info` - Display simulation information

---

## Command: `create`

**Purpose**: Initialize a new peer network simulation with configured characteristics.

### Syntax

```bash
eigentrust create [OPTIONS]
```

### Options

| Flag | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--peers` | int | No | 10 | Number of peers in network (2-500) |
| `--output` | Path | No | simulation.json | Output file path |
| `--seed` | int | No | None | Random seed for reproducibility |
| `--preset` | str | No | random | Peer distribution preset: random, uniform, adversarial |
| `--verbose` | bool | No | False | Enable detailed logging |

### Presets

- **random**: Peers with random [competence, maliciousness] values uniformly distributed in [0,1]×[0,1]
- **uniform**: All peers with [0.5, 0.5] characteristics (neutral)
- **adversarial**: Mix of [0,0] (good), [1,1] (bad), and [0,1] (malicious competent)

### Output

**Success** (exit code 0):
```json
{
  "simulation_id": "a1b2c3d4-...",
  "peers": 10,
  "output_file": "simulation.json",
  "message": "Created simulation with 10 peers"
}
```

**Error** (exit code 1):
```json
{
  "error": "InvalidPeerCount",
  "message": "Peer count must be between 2 and 500",
  "peers_requested": 1000
}
```

### Examples

```bash
# Create default 10-peer network
eigentrust create

# Create 50-peer network with specific seed
eigentrust create --peers 50 --seed 42 --output my_network.json

# Create adversarial network
eigentrust create --peers 20 --preset adversarial --output adversarial.json
```

---

## Command: `simulate`

**Purpose**: Simulate peer-to-peer interactions to build interaction history.

### Syntax

```bash
eigentrust simulate [OPTIONS]
```

### Options

| Flag | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--input` | Path | Yes | - | Input simulation file |
| `--interactions` | int | No | 100 | Number of interactions to simulate |
| `--output` | Path | No | sim_results.json | Output file path |
| `--pattern` | str | No | random | Interaction pattern: random, preferential, adversarial |
| `--verbose` | bool | No | False | Enable detailed logging |

### Interaction Patterns

- **random**: Each interaction picks random source and target peers
- **preferential**: Peers with higher current local trust are picked more often
- **adversarial**: Malicious peers deliberately target altruistic peers

### Output

**Success** (exit code 0):
```json
{
  "simulation_id": "a1b2c3d4-...",
  "interactions_simulated": 100,
  "success_rate": 0.65,
  "output_file": "sim_results.json",
  "message": "Simulated 100 interactions (65 successful, 35 failed)"
}
```

**Error** (exit code 1):
```json
{
  "error": "SimulationNotFound",
  "message": "Input file not found or invalid",
  "input_file": "missing.json"
}
```

### Examples

```bash
# Simulate 100 random interactions
eigentrust simulate --input simulation.json

# Simulate 500 interactions with preferential attachment
eigentrust simulate --input simulation.json --interactions 500 --pattern preferential

# Simulate adversarial scenario
eigentrust simulate --input simulation.json --interactions 200 --pattern adversarial --output adversarial_sim.json
```

---

## Command: `run`

**Purpose**: Execute the EigenTrust algorithm on a simulation with interaction history.

### Syntax

```bash
eigentrust run [OPTIONS]
```

### Options

| Flag | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--input` | Path | Yes | - | Input simulation file with interactions |
| `--max-iterations` | int | No | 100 | Maximum EigenTrust iterations |
| `--epsilon` | float | No | 0.001 | Convergence threshold |
| `--output` | Path | No | results.json | Output file with trust scores |
| `--profile` | bool | No | False | Enable torch.profiler performance analysis |
| `--gpu` | bool | No | False | Use GPU acceleration (if available) |
| `--verbose` | bool | No | False | Enable detailed logging |

### Output

**Success** (exit code 0):
```json
{
  "simulation_id": "a1b2c3d4-...",
  "converged": true,
  "iterations": 23,
  "final_delta": 0.0008,
  "epsilon": 0.001,
  "execution_time_ms": 145.3,
  "trust_scores": {
    "peer-001": 0.35,
    "peer-002": 0.15,
    "peer-003": 0.50
  },
  "output_file": "results.json",
  "message": "Algorithm converged in 23 iterations"
}
```

**Error - No Convergence** (exit code 1):
```json
{
  "error": "ConvergenceError",
  "message": "Algorithm did not converge within maximum iterations",
  "iterations_reached": 100,
  "final_delta": 0.015,
  "epsilon": 0.001
}
```

**Error - Insufficient Data** (exit code 1):
```json
{
  "error": "InsufficientInteractions",
  "message": "Cannot build trust matrix without interactions",
  "interaction_count": 0,
  "required_minimum": 1
}
```

### Examples

```bash
# Run EigenTrust with defaults
eigentrust run --input sim_results.json

# Run with tighter convergence and more iterations
eigentrust run --input sim_results.json --epsilon 0.0001 --max-iterations 200

# Run with performance profiling
eigentrust run --input sim_results.json --profile --output profiled_results.json

# Run with GPU acceleration
eigentrust run --input sim_results.json --gpu
```

---

## Command: `visualize`

**Purpose**: Generate visual representations of trust matrix and trust graph.

### Syntax

```bash
eigentrust visualize [VISUALIZATION_TYPE] [OPTIONS]
```

### Subcommands

1. `matrix` - Generate trust matrix heatmap
2. `graph` - Generate trust graph
3. `convergence` - Plot convergence history
4. `all` - Generate all visualizations

---

### Subcommand: `visualize matrix`

**Purpose**: Render trust matrix as heatmap.

### Options

| Flag | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--input` | Path | Yes | - | Input results file |
| `--output` | Path | No | trust_matrix.png | Output image path |
| `--annotate` | bool | No | True | Show values in cells (auto-disabled for >20 peers) |
| `--colormap` | str | No | viridis | Matplotlib colormap name |
| `--dpi` | int | No | 300 | Image resolution |
| `--format` | str | No | png | Output format: png, svg, pdf |

### Output

**Success** (exit code 0):
```json
{
  "visualization_type": "matrix",
  "peers": 10,
  "output_file": "trust_matrix.png",
  "dimensions": "10x10",
  "message": "Trust matrix visualization saved"
}
```

### Examples

```bash
# Generate default matrix visualization
eigentrust visualize matrix --input results.json

# Generate high-res SVG with custom colormap
eigentrust visualize matrix --input results.json --output matrix.svg --colormap plasma --dpi 600 --format svg
```

---

### Subcommand: `visualize graph`

**Purpose**: Render trust network as directed graph.

### Options

| Flag | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--input` | Path | Yes | - | Input results file |
| `--output` | Path | No | trust_graph.png | Output image path |
| `--layout` | str | No | spring | Graph layout: spring, circular, kamada_kawai |
| `--edge-threshold` | float | No | 0.01 | Minimum trust value to show edge |
| `--node-size` | int | No | 1000 | Base node size |
| `--dpi` | int | No | 300 | Image resolution |
| `--format` | str | No | png | Output format: png, svg, pdf |

### Node Encoding

- **Color**: RGB gradient (R=maliciousness, G=1-maliciousness, B=0.5)
- **Size**: Proportional to (1 - competence) × base_size
- **Label**: Peer display name + global trust score

### Edge Encoding

- **Thickness**: Proportional to trust weight × 5
- **Direction**: Arrow from truster to trustee
- **Color**: Gray with alpha proportional to weight

### Output

**Success** (exit code 0):
```json
{
  "visualization_type": "graph",
  "peers": 10,
  "edges": 45,
  "output_file": "trust_graph.png",
  "message": "Trust graph visualization saved"
}
```

### Examples

```bash
# Generate default graph visualization
eigentrust visualize graph --input results.json

# Generate graph with circular layout, filtering weak edges
eigentrust visualize graph --input results.json --layout circular --edge-threshold 0.05

# Generate high-quality PDF for publication
eigentrust visualize graph --input results.json --output graph.pdf --format pdf --dpi 600
```

---

### Subcommand: `visualize convergence`

**Purpose**: Plot trust score evolution over algorithm iterations.

### Options

| Flag | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--input` | Path | Yes | - | Input results file |
| `--output` | Path | No | convergence.png | Output image path |
| `--show-delta` | bool | No | True | Include delta (convergence rate) subplot |
| `--peer-limit` | int | No | 10 | Max peers to show (avoids cluttered plots) |
| `--dpi` | int | No | 300 | Image resolution |
| `--format` | str | No | png | Output format: png, svg, pdf |

### Output

**Success** (exit code 0):
```json
{
  "visualization_type": "convergence",
  "iterations": 23,
  "peers_shown": 10,
  "output_file": "convergence.png",
  "message": "Convergence plot saved"
}
```

### Examples

```bash
# Generate convergence plot
eigentrust visualize convergence --input results.json

# Show only top 5 peers
eigentrust visualize convergence --input results.json --peer-limit 5 --output top5_convergence.png
```

---

### Subcommand: `visualize all`

**Purpose**: Generate all visualization types at once.

### Options

| Flag | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--input` | Path | Yes | - | Input results file |
| `--output-dir` | Path | No | ./visualizations | Output directory for all files |
| `--prefix` | str | No | "" | Filename prefix for all outputs |

### Output

**Success** (exit code 0):
```json
{
  "visualization_type": "all",
  "files_created": [
    "./visualizations/trust_matrix.png",
    "./visualizations/trust_graph.png",
    "./visualizations/convergence.png"
  ],
  "message": "All visualizations saved"
}
```

### Examples

```bash
# Generate all visualizations in default directory
eigentrust visualize all --input results.json

# Generate all with custom directory and prefix
eigentrust visualize all --input results.json --output-dir ./output --prefix "experiment1_"
```

---

## Command: `all`

**Purpose**: Execute complete simulation pipeline (create → simulate → run → visualize).

### Syntax

```bash
eigentrust all [OPTIONS]
```

### Options

| Flag | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--peers` | int | No | 10 | Number of peers |
| `--interactions` | int | No | 100 | Number of interactions to simulate |
| `--max-iterations` | int | No | 100 | Max EigenTrust iterations |
| `--epsilon` | float | No | 0.001 | Convergence threshold |
| `--output-dir` | Path | No | ./output | Directory for all output files |
| `--seed` | int | No | None | Random seed |
| `--preset` | str | No | random | Peer preset |
| `--pattern` | str | No | random | Interaction pattern |
| `--visualize` | bool | No | True | Generate visualizations |
| `--verbose` | bool | No | False | Enable detailed logging |

### Output

**Success** (exit code 0):
```json
{
  "pipeline": "complete",
  "simulation_id": "a1b2c3d4-...",
  "steps_completed": ["create", "simulate", "run", "visualize"],
  "converged": true,
  "iterations": 23,
  "files_created": [
    "./output/simulation.json",
    "./output/sim_results.json",
    "./output/results.json",
    "./output/trust_matrix.png",
    "./output/trust_graph.png",
    "./output/convergence.png"
  ],
  "message": "Complete pipeline executed successfully"
}
```

### Examples

```bash
# Run complete default pipeline
eigentrust all

# Run full pipeline with custom parameters
eigentrust all --peers 50 --interactions 500 --seed 42 --output-dir ./experiment1

# Run without visualizations
eigentrust all --peers 20 --visualize false
```

---

## Command: `info`

**Purpose**: Display information about a simulation file.

### Syntax

```bash
eigentrust info [OPTIONS]
```

### Options

| Flag | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--input` | Path | Yes | - | Input simulation file |
| `--format` | str | No | text | Output format: text, json |

### Output (text format)

```
Simulation ID: a1b2c3d4-...
Created: 2025-11-15 12:00:00
State: completed
Peers: 10
Interactions: 100
  - Successful: 65
  - Failed: 35
Algorithm Status: Converged in 23 iterations
Final Delta: 0.0008
Trust Scores:
  Peer-001 [0.0, 0.0]: 0.35
  Peer-002 [1.0, 1.0]: 0.05
  Peer-003 [0.5, 0.5]: 0.12
  ... (7 more)
```

### Output (JSON format)

```json
{
  "simulation_id": "a1b2c3d4-...",
  "created_at": "2025-11-15T12:00:00Z",
  "state": "completed",
  "peers": 10,
  "interactions": {
    "total": 100,
    "successful": 65,
    "failed": 35
  },
  "algorithm": {
    "converged": true,
    "iterations": 23,
    "final_delta": 0.0008,
    "epsilon": 0.001
  },
  "trust_scores_summary": {
    "min": 0.02,
    "max": 0.35,
    "mean": 0.10,
    "std": 0.12
  }
}
```

### Examples

```bash
# Display simulation info as text
eigentrust info --input results.json

# Display as JSON for piping
eigentrust info --input results.json --format json
```

---

## Global Options

Available for all commands:

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--help` | bool | - | Show help message |
| `--version` | bool | - | Show version |
| `--verbose` | bool | False | Enable verbose logging (DEBUG level) |
| `--quiet` | bool | False | Suppress all output except errors |
| `--log-file` | Path | None | Write logs to file |
| `--log-format` | str | text | Log format: text, json |

---

## Error Handling

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error (invalid input, file not found, etc.) |
| 2 | Convergence error (algorithm did not converge) |
| 3 | Validation error (invalid peer characteristics, matrix, etc.) |
| 4 | IO error (file permissions, disk space, etc.) |

### Error Output Format

All errors output JSON to stderr:

```json
{
  "error": "ErrorClassName",
  "message": "Human-readable error description",
  "context": {
    "field1": "value1",
    "field2": "value2"
  },
  "timestamp": "2025-11-15T12:00:00Z"
}
```

---

## Logging

### Log Levels

- **DEBUG**: Matrix operations, iteration details, profiling data
- **INFO**: Algorithm progress, convergence status, file I/O
- **WARNING**: Convergence issues, performance warnings
- **ERROR**: Failures, exceptions, validation errors

### Structured Logging (JSON format)

```json
{
  "timestamp": "2025-11-15T12:00:00.123Z",
  "level": "INFO",
  "message": "EigenTrust converged",
  "context": {
    "simulation_id": "a1b2c3d4-...",
    "iteration": 23,
    "delta": 0.0008,
    "epsilon": 0.001
  }
}
```

---

## Examples: Common Workflows

### Workflow 1: Quick Demo

```bash
# One-command complete demo
eigentrust all --peers 20 --interactions 200
```

### Workflow 2: Reproducible Research

```bash
# Create network with seed
eigentrust create --peers 50 --seed 42 --output exp1_network.json

# Simulate interactions
eigentrust simulate --input exp1_network.json --interactions 1000 --output exp1_sim.json

# Run algorithm with profiling
eigentrust run --input exp1_sim.json --profile --output exp1_results.json

# Generate visualizations
eigentrust visualize all --input exp1_results.json --output-dir ./exp1_viz
```

### Workflow 3: Adversarial Analysis

```bash
# Create adversarial network
eigentrust create --peers 30 --preset adversarial --output adversarial.json

# Simulate adversarial interactions
eigentrust simulate --input adversarial.json --interactions 500 --pattern adversarial --output adversarial_sim.json

# Run algorithm
eigentrust run --input adversarial_sim.json --output adversarial_results.json

# Visualize trust graph only
eigentrust visualize graph --input adversarial_results.json --output adversarial_graph.png
```

---

## Performance Expectations

| Operation | Network Size | Expected Time | Constraint |
|-----------|--------------|---------------|------------|
| `create` | 100 peers | <1 second | SC-001 |
| `simulate` | 100 peers, 1000 interactions | <10 seconds | SC-001 |
| `run` | 50 peers | <1 minute | SC-001, SC-005 |
| `run` | 100 peers | <5 minutes | SC-001 |
| `visualize matrix` | 50 peers | <10 seconds | SC-003 |
| `visualize graph` | 100 peers | <10 seconds | SC-004 |
| `all` (complete) | 100 peers, 1000 interactions | <5 minutes | SC-001 |

---

## Contract Validation

This CLI contract satisfies all functional requirements from spec.md:

- **FR-001**: `create` command creates peer network
- **FR-002**: `create --peers` sets peer count, characteristics assigned during creation
- **FR-003**: Peer characteristics interpretation embedded in simulation behavior
- **FR-004**: `run` command executes EigenTrust algorithm
- **FR-005**: Algorithm automatically normalizes trust scores
- **FR-006**: `info` and `run` output display trust scores
- **FR-007**: `visualize matrix` generates trust matrix visualization
- **FR-008**: `visualize graph` generates directed graph visualization
- **FR-009**: Graph uses color/size encoding for peer characteristics
- **FR-010**: `simulate` command simulates interactions based on characteristics
- **FR-011**: `run --max-iterations` supports iterative execution
- **FR-012**: Convergence history tracked, `visualize convergence` displays evolution
- **FR-013**: `run` output reports convergence status and delta
- **FR-014**: Error handling for edge cases (isolated peers, zero matrix, etc.)
- **FR-015**: `create` can modify existing simulation (or create new), `run` can re-run with different parameters

All success criteria (SC-001 to SC-007) are addressed through performance expectations and error handling.
