# Quickstart Guide: EigenTrust Demonstration

**Feature**: 001-eigentrust-demo
**Phase**: 1 - Design & Contracts
**Date**: 2025-11-15

## Purpose

This quickstart guide provides step-by-step instructions for installing, running, and testing the EigenTrust demonstration application. It includes example scenarios for each user story from the specification.

---

## Installation

### Prerequisites

- Python 3.11 or higher
- pip or Poetry package manager
- (Optional) CUDA-capable GPU for GPU acceleration

### Install with Poetry (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/eigentrust.git
cd eigentrust

# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Verify installation
poetry run eigentrust --version
```

### Install with pip

```bash
# Clone repository
git clone https://github.com/yourusername/eigentrust.git
cd eigentrust

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .

# Verify installation
eigentrust --version
```

### Install Optional Dependencies

```bash
# Install scikit-learn extras
poetry install --extras scikit

# Install Triton for GPU kernel optimization
poetry install --extras triton

# Install all extras
poetry install --all-extras
```

---

## Quick Start: 5-Minute Demo

Run a complete simulation in one command:

```bash
eigentrust all --peers 20 --interactions 200 --output-dir ./demo
```

**Expected Output**:
```
Creating simulation with 20 peers...
Simulating 200 peer interactions...
Running EigenTrust algorithm...
Converged in 18 iterations (delta=0.0007)
Generating visualizations...

✓ Simulation complete!

Files created:
  - ./demo/simulation.json
  - ./demo/sim_results.json
  - ./demo/results.json
  - ./demo/trust_matrix.png
  - ./demo/trust_graph.png
  - ./demo/convergence.png

Top 3 Trusted Peers:
  Peer-007 [0.02, 0.08]: 0.28  (hypercompetent, altruistic)
  Peer-015 [0.05, 0.12]: 0.19  (competent, mostly altruistic)
  Peer-003 [0.15, 0.20]: 0.15  (moderately competent, somewhat altruistic)
```

View your results:

```bash
# Open visualizations
open ./demo/trust_graph.png        # macOS
xdg-open ./demo/trust_graph.png    # Linux
start ./demo/trust_graph.png       # Windows

# Display simulation info
eigentrust info --input ./demo/results.json
```

---

## User Story Walkthroughs

### User Story 1: Create and Configure Peer Network

**Goal**: Create a network with peers of different characteristics.

**Scenario**: Create a 10-peer network with adversarial characteristics.

```bash
# Step 1: Create network
eigentrust create --peers 10 --preset adversarial --output network.json --seed 42

# Expected output:
# Created simulation with 10 peers:
#   - 3 peers [0.0-0.2, 0.0-0.2]: Competent & Altruistic
#   - 4 peers [0.4-0.6, 0.4-0.6]: Neutral
#   - 3 peers [0.8-1.0, 0.8-1.0]: Incompetent & Malicious
# Saved to: network.json

# Step 2: Inspect the network
eigentrust info --input network.json

# Expected output:
# Simulation ID: d34f56a7-...
# Created: 2025-11-15 14:23:10
# State: created
# Peers: 10
#   Peer-001 [0.05, 0.03]: No global trust (algorithm not run)
#   Peer-002 [0.92, 0.88]: No global trust (algorithm not run)
#   ...
```

**Acceptance Test**:
- ✓ System creates 10 peers with unique IDs
- ✓ Peer characteristics stored correctly ([competence, maliciousness])
- ✓ Output file created at network.json

---

### User Story 2: Run EigenTrust Algorithm

**Goal**: Execute the algorithm and view trust scores.

**Prerequisites**: Completed User Story 1 or use existing simulation.

```bash
# Step 1: Simulate interactions (required before running algorithm)
eigentrust simulate --input network.json --interactions 100 --output sim_with_history.json

# Expected output:
# Simulating 100 interactions...
# Results:
#   - Successful: 42 (42%)
#   - Failed: 58 (58%)
# Saved to: sim_with_history.json

# Step 2: Run EigenTrust algorithm
eigentrust run --input sim_with_history.json --max-iterations 100 --epsilon 0.001 --output results.json

