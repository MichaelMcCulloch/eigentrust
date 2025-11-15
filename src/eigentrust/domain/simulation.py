"""Simulation aggregate root for EigenTrust.

The Simulation is the root entity that encapsulates the entire simulation state
and enforces invariants across all contained entities.
"""

import uuid
import random
from enum import Enum
from datetime import datetime
from typing import Optional
from eigentrust.domain import InsufficientPeersError
from eigentrust.domain.peer import Peer
from eigentrust.domain.interaction import Interaction, InteractionOutcome


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

    def run_algorithm(
        self,
        max_iterations: int = 100,
        epsilon: float = 0.001,
    ) -> dict[str, float]:
        """Execute the EigenTrust algorithm.

        This is a placeholder that will be implemented in Phase 4 (User Story 2).

        Args:
            max_iterations: Maximum number of iterations
            epsilon: Convergence threshold

        Returns:
            Dictionary mapping peer IDs to global trust scores

        Raises:
            InsufficientPeersError: If fewer than 2 peers in network
        """
        if len(self.peers) < 2:
            raise InsufficientPeersError(
                "At least 2 peers required to run algorithm",
                peer_count=len(self.peers),
            )

        # Placeholder - will be implemented in User Story 2
        # For now, just update state and return empty dict
        self.state = SimulationState.RUNNING
        # Algorithm implementation will go here
        self.state = SimulationState.COMPLETED

        return {}

    def simulate_interactions(self, count: int) -> list[Interaction]:
        """Simulate random peer-to-peer interactions.

        This is a placeholder that will be implemented in Phase 4 (User Story 2).

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

        # Placeholder - will be implemented in User Story 2
        return []

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
