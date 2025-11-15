"""Simulation aggregate root for EigenTrust.

The Simulation is the root entity that encapsulates the entire simulation state
and enforces invariants across all contained entities.
"""

import uuid
import random
import torch
from enum import Enum
from datetime import datetime
from typing import Optional, List

from eigentrust.domain import (
    InsufficientPeersError,
    TrustScores,
    ConvergenceSnapshot,
    OrphanInteractionError
)
from eigentrust.domain.peer import Peer
from eigentrust.domain.interaction import Interaction, InteractionOutcome
from eigentrust.domain.trust_matrix import TrustMatrix
from eigentrust.algorithms.eigentrust import compute_eigentrust, compute_eigentrust_with_history
from eigentrust.algorithms.normalization import normalize_columns
from eigentrust.simulation.interactions import simulate_interactions


class SimulationState(Enum):
    """Enumeration of possible simulation states."""

    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Simulation:
    """Aggregate root for EigenTrust simulation.

    Encapsulates all simulation state including peers, interactions,
    and algorithm execution results.

    Attributes:
        simulation_id: Unique identifier for simulation
        created_at: Timestamp of creation
        state: Current simulation state
        peers: List of peers in the network
        interactions: History of all peer interactions
        convergence_history: Iteration-by-iteration trust evolution
        random_seed: Optional seed for reproducibility
    """

    def __init__(
        self,
        simulation_id: Optional[str] = None,
        random_seed: Optional[int] = None,
    ):
        """Initialize a new simulation.

        Args:
            simulation_id: Optional ID (auto-generated if not provided)
            random_seed: Optional random seed for reproducibility
        """
        self.simulation_id = (
            simulation_id if simulation_id is not None else str(uuid.uuid4())
        )
        self.created_at = datetime.utcnow()
        self.state = SimulationState.CREATED
        self.peers: list[Peer] = []
        self.interactions: list[Interaction] = []
        self.convergence_history: list = []  # Will be ConvergenceSnapshot objects
        self.random_seed = random_seed

        # Set random seed if provided
        if random_seed is not None:
            random.seed(random_seed)

    def add_peer(
        self,
        competence: float,
        maliciousness: float,
        peer_id: Optional[str] = None,
    ) -> Peer:
        """Add a new peer to the simulation.

        Args:
            competence: Peer's incompetence level [0.0, 1.0]
            maliciousness: Peer's malicious intent [0.0, 1.0]
            peer_id: Optional peer ID

        Returns:
            The newly created Peer

        Raises:
            InvalidPeerCharacteristics: If characteristics invalid
        """
        peer = Peer(
            competence=competence,
            maliciousness=maliciousness,
            peer_id=peer_id,
        )
        self.peers.append(peer)
        return peer

    def add_interaction(self, interaction: Interaction) -> None:
        """Add an interaction to the simulation.

        Args:
            interaction: Interaction to add

        Raises:
            OrphanInteractionError: If interaction references unknown peer
        """
        peer_ids = {p.peer_id for p in self.peers}

        if interaction.source_peer_id not in peer_ids:
            raise OrphanInteractionError(
                f"Source peer {interaction.source_peer_id} not in simulation",
                interaction.source_peer_id
            )

        if interaction.target_peer_id not in peer_ids:
            raise OrphanInteractionError(
                f"Target peer {interaction.target_peer_id} not in simulation",
                interaction.target_peer_id
            )

        self.interactions.append(interaction)

    def run_algorithm(
        self,
        max_iterations: int = 100,
        epsilon: float = 0.001,
        track_history: bool = False
    ) -> TrustScores:
        """Execute the EigenTrust algorithm.

        Args:
            max_iterations: Maximum number of iterations
            epsilon: Convergence threshold
            track_history: Whether to track convergence history

        Returns:
            TrustScores object with global trust scores and convergence info

        Raises:
            InsufficientPeersError: If fewer than 2 peers in network
        """
        if len(self.peers) < 2:
            raise InsufficientPeersError(
                "At least 2 peers required to run algorithm",
                peer_count=len(self.peers),
            )

        self.state = SimulationState.RUNNING

        try:
            # Build trust matrix from peer local trust or interactions
            trust_matrix = self._build_trust_matrix()

            # Normalize to column-stochastic
            normalized_matrix = normalize_columns(trust_matrix.matrix)

            # Initialize pre-trust (uniform distribution)
            n = len(self.peers)
            pre_trust = torch.ones(n) / n

            # Run EigenTrust algorithm with or without history tracking
            if track_history:
                peer_ids = list(trust_matrix.peer_mapping.keys())
                global_trust_vector, iterations, converged, history = compute_eigentrust_with_history(
                    trust_matrix=normalized_matrix,
                    pre_trust=pre_trust,
                    peer_ids=peer_ids,
                    max_iterations=max_iterations,
                    epsilon=epsilon
                )
                # Store convergence history
                self.convergence_history = history
            else:
                global_trust_vector, iterations, converged = compute_eigentrust(
                    trust_matrix=normalized_matrix,
                    pre_trust=pre_trust,
                    max_iterations=max_iterations,
                    epsilon=epsilon
                )

            # Convert tensor to dictionary mapping peer IDs to scores
            peer_ids = list(trust_matrix.peer_mapping.keys())
            scores = {
                peer_id: float(global_trust_vector[idx].item())
                for peer_id, idx in trust_matrix.peer_mapping.items()
            }

            # Update peers with global trust scores
            for peer in self.peers:
                peer.global_trust = scores[peer.peer_id]

            # Create TrustScores result
            from eigentrust.algorithms.convergence import check_convergence
            final_delta = check_convergence(
                pre_trust, global_trust_vector, epsilon
            ).delta if iterations > 1 else 1.0

            trust_scores = TrustScores(
                scores=scores,
                iteration_count=iterations,
                converged=converged,
                convergence_epsilon=epsilon,
                final_delta=final_delta,
                history=[] if not track_history else self.convergence_history
            )

            self.state = SimulationState.COMPLETED
            return trust_scores

        except Exception as e:
            self.state = SimulationState.FAILED
            raise

    def _build_trust_matrix(self) -> TrustMatrix:
        """Build trust matrix from peer local trust or interactions.

        Returns:
            TrustMatrix entity

        Note:
            If peers have no local trust values, they will be initialized
            based on interaction history (if available) or uniformly.
        """
        n = len(self.peers)
        matrix = torch.zeros(n, n, dtype=torch.float32)
        peer_mapping = {peer.peer_id: idx for idx, peer in enumerate(self.peers)}

        # Build matrix from peer local trust
        for i, peer_i in enumerate(self.peers):
            if peer_i.local_trust:
                # Peer has local trust values
                for peer_j_id, trust_value in peer_i.local_trust.items():
                    if peer_j_id in peer_mapping:
                        j = peer_mapping[peer_j_id]
                        matrix[i, j] = trust_value
            else:
                # Initialize local trust from interactions if available
                self._update_peer_local_trust_from_interactions(peer_i)
                for peer_j_id, trust_value in peer_i.local_trust.items():
                    if peer_j_id in peer_mapping:
                        j = peer_mapping[peer_j_id]
                        matrix[i, j] = trust_value

        return TrustMatrix(matrix=matrix, peer_mapping=peer_mapping)

    def _update_peer_local_trust_from_interactions(self, peer: Peer) -> None:
        """Update peer's local trust based on interaction history.

        Args:
            peer: Peer to update
        """
        # Find interactions where this peer was the source (requester)
        peer_interactions = [
            interaction for interaction in self.interactions
            if interaction.source_peer_id == peer.peer_id
        ]

        if not peer_interactions:
            # No interactions: initialize uniform trust
            other_peers = [p for p in self.peers if p.peer_id != peer.peer_id]
            if other_peers:
                uniform_trust = 1.0 / len(other_peers)
                peer.local_trust = {p.peer_id: uniform_trust for p in other_peers}
            return

        # Count successes and failures per target peer
        from collections import defaultdict
        interaction_counts = defaultdict(lambda: {"success": 0, "failure": 0})

        for interaction in peer_interactions:
            target_id = interaction.target_peer_id
            if interaction.outcome == InteractionOutcome.SUCCESS:
                interaction_counts[target_id]["success"] += 1
            else:
                interaction_counts[target_id]["failure"] += 1

        # Compute local trust: success_rate
        local_trust = {}
        for target_id, counts in interaction_counts.items():
            total = counts["success"] + counts["failure"]
            if total > 0:
                success_rate = counts["success"] / total
                local_trust[target_id] = success_rate

        # Normalize to sum to 1.0
        total_trust = sum(local_trust.values())
        if total_trust > 0:
            peer.local_trust = {
                peer_id: trust / total_trust
                for peer_id, trust in local_trust.items()
            }
        else:
            # All failures: assign minimal trust uniformly
            peer.local_trust = {
                peer_id: 1.0 / len(local_trust)
                for peer_id in local_trust.keys()
            }

    def simulate_interactions(self, count: int) -> list[Interaction]:
        """Simulate random peer-to-peer interactions.

        Creates random interactions between peers based on their behavioral
        characteristics (competence and maliciousness).

        Args:
            count: Number of interactions to simulate

        Returns:
            List of simulated interactions

        Raises:
            InsufficientPeersError: If fewer than 2 peers in network
        """
        if len(self.peers) < 2:
            raise InsufficientPeersError(
                "At least 2 peers required to simulate interactions",
                peer_count=len(self.peers),
            )

        # Use imported simulation function
        new_interactions = simulate_interactions(
            peers=self.peers,
            num_interactions=count,
            seed=self.random_seed
        )

        # Add interactions to simulation history
        for interaction in new_interactions:
            self.interactions.append(interaction)

            # Update local trust for source peer based on outcome
            source_peer = next(p for p in self.peers if p.peer_id == interaction.source_peer_id)
            success = interaction.outcome == InteractionOutcome.SUCCESS
            source_peer.update_local_trust(interaction.target_peer_id, success)

        return new_interactions

    def to_dict(self) -> dict:
        """Convert simulation to dictionary for serialization."""
        return {
            "simulation_id": self.simulation_id,
            "created_at": self.created_at.isoformat(),
            "state": self.state.value,
            "random_seed": self.random_seed,
            "peers": [
                {
                    "peer_id": p.peer_id,
                    "display_name": p.display_name,
                    "competence": p.competence,
                    "maliciousness": p.maliciousness,
                    "global_trust": p.global_trust,
                    "local_trust": p.local_trust,
                }
                for p in self.peers
            ],
            "interactions": [i.to_dict() for i in self.interactions],
            "convergence_history": self.convergence_history,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Simulation":
        """Create simulation from dictionary.

        Args:
            data: Dictionary containing simulation data

        Returns:
            New Simulation instance
        """
        sim = cls(
            simulation_id=data["simulation_id"],
            random_seed=data.get("random_seed"),
        )
        sim.created_at = datetime.fromisoformat(data["created_at"])
        sim.state = SimulationState(data["state"])

        # Recreate peers
        for peer_data in data["peers"]:
            peer = Peer(
                competence=peer_data["competence"],
                maliciousness=peer_data["maliciousness"],
                peer_id=peer_data["peer_id"],
                display_name=peer_data["display_name"],
            )
            peer.global_trust = peer_data.get("global_trust")
            peer.local_trust = peer_data.get("local_trust", {})
            sim.peers.append(peer)

        # Recreate interactions
        for interaction_data in data["interactions"]:
            interaction = Interaction.from_dict(interaction_data)
            sim.interactions.append(interaction)

        sim.convergence_history = data.get("convergence_history", [])

        return sim

    def __repr__(self) -> str:
        """Return string representation of simulation."""
        return (
            f"Simulation(id={self.simulation_id[:8]}..., "
            f"state={self.state.value}, "
            f"peers={len(self.peers)}, "
            f"interactions={len(self.interactions)})"
        )