# Expected output:
# Running EigenTrust algorithm...
# Iteration 10: delta=0.0542
# Iteration 20: delta=0.0089
# Iteration 27: delta=0.0009 (CONVERGED)
#
# ✓ Algorithm converged in 27 iterations
#
# Trust Scores (sorted by trust):
#   Peer-001 [0.05, 0.03]: 0.31  ⭐ Most trusted
#   Peer-007 [0.12, 0.09]: 0.24
#   Peer-004 [0.48, 0.52]: 0.15
#   Peer-009 [0.55, 0.47]: 0.12
#   ...
#   Peer-002 [0.92, 0.88]: 0.02  ⚠️  Least trusted
#
# Saved to: results.json

# Step 3: View results
eigentrust info --input results.json --format json | jq '.trust_scores_summary'

# Expected JSON output:
# {
#   "min": 0.02,
#   "max": 0.31,
#   "mean": 0.10,
#   "std": 0.09
# }
```

**Acceptance Test**:
- ✓ Global trust scores computed for all peers
- ✓ Trust scores between 0 and 1
- ✓ Competent/altruistic peers [0.0, 0.0] have higher scores than incompetent/malicious peers [1.0, 1.0]
- ✓ Scores are sortable

---

### User Story 3: Visualize Trust Matrix

**Goal**: Display the N×N trust matrix as a heatmap.

**Prerequisites**: Completed User Story 2 (results.json with trust scores).

```bash
# Generate matrix visualization
eigentrust visualize matrix --input results.json --output trust_matrix.png

# Expected output:
# Generating trust matrix heatmap...
# Matrix size: 10x10
# Annotated: Yes (peer count < 20)
# Saved to: trust_matrix.png

# View the image
open trust_matrix.png  # macOS/Linux/Windows
```

**What to Look For in the Visualization**:
- Heatmap shows 10×10 grid
- Each cell (i, j) contains normalized local trust value
- Color scale: dark (low trust) to bright (high trust)
- Row sums equal 1.0 (each row normalized)
- Diagonal is dark/zero (peers don't trust themselves)
- Annotations show exact values (e.g., "0.23")

**Acceptance Test**:
- ✓ Matrix displays 10×10 cells
- ✓ Hovering/inspecting cell (i, j) shows local trust value
- ✓ Row i values sum to 1.0 (verify with spot check on visualization)
- ✓ Colorbar legend shows trust scale 0.0-1.0

---

### User Story 4: Visualize Trust Graph

**Goal**: View the peer network as a directed graph.

**Prerequisites**: Completed User Story 2 (results.json with trust scores).

```bash
# Generate graph visualization
eigentrust visualize graph --input results.json --output trust_graph.png --layout spring

# Expected output:
# Generating trust graph...
# Layout: spring
# Nodes: 10
# Edges: 37 (threshold: 0.01)
# Saved to: trust_graph.png

# View the image
open trust_graph.png
```

**What to Look For in the Visualization**:
- **Nodes**:
  - Green nodes: Altruistic peers (low maliciousness)
  - Red nodes: Malicious peers (high maliciousness)
  - Large nodes: Competent peers (low competence value)
  - Small nodes: Incompetent peers (high competence value)
- **Edges**:
  - Arrows point from truster to trustee
  - Thick edges: High trust
  - Thin edges: Low trust
- **Labels**: Peer IDs with global trust scores

**Example Interpretation**:
- Large green node (Peer-001): Competent & altruistic, highly trusted
- Small red node (Peer-002): Incompetent & malicious, few incoming edges (untrusted)

**Acceptance Test**:
- ✓ Graph displays all 10 peers as nodes
- ✓ Node colors distinguish malicious (red) from altruistic (green)
- ✓ Node sizes distinguish competent (large) from incompetent (small)
- ✓ Edges show trust direction with arrows
- ✓ Edge thickness reflects trust weight

---

### User Story 5: Simulate Interactions and Observe Convergence

**Goal**: See how trust scores evolve over algorithm iterations.

**Prerequisites**: None (this is a complete workflow).

```bash
# Step 1: Create network
eigentrust create --peers 15 --preset random --output iterative_network.json --seed 123

# Step 2: Simulate interactions
eigentrust simulate --input iterative_network.json --interactions 300 --output iterative_sim.json

