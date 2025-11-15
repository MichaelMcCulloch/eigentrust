"""Peer entity for EigenTrust network.

Represents an individual node in the peer-to-peer network with behavioral characteristics.
"""

import uuid
from typing import Optional
from eigentrust.domain import InvalidPeerCharacteristics


class Peer:
    """Entity representing a peer in the trust network.

    Attributes:
        peer_id: Unique identifier for the peer
        competence: Incompetence level [0.0, 1.0] where 0.0 = hypercompetent
        maliciousness: Malicious intent [0.0, 1.0] where 0.0 = altruistic
        global_trust: EigenTrust-computed global trust score (None until algorithm runs)
        local_trust: Dictionary mapping peer IDs to local trust values
        display_name: Human-readable name for the peer
    """

    def __init__(
        self,
        competence: float,
        maliciousness: float,
        peer_id: Optional[str] = None,
        display_name: Optional[str] = None,
    ):
        """Initialize a new peer with characteristics.

        Args:
            competence: Incompetence level [0.0, 1.0]
            maliciousness: Malicious intent [0.0, 1.0]
            peer_id: Optional peer ID (auto-generated if not provided)
            display_name: Optional display name (auto-generated if not provided)

        Raises:
            InvalidPeerCharacteristics: If characteristics are outside [0.0, 1.0] range
        """
        # Validate characteristics
        if not (0.0 <= competence <= 1.0):
            raise InvalidPeerCharacteristics(
                f"Competence must be in [0.0, 1.0], got {competence}",
                competence=competence,
                maliciousness=maliciousness,
            )

        if not (0.0 <= maliciousness <= 1.0):
            raise InvalidPeerCharacteristics(
                f"Maliciousness must be in [0.0, 1.0], got {maliciousness}",
                competence=competence,
                maliciousness=maliciousness,
            )

        # Initialize attributes
        self.peer_id = peer_id if peer_id is not None else str(uuid.uuid4())
        self.competence = competence
        self.maliciousness = maliciousness
        self.global_trust: Optional[float] = None
        self.local_trust: dict[str, float] = {}

        # Generate display name if not provided
        if display_name is not None:
            self.display_name = display_name
        else:
            # Use last 3 characters of UUID for human-readable name
            short_id = self.peer_id.split("-")[-1][:3].upper()
            self.display_name = f"Peer-{short_id}"

    def compute_interaction_outcome(self, partner: "Peer") -> bool:
        """Compute outcome of interaction with another peer.

        The outcome is probabilistic based on this peer's characteristics:
        - Success probability = (1 - competence) * (1 - maliciousness)
        - Lower competence (more skilled) = higher success rate
        - Lower maliciousness (more altruistic) = higher cooperation rate

        Args:
            partner: The peer being interacted with

        Returns:
            True if interaction succeeds, False otherwise
        """
        import random

        # Base success rate inversely related to incompetence
        technical_success = 1.0 - self.competence

        # Maliciousness reduces likelihood of helping partner
        cooperation_factor = 1.0 - self.maliciousness

        # Combined probability
        success_prob = technical_success * cooperation_factor

        # Add small random noise to prevent determinism
        noise = random.gauss(0, 0.05)
        final_prob = max(0.0, min(1.0, success_prob + noise))

        return random.random() < final_prob

    def update_local_trust(self, partner_id: str, interaction_success: bool) -> None:
        """Update local trust for a partner based on interaction outcome.

        Successful interactions increase trust, failures decrease trust.
        Trust values are normalized to sum to 1.0 after each update.

        Args:
            partner_id: ID of the peer that was interacted with
            interaction_success: True if interaction succeeded, False otherwise
        """
        # Initialize trust if first interaction
        if partner_id not in self.local_trust:
            self.local_trust[partner_id] = 0.5  # Neutral starting trust

        # Update trust based on outcome
        trust_delta = 0.1 if interaction_success else -0.1
        new_trust = self.local_trust[partner_id] + trust_delta

        # Clamp to [0.0, 1.0]
        self.local_trust[partner_id] = max(0.0, min(1.0, new_trust))

        # Normalize trust values to sum to 1.0
        total_trust = sum(self.local_trust.values())
        if total_trust > 0:
            self.local_trust = {
                peer_id: trust / total_trust
                for peer_id, trust in self.local_trust.items()
            }

    def __repr__(self) -> str:
        """Return string representation of peer."""
        return (
            f"Peer(id={self.peer_id[:8]}..., "
            f"competence={self.competence:.2f}, "
            f"maliciousness={self.maliciousness:.2f}, "
            f"global_trust={self.global_trust})"
        )

    def __eq__(self, other: object) -> bool:
        """Check equality based on peer_id."""
        if not isinstance(other, Peer):
            return False
        return self.peer_id == other.peer_id

    def __hash__(self) -> int:
        """Hash based on peer_id for use in sets/dicts."""
        return hash(self.peer_id)
