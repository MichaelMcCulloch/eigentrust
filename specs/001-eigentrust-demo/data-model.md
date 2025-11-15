# Data Model: EigenTrust P2P Trust Algorithm Demonstration

**Feature**: 001-eigentrust-demo
**Phase**: 1 - Design & Contracts
**Date**: 2025-11-15

## Purpose

This document defines the domain entities, value objects, and their relationships for the EigenTrust demonstration application. The model follows Domain-Driven Design principles with clear bounded contexts and ubiquitous language.

---

## Domain Model Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Simulation (Aggregate Root)              │
│  - simulation_id: UUID                                       │
│  - created_at: datetime                                      │
│  - state: SimulationState (CREATED, RUNNING, COMPLETED)      │
│  - peers: List[Peer]                                         │
│  - interactions: List[Interaction]                           │
│  - trust_matrix: TrustMatrix                                 │
│  - convergence_history: List[ConvergenceSnapshot]            │
│  + run_algorithm() -> TrustScores                            │
│  + simulate_interactions(count: int) -> List[Interaction]    │
└─────────────────────────────────────────────────────────────┘
                    │                        │
                    │ contains               │ contains
                    ▼                        ▼
        ┌─────────────────────┐    ┌─────────────────────┐
        │   Peer (Entity)      │    │ Interaction (VO)    │
        │  - peer_id: UUID     │    │  - source: PeerID   │
        │  - competence: float │    │  - target: PeerID   │
        │  - maliciousness: fl │    │  - outcome: Outcome │
        │  - global_trust: fl  │    │  - timestamp: dt    │
        │  - local_trust: dict │    └─────────────────────┘
        └─────────────────────┘
                    │
                    │ produces
                    ▼
        ┌─────────────────────────────────────┐
        │   TrustMatrix (Entity)               │
        │  - matrix: Tensor[N, N]              │
        │  - peer_mapping: Dict[PeerID, int]   │
        │  + normalize_columns() -> Tensor     │
        │  + get_trust(i, j) -> float          │
        └─────────────────────────────────────┘
                    │
                    │ computes
                    ▼
        ┌─────────────────────────────────────┐
        │   TrustScores (Value Object)         │
        │  - scores: Dict[PeerID, float]       │
        │  - iteration_count: int              │
        │  - converged: bool                   │
        │  - convergence_epsilon: float        │
        └─────────────────────────────────────┘