# Step 3: Run algorithm (it tracks convergence history automatically)
eigentrust run --input iterative_sim.json --output iterative_results.json --verbose

# Expected verbose output shows iteration-by-iteration progress:
# Iteration 1: trust_scores=[0.067, 0.067, ...], delta=0.9331
# Iteration 2: trust_scores=[0.082, 0.053, ...], delta=0.5421
# ...
# Iteration 34: trust_scores=[0.145, 0.092, ...], delta=0.0009 (CONVERGED)

# Step 4: Visualize convergence
eigentrust visualize convergence --input iterative_results.json --output convergence.png

# Expected output:
# Generating convergence plot...
# Iterations: 34
# Peers shown: 10 (limited for readability)
# Saved to: convergence.png

# View the plot
open convergence.png
```

**What to Look For in Convergence Plot**:
- **Top subplot**: Trust score evolution
  - Each line represents one peer's trust score over iterations
  - Peers with [0.0, 0.0] characteristics: lines converge high (near 0.2-0.3)
  - Peers with [1.0, 1.0] characteristics: lines converge low (near 0.01-0.05)
  - Peers with [0.5, 0.5] characteristics: lines converge mid-range
- **Bottom subplot** (if --show-delta=True): Delta (convergence rate)
  - Delta decreases exponentially
  - Crosses epsilon threshold (0.001) at convergence iteration

**Acceptance Test**:
- ✓ Interactions recorded with success/failure based on peer characteristics
- ✓ Trust scores update after each algorithm iteration
- ✓ Convergence plot shows score evolution
- ✓ System reports "Converged in N iterations" message
- ✓ Well-behaved peers [low competence, low maliciousness] show increasing trust over iterations

---

## Advanced Scenarios

### Scenario 1: Reproducible Research Experiment

```bash
# Run identical simulation multiple times with same seed
for i in {1..3}; do
  eigentrust all --peers 20 --interactions 200 --seed 42 --output-dir ./run_$i
  echo "Run $i complete"
done

# Verify all runs produce identical results
diff ./run_1/results.json ./run_2/results.json
diff ./run_2/results.json ./run_3/results.json

# Expected: No differences (reproducible with same seed)
```

### Scenario 2: Performance Profiling

```bash
# Profile algorithm execution
eigentrust run --input large_sim.json --profile --output profiled_results.json

# Expected additional output:
# Performance Profile:
#   Total CPU time: 1234.5 ms
#   Matrix normalization: 45.2 ms (3.7%)
#   Power iteration: 987.3 ms (80.0%)
#   Convergence check: 102.0 ms (8.3%)
#   Other: 100.0 ms (8.0%)
#
# Top operations:
#   1. torch.matmul: 654.2 ms
#   2. torch.norm: 102.0 ms
#   3. normalize_columns: 45.2 ms
```

### Scenario 3: Adversarial Network Analysis

```bash
# Create network with mix of good and malicious peers
eigentrust create --peers 30 --preset adversarial --output adversarial.json

# Simulate adversarial interaction pattern (malicious peers target good peers)
eigentrust simulate --input adversarial.json --interactions 500 --pattern adversarial --output adversarial_sim.json

# Run algorithm
eigentrust run --input adversarial_sim.json --output adversarial_results.json

# Visualize to see if malicious peers are correctly identified
eigentrust visualize graph --input adversarial_results.json --output adversarial_graph.png

# Analyze results
eigentrust info --input adversarial_results.json

# Expected: Malicious peers [0,1] and [1,1] have low trust scores despite competence
```

### Scenario 4: Large-Scale Network

```bash
# Create 100-peer network
eigentrust create --peers 100 --output large_network.json

# Simulate many interactions
eigentrust simulate --input large_network.json --interactions 2000 --output large_sim.json

# Run with GPU acceleration (if available)
eigentrust run --input large_sim.json --gpu --output large_results.json

# Visualize matrix without annotations (too many peers)
eigentrust visualize matrix --input large_results.json --annotate false --output large_matrix.png

# Visualize graph with higher edge threshold (reduce clutter)
eigentrust visualize graph --input large_results.json --edge-threshold 0.05 --output large_graph.png

# Expected: Completes in < 5 minutes per Success Criteria SC-001
```

---

## Testing Scenarios

### Integration Test: Full Pipeline

```bash
# Test complete workflow programmatically
pytest tests/integration/test_full_simulation.py -v

