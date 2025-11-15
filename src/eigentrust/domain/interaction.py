"""Interaction entities and enums for EigenTrust.

Defines interaction outcomes and interaction records between peers.
"""

import uuid
from datetime import datetime
from enum import Enum


class InteractionOutcome(Enum):
    """Enumeration of possible interaction outcomes."""

    SUCCESS = "success"
    FAILURE = "failure"


class Interaction:
    """Value object representing a peer-to-peer interaction event.

    Immutable record of an interaction between two peers.

    Attributes:
        interaction_id: Unique identifier for this interaction
        source_peer_id: Peer requesting service
        target_peer_id: Peer providing service
        outcome: SUCCESS or FAILURE
        timestamp: When the interaction occurred
    """

    def __init__(
        self,
        source_peer_id: str,
        target_peer_id: str,
        outcome: InteractionOutcome,
        interaction_id: str | None = None,
        timestamp: datetime | None = None,
    ):
        """Initialize an interaction record.

        Args:
            source_peer_id: ID of peer requesting service
            target_peer_id: ID of peer providing service
            outcome: Result of the interaction (SUCCESS or FAILURE)
            interaction_id: Optional ID (auto-generated if not provided)
            timestamp: Optional timestamp (auto-set to now if not provided)

        Raises:
            ValueError: If source and target are the same peer
        """
        if source_peer_id == target_peer_id:
            raise ValueError("Source and target must be different")

        object.__setattr__(
            self,
            "interaction_id",
            interaction_id if interaction_id is not None else str(uuid.uuid4()),
        )
        object.__setattr__(self, "source_peer_id", source_peer_id)
        object.__setattr__(self, "target_peer_id", target_peer_id)
        object.__setattr__(self, "outcome", outcome)
        object.__setattr__(
            self, "timestamp", timestamp if timestamp is not None else datetime.utcnow()
        )

    def __setattr__(self, name, value):
        """Prevent modification of attributes (immutability)."""
        raise AttributeError("Cannot modify immutable Interaction object")

    def to_dict(self) -> dict:
        """Convert interaction to dictionary for serialization."""
        return {
            "interaction_id": self.interaction_id,
            "source_peer_id": self.source_peer_id,
            "target_peer_id": self.target_peer_id,
            "outcome": self.outcome.value,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Interaction":
        """Create interaction from dictionary.

        Args:
            data: Dictionary containing interaction data

        Returns:
            New Interaction instance
        """
        return cls(
            interaction_id=data["interaction_id"],
            source_peer_id=data["source_peer_id"],
            target_peer_id=data["target_peer_id"],
            outcome=InteractionOutcome(data["outcome"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )

    def __repr__(self) -> str:
        """Return string representation of interaction."""
        return (
            f"Interaction({self.source_peer_id[:8]}... → "
            f"{self.target_peer_id[:8]}..., {self.outcome.value})"
        )

    def __eq__(self, other: object) -> bool:
        """Check equality based on interaction_id."""
        if not isinstance(other, Interaction):
            return False
        return self.interaction_id == other.interaction_id

    def __hash__(self) -> int:
        """Hash based on interaction_id."""
        return hash(self.interaction_id)