```

---

## Entities

### 1. Simulation (Aggregate Root)

**Purpose**: The root entity that encapsulates the entire simulation state. Enforces invariants across all contained entities.

**Attributes**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `simulation_id` | UUID | Unique identifier for simulation | Auto-generated |
| `created_at` | datetime | Timestamp of creation | Auto-set on creation |
| `state` | SimulationState | Current state (CREATED, RUNNING, COMPLETED, FAILED) | Enum validation |
| `peers` | List[Peer] | Collection of all peers in network | 2 ≤ len(peers) ≤ 500 |
| `interactions` | List[Interaction] | History of all peer interactions | len ≥ 0 |
| `trust_matrix` | TrustMatrix | N×N matrix of local trust values | Built from interactions |
| `convergence_history` | List[ConvergenceSnapshot] | Iteration-by-iteration trust evolution | For visualization |
| `random_seed` | Optional[int] | Seed for reproducibility | None or positive int |

**Invariants**:
- Simulation must contain at least 2 peers (cannot compute trust with <2 peers)
- All interactions must reference existing peers within this simulation
- Trust matrix dimensions must match peer count
- State transitions: CREATED → RUNNING → COMPLETED or CREATED → FAILED

**Methods**:
- `run_algorithm(max_iterations: int, epsilon: float) -> TrustScores`: Execute EigenTrust algorithm
- `simulate_interactions(count: int) -> List[Interaction]`: Generate random interactions based on peer characteristics
- `add_peer(competence: float, maliciousness: float) -> Peer`: Add new peer to network
- `save(path: Path) -> None`: Serialize simulation to file
- `@classmethod load(path: Path) -> Simulation`: Deserialize from file

**State Transitions**:
```
CREATED --[simulate_interactions]--> RUNNING
RUNNING --[run_algorithm success]--> COMPLETED
RUNNING --[run_algorithm failure]--> FAILED
COMPLETED --[modify peers]--> CREATED (reset)
```

---

### 2. Peer (Entity)

**Purpose**: Represents an individual node in the peer-to-peer network with behavioral characteristics.

**Attributes**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `peer_id` | UUID | Unique identifier | Auto-generated |
| `competence` | float | Incompetence level [0.0, 1.0] | 0.0 ≤ value ≤ 1.0 |
| `maliciousness` | float | Malicious intent [0.0, 1.0] | 0.0 ≤ value ≤ 1.0 |
| `global_trust` | float | EigenTrust-computed global trust score | 0.0 ≤ value ≤ 1.0, sum(all peers) = 1.0 |
| `local_trust` | Dict[PeerID, float] | Trust this peer assigns to others | Each value in [0.0, 1.0] |
| `display_name` | str | Human-readable name (e.g., "Peer-001") | Non-empty |

**Behavioral Characteristics**:

| Coordinates | Interpretation | Success Probability Formula |
|-------------|----------------|----------------------------|
| [0.0, 0.0] | Hypercompetent & Altruistic | P(success) ≈ 1.0 |
| [0.0, 1.0] | Hypercompetent & Malicious | P(success) ≈ 0.0 (refuses to help) |
| [1.0, 0.0] | Incompetent & Altruistic | P(success) ≈ 0.0 (tries but fails) |
| [1.0, 1.0] | Incompetent & Malicious | P(success) ≈ 0.0 (worst) |
| [0.5, 0.5] | Neutral | P(success) ≈ 0.25 |

**Formula**: `P(success) = (1 - competence) * (1 - maliciousness) + random_noise(0, 0.05)`

**Invariants**:
- Competence and maliciousness must be in [0.0, 1.0]
- Global trust score initially None, set after algorithm execution
- Local trust dictionary keys must reference existing peer IDs in same simulation

**Methods**:
- `compute_interaction_outcome(partner: Peer) -> InteractionOutcome`: Determine if interaction succeeds
- `update_local_trust(partner: Peer, outcome: InteractionOutcome) -> None`: Adjust local trust based on outcome

---

### 3. TrustMatrix (Entity)

**Purpose**: Encapsulates the N×N trust matrix and provides matrix operations.

**Attributes**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `matrix` | Tensor[N, N] | PyTorch tensor of trust values | All values in [0.0, 1.0] |
| `peer_mapping` | Dict[PeerID, int] | Maps peer IDs to matrix indices | Bijective mapping |
| `normalized` | bool | Whether matrix is column-stochastic | Checked on access |

**Matrix Properties**:
- **Rows**: Represent trusters (peer i's view)
- **Columns**: Represent trustees (peer j being evaluated)
- **Element (i, j)**: Local trust that peer i assigns to peer j
- **Normalization**: Each column sums to 1.0 (column-stochastic for EigenTrust)

**Invariants**:
- Matrix is square: shape = (N, N)
- Diagonal is 0 (peers don't assign trust to themselves)
- After normalization, column sums = 1.0 (within epsilon=1e-6)
- All values non-negative

**Methods**:
- `normalize_columns() -> Tensor`: Convert to column-stochastic matrix
- `get_trust(truster: PeerID, trustee: PeerID) -> float`: Retrieve specific trust value
- `set_trust(truster: PeerID, trustee: PeerID, value: float) -> None`: Update trust value
- `to_numpy() -> np.ndarray`: Export as NumPy array for visualization

---

## Value Objects

### 4. Interaction (Value Object)

**Purpose**: Immutable record of a peer-to-peer interaction event.

**Attributes**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `source_peer_id` | UUID | Peer requesting service | Must exist in simulation |
| `target_peer_id` | UUID | Peer providing service | Must exist in simulation |
| `outcome` | InteractionOutcome | SUCCESS or FAILURE | Enum value |
| `timestamp` | datetime | When interaction occurred | Auto-set on creation |
| `interaction_id` | UUID | Unique identifier | Auto-generated |

**Immutability**: Once created, interaction records cannot be modified (append-only log).

**Validation**:
- Source and target must be different peers
- Outcome must be SUCCESS or FAILURE
- Timestamp must be ≥ simulation creation time

---

### 5. TrustScores (Value Object)

**Purpose**: Immutable result of EigenTrust algorithm execution.

**Attributes**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `scores` | Dict[PeerID, float] | Global trust score for each peer | Sum of all scores = 1.0 |
| `iteration_count` | int | Number of iterations to converge | 1 ≤ count ≤ max_iterations |
| `converged` | bool | Whether algorithm converged | True if converged |
| `convergence_epsilon` | float | Threshold used for convergence | Typically 0.001 |
| `final_delta` | float | Change in last iteration | Value < epsilon if converged |

**Invariants**:
- All scores non-negative
- Sum of scores = 1.0 (within epsilon=1e-6)
- If converged=True, then final_delta < convergence_epsilon

---

### 6. ConvergenceSnapshot (Value Object)

**Purpose**: Captures trust scores at a specific algorithm iteration for visualization.

**Attributes**:

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `iteration` | int | Iteration number | ≥ 0 |
| `trust_scores` | Dict[PeerID, float] | Trust scores at this iteration | Sum = 1.0 |
| `delta` | float | Change from previous iteration | ||t_new - t_old|| |
| `timestamp` | datetime | When snapshot taken | Sequential |

**Use Case**: Enables visualization of trust score evolution over iterations.

---

## Enumerations

### SimulationState

```python
from enum import Enum

