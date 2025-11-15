# EigenTrust P2P Trust Algorithm Demonstration

A command-line application that demonstrates the EigenTrust peer-to-peer trust algorithm through simulation and visualization.

## Overview

This application simulates peer-to-peer networks with configurable peer characteristics (competence and maliciousness), executes the EigenTrust algorithm to compute global trust scores, and provides rich visualizations to understand how trust propagates through networks.

## Features

- **Peer Network Simulation**: Create networks with peers having orthogonal characteristics:
  - Competence: [0.0, 1.0] where 0.0 = hypercompetent, 1.0 = incompetent
  - Maliciousness: [0.0, 1.0] where 0.0 = altruistic, 1.0 = malicious

- **EigenTrust Algorithm**: Compute global trust scores using the EigenTrust algorithm
  - Power iteration method with convergence detection
  - Normalized trust scores (sum to 1.0)
  - Tracks iteration history for convergence analysis

- **Visualizations**:
  - Trust matrix heatmaps showing local trust values
  - Trust graph with color-coded nodes and weighted edges
  - Convergence plots showing trust evolution over iterations

## Installation

### Prerequisites

- Python 3.11 or higher
- Poetry (recommended) or pip

### Install with Poetry

```bash
# Clone repository
git clone https://github.com/yourusername/eigentrust.git
cd eigentrust

# Install dependencies
poetry install

# Verify installation
poetry run eigentrust --version
```

### Install with pip

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .

# Verify installation
eigentrust --version
```

## Quick Start

Run a complete simulation in one command:

```bash
eigentrust all --peers 20 --interactions 200 --output-dir ./demo
```

This creates a 20-peer network, simulates 200 interactions, runs the EigenTrust algorithm, and generates visualizations in the `./demo` directory.

## Usage

### Create a Network

```bash
eigentrust create --peers 10 --preset random --output network.json
```

### Simulate Interactions

```bash
eigentrust simulate --input network.json --interactions 100 --output sim_results.json
```

### Run EigenTrust Algorithm

```bash
eigentrust run --input sim_results.json --output results.json
```

### Visualize Results

```bash
# Matrix heatmap
eigentrust visualize matrix --input results.json --output matrix.png

# Trust graph
eigentrust visualize graph --input results.json --output graph.png

# Convergence plot
eigentrust visualize convergence --input results.json --output convergence.png

# All visualizations
eigentrust visualize all --input results.json --output-dir ./viz
```

## Documentation

- [Implementation Plan](specs/001-eigentrust-demo/plan.md) - Technical architecture and design decisions
- [Data Model](specs/001-eigentrust-demo/data-model.md) - Domain entities and relationships
- [CLI Reference](specs/001-eigentrust-demo/contracts/cli-interface.md) - Complete CLI documentation
- [Quickstart Guide](specs/001-eigentrust-demo/quickstart.md) - Step-by-step tutorials

## Development

### Setup Development Environment

```bash
# Install with dev dependencies
poetry install

# Install optional extras
poetry install --extras "scikit triton"
```

### Run Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Run specific test file
poetry run pytest tests/unit/domain/test_peer.py
```

### Code Quality

```bash
# Format code
poetry run black src/ tests/

# Type check
poetry run mypy src/

# Lint
poetry run ruff check src/
```

## Architecture

The project follows Domain-Driven Design principles:

```
src/eigentrust/
├── domain/       # Domain entities (Peer, Simulation, TrustMatrix)
├── algorithms/   # EigenTrust computation, convergence
├── simulation/   # Network creation, interaction simulation
├── visualization/# Matrix and graph rendering
├── cli/          # Command-line interface
└── utils/        # Logging, I/O utilities
```

## License

[Your License Here]

## References

- Kamvar, S. D., Schlosser, M. T., & Garcia-Molina, H. (2003). The EigenTrust algorithm for reputation management in P2P networks. *WWW '03*.