# Expected output:
# test_should_complete_full_simulation_pipeline PASSED
# test_should_handle_edge_case_isolated_peer PASSED
# test_should_handle_edge_case_uniform_network PASSED
# test_should_handle_cold_start PASSED
```

### Performance Test: Algorithm Scaling

```bash
# Run performance tests
pytest tests/performance/test_algorithm_scaling.py -v

# Expected output:
# test_algorithm_performance_vs_network_size PASSED
#
# Performance Scaling Results:
#   10 peers: 5 iterations, 12.34ms CPU time
#   20 peers: 12 iterations, 45.67ms CPU time
#   50 peers: 28 iterations, 234.56ms CPU time
#   100 peers: 45 iterations, 1234.89ms CPU time
#
# ✓ All performance targets met (100 peers < 5 minutes)
```

### Unit Test: Algorithm Correctness

```bash
# Run unit tests for EigenTrust algorithm
pytest tests/unit/algorithms/test_eigentrust.py -v

# Expected output:
# test_should_normalize_trust_matrix_to_column_stochastic PASSED
# test_should_converge_when_iterations_stabilize PASSED
# test_should_compute_correct_trust_for_known_example PASSED
```

---

## Troubleshooting

### Issue: "Algorithm did not converge"

**Symptom**:
```
ERROR: ConvergenceError
Algorithm did not converge within 100 iterations
Final delta: 0.015 (threshold: 0.001)
```

**Solutions**:
1. Increase max iterations: `--max-iterations 200`
2. Relax epsilon: `--epsilon 0.01`
3. Check for cold start (no interactions): Run `simulate` first
4. Verify trust matrix is well-formed: Use `--verbose` to see iteration details

### Issue: "Insufficient interactions"

**Symptom**:
```
ERROR: InsufficientInteractions
Cannot build trust matrix without interactions
```

**Solution**:
```bash
# Run simulate step before running algorithm
eigentrust simulate --input network.json --interactions 100 --output sim.json
eigentrust run --input sim.json --output results.json
```

### Issue: Visualization is cluttered (too many peers)

**Solutions**:
```bash
# For matrix: disable annotations
eigentrust visualize matrix --input results.json --annotate false

# For graph: increase edge threshold to show only strong trust
eigentrust visualize graph --input results.json --edge-threshold 0.1

# For convergence: limit peers shown
eigentrust visualize convergence --input results.json --peer-limit 5
```

### Issue: Slow performance for large networks

**Solutions**:
```bash
# Enable GPU acceleration
eigentrust run --input sim.json --gpu

# Install Triton for optimized kernels
poetry install --extras triton

# Profile to identify bottlenecks
eigentrust run --input sim.json --profile
```

---

## Next Steps

1. **Explore Edge Cases**: Test with 2 peers, 500 peers, uniform networks
2. **Customize Parameters**: Experiment with different epsilon values, interaction patterns
3. **Analyze Results**: Study relationship between peer characteristics and final trust scores
4. **Extend**: Modify peer behavior models in `src/eigentrust/simulation/behaviors.py`
5. **Contribute**: Run full test suite with `pytest tests/ --cov` before submitting PRs

---

## Reference

- **Full CLI Reference**: See [contracts/cli-interface.md](contracts/cli-interface.md)
- **Data Model**: See [data-model.md](data-model.md)
- **Research Decisions**: See [research.md](research.md)
- **Implementation Plan**: See [plan.md](plan.md)

---

## Success Criteria Validation

This quickstart validates all success criteria:

- **SC-001**: ✓ Users can create network + run algorithm in <5 min (tested with 100 peers)
- **SC-002**: ✓ Trust scores correctly reflect characteristics (User Story 2 walkthrough)
- **SC-003**: ✓ Matrix visualization accurate for 50 peers (User Story 3)
- **SC-004**: ✓ Graph distinguishes peer types (User Story 4)
- **SC-005**: ✓ Convergence within 100 iterations (User Story 5)
- **SC-006**: ✓ Users understand relationship within 10 minutes (entire quickstart ~10 min)
- **SC-007**: ✓ Edge cases handled (troubleshooting section + integration tests)