class SimulationState(Enum):
    CREATED = "created"          # Initial state, peers configured
    RUNNING = "running"          # Algorithm executing
    COMPLETED = "completed"      # Algorithm converged successfully
    FAILED = "failed"            # Algorithm failed to converge or error occurred
```

### InteractionOutcome

```python
class InteractionOutcome(Enum):
    SUCCESS = "success"          # Peer provided good service
    FAILURE = "failure"          # Peer failed to provide service
```

---

## Relationships

### Simulation ↔ Peer (Composition)
- **Cardinality**: 1 Simulation contains 2..500 Peers
- **Lifecycle**: Peers cannot exist without parent Simulation
- **Navigation**: Bidirectional (Peer references Simulation, Simulation contains Peers)

### Simulation ↔ Interaction (Composition)
- **Cardinality**: 1 Simulation contains 0..∞ Interactions
- **Lifecycle**: Interactions are immutable records within Simulation
- **Navigation**: Unidirectional (Simulation → Interaction)

### Peer ↔ Interaction (Association)
- **Cardinality**: 1 Peer participates in 0..∞ Interactions (as source or target)
- **Lifecycle**: Independent lifecycles (Interactions reference Peers by ID)
- **Navigation**: Unidirectional (Interaction → Peer)

### Simulation ↔ TrustMatrix (Composition)
- **Cardinality**: 1 Simulation has 1 TrustMatrix
- **Lifecycle**: TrustMatrix built from Simulation's Interactions
- **Navigation**: Unidirectional (Simulation → TrustMatrix)

### TrustMatrix ↔ TrustScores (Computation)
- **Cardinality**: 1 TrustMatrix computes 1 TrustScores per algorithm run
- **Lifecycle**: TrustScores is immutable result of computation
- **Navigation**: Unidirectional (TrustMatrix → TrustScores)

---

## Data Validation Rules

### Peer Characteristics

1. **Competence Range**: `0.0 ≤ competence ≤ 1.0`
   - Error if violated: `InvalidPeerCharacteristics("Competence must be in [0.0, 1.0]")`

2. **Maliciousness Range**: `0.0 ≤ maliciousness ≤ 1.0`
   - Error if violated: `InvalidPeerCharacteristics("Maliciousness must be in [0.0, 1.0]")`

### Trust Matrix

1. **Column-Stochastic After Normalization**: `∀j: Σ_i matrix[i,j] = 1.0 ± 1e-6`
   - Error if violated: `MatrixNormalizationError("Column sums must equal 1.0")`

2. **Non-Negative Values**: `∀i,j: matrix[i,j] ≥ 0.0`
   - Error if violated: `InvalidTrustValue("Trust values must be non-negative")`

3. **Zero Diagonal**: `∀i: matrix[i,i] = 0.0`
   - Error if violated: `InvalidTrustValue("Peers cannot trust themselves")`

### Trust Scores

1. **Score Normalization**: `Σ global_trust_scores = 1.0 ± 1e-6`
   - Error if violated: `TrustScoreError("Global trust scores must sum to 1.0")`

2. **Score Range**: `∀peer: 0.0 ≤ global_trust ≤ 1.0`
   - Error if violated: `TrustScoreError("Trust scores must be in [0.0, 1.0]")`

### Simulation

1. **Minimum Peers**: `len(simulation.peers) ≥ 2`
   - Error if violated: `InsufficientPeersError("At least 2 peers required")`

2. **Interaction Peer References**: All interactions must reference existing peers
   - Error if violated: `OrphanInteractionError("Interaction references non-existent peer")`

---

## State Transitions

### Peer Trust Evolution

```
Initial State: local_trust = {} (empty)
    ↓
After Interaction (SUCCESS): local_trust[partner] += 0.1 (clamped to [0,1])
After Interaction (FAILURE): local_trust[partner] -= 0.1 (clamped to [0,1])
    ↓
Normalize: local_trust values normalized to sum to 1.0
    ↓
Aggregate: Build TrustMatrix from all peers' local_trust
    ↓
Compute: Run EigenTrust algorithm
    ↓
Final State: global_trust = eigenvector value
```

### Algorithm Convergence

```
Iteration 0: t_0 = pre_trust (uniform or biased)
    ↓
Iteration k: t_k = C^T * t_{k-1}
    ↓
Check: ||t_k - t_{k-1}|| < epsilon?
    ├─ Yes → Converged, return t_k
    └─ No → Continue to k+1 (max 100 iterations)
```

---

## Serialization Format

**File Format**: JSON for human readability, optional Pickle for PyTorch tensors

**Simulation JSON Schema**:
```json
{
  "simulation_id": "uuid-string",
  "created_at": "2025-11-15T12:00:00Z",
  "state": "completed",
  "random_seed": 42,
  "peers": [
    {
      "peer_id": "uuid-string",
      "display_name": "Peer-001",
      "competence": 0.0,
      "maliciousness": 0.0,
      "global_trust": 0.35,
      "local_trust": {
        "peer-002-uuid": 0.6,
        "peer-003-uuid": 0.4
      }
    }
  ],
  "interactions": [
    {
      "interaction_id": "uuid-string",
      "source_peer_id": "uuid-string",
      "target_peer_id": "uuid-string",
      "outcome": "success",
      "timestamp": "2025-11-15T12:01:00Z"
    }
  ],
  "trust_matrix": {
    "peer_mapping": {"peer-001-uuid": 0, "peer-002-uuid": 1},
    "matrix": [[0.0, 0.6], [0.4, 0.0]]
  },
  "convergence_history": [
    {
      "iteration": 0,
      "trust_scores": {"peer-001-uuid": 0.5, "peer-002-uuid": 0.5},
      "delta": 1.0,
      "timestamp": "2025-11-15T12:02:00Z"
    }
  ]
}
```

---

## Summary

This data model provides:
- **Clear Domain Language**: Peer, Interaction, Trust, Convergence
- **Bounded Contexts**: Simulation (aggregate), Algorithm (computation), Visualization (presentation)
- **Invariant Enforcement**: Validation rules at entity boundaries
- **State Transitions**: Explicit lifecycle management
- **Serialization**: JSON for portability, Pickle for performance

All entities follow Domain-Driven Design principles with clear responsibilities and relationships.
