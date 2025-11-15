"""Domain entities and custom exceptions for EigenTrust.

This module defines the domain model following Domain-Driven Design principles,
including custom exceptions for handling domain-specific errors.
"""

from datetime import datetime
from typing import Dict, List, Optional


# Value Objects


class TrustScores:
    """Value object representing computed global trust scores.

    Immutable result of EigenTrust algorithm execution.

    Attributes:
        scores: Dictionary mapping peer IDs to global trust scores
        iteration_count: Number of iterations to converge
        converged: Whether algorithm converged
        convergence_epsilon: Threshold used for convergence
        final_delta: Change in last iteration
        history: Optional list of convergence snapshots
    """

    def __init__(
        self,
        scores: Dict[str, float],
        iteration_count: int,
        converged: bool,
        convergence_epsilon: float,
        final_delta: float,
        history: Optional[List["ConvergenceSnapshot"]] = None
    ):
        """Initialize trust scores.

        Args:
            scores: Peer ID to trust score mapping
            iteration_count: Number of iterations executed
            converged: Whether convergence was achieved
            convergence_epsilon: Convergence threshold used
            final_delta: Final iteration delta
            history: Optional convergence history

        Raises:
            TrustScoreError: If scores violate invariants
        """
        # Validate scores sum to 1.0
        total = sum(scores.values())
        if abs(total - 1.0) > 1e-6:
            raise TrustScoreError(
                f"Global trust scores must sum to 1.0, got {total}",
                scores,
                total
            )

        # Validate all scores are non-negative
        if any(score < 0.0 for score in scores.values()):
            raise TrustScoreError(
                "All trust scores must be non-negative",
                scores,
                total
            )

        # Validate convergence consistency
        if converged and final_delta >= convergence_epsilon:
            raise ValueError(
                f"Convergence inconsistency: marked converged but delta ({final_delta}) >= epsilon ({convergence_epsilon})"
            )

        object.__setattr__(self, 'scores', scores.copy())
        object.__setattr__(self, 'iteration_count', iteration_count)
        object.__setattr__(self, 'converged', converged)
        object.__setattr__(self, 'convergence_epsilon', convergence_epsilon)
        object.__setattr__(self, 'final_delta', final_delta)
        object.__setattr__(self, 'history', history.copy() if history else [])

    def __setattr__(self, name, value):
        """Prevent modification of attributes (immutability)."""
        raise AttributeError("Cannot modify immutable TrustScores object")

    def get_score(self, peer_id: str) -> float:
        """Get trust score for a specific peer.

        Args:
            peer_id: ID of peer

        Returns:
            Global trust score

        Raises:
            KeyError: If peer ID not found
        """
        return self.scores[peer_id]

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "scores": self.scores,
            "iteration_count": self.iteration_count,
            "converged": self.converged,
            "convergence_epsilon": self.convergence_epsilon,
            "final_delta": self.final_delta,
        }

    def __repr__(self) -> str:
        """Return string representation."""
        status = "converged" if self.converged else "not converged"
        return f"TrustScores({len(self.scores)} peers, {self.iteration_count} iterations, {status})"


class ConvergenceSnapshot:
    """Value object capturing trust scores at a specific iteration.

    Used for tracking trust score evolution during algorithm execution.

    Attributes:
        iteration: Iteration number
        trust_scores: Trust scores at this iteration
        delta: Change from previous iteration
        timestamp: When snapshot was taken
    """

    def __init__(
        self,
        iteration: int,
        trust_scores: Dict[str, float],
        delta: float,
        timestamp: Optional[datetime] = None
    ):
        """Initialize convergence snapshot.

        Args:
            iteration: Iteration number (0-indexed)
            trust_scores: Trust scores at this iteration
            delta: Norm of change from previous iteration
            timestamp: Optional timestamp (auto-set if not provided)

        Raises:
            ValueError: If iteration < 0 or delta < 0
        """
        if iteration < 0:
            raise ValueError(f"Iteration must be non-negative, got {iteration}")

        if delta < 0:
            raise ValueError(f"Delta must be non-negative, got {delta}")

        # Validate scores sum to 1.0
        total = sum(trust_scores.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Trust scores must sum to 1.0, got {total}")

        object.__setattr__(self, 'iteration', iteration)
        object.__setattr__(self, 'trust_scores', trust_scores.copy())
        object.__setattr__(self, 'delta', delta)
        object.__setattr__(self, 'timestamp', timestamp or datetime.utcnow())

    def __setattr__(self, name, value):
        """Prevent modification of attributes (immutability)."""
        raise AttributeError("Cannot modify immutable ConvergenceSnapshot object")

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "iteration": self.iteration,
            "trust_scores": self.trust_scores,
            "delta": self.delta,
            "timestamp": self.timestamp.isoformat(),
        }

    def __repr__(self) -> str:
        """Return string representation."""
        return f"ConvergenceSnapshot(iteration={self.iteration}, delta={self.delta:.6f})"


# Custom Exceptions


class EigenTrustError(Exception):
    """Base exception for all EigenTrust errors."""

    pass


class ConvergenceError(EigenTrustError):
    """Raised when EigenTrust algorithm fails to converge."""

    def __init__(
        self,
        message: str,
        iterations: int,
        final_delta: float,
        epsilon: float,
    ):
        """Initialize convergence error with context.

        Args:
            message: Human-readable error description
            iterations: Number of iterations attempted
            final_delta: Final change in trust scores
            epsilon: Convergence threshold
        """
        super().__init__(message)
        self.iterations = iterations
        self.final_delta = final_delta
        self.epsilon = epsilon


class InvalidPeerCharacteristics(EigenTrustError):
    """Raised when peer characteristics are outside valid range [0.0, 1.0]."""

    def __init__(self, message: str, competence: float, maliciousness: float):
        """Initialize invalid characteristics error.

        Args:
            message: Human-readable error description
            competence: Invalid competence value
            maliciousness: Invalid maliciousness value
        """
        super().__init__(message)
        self.competence = competence
        self.maliciousness = maliciousness


class MatrixNormalizationError(EigenTrustError):
    """Raised when trust matrix cannot be normalized to column-stochastic form."""

    def __init__(self, message: str, column_sums: list[float]):
        """Initialize matrix normalization error.

        Args:
            message: Human-readable error description
            column_sums: List of column sums that violate normalization
        """
        super().__init__(message)
        self.column_sums = column_sums


class InvalidTrustValue(EigenTrustError):
    """Raised when trust value is negative or otherwise invalid."""

    def __init__(self, message: str, value: float, peer_i: str, peer_j: str):
        """Initialize invalid trust value error.

        Args:
            message: Human-readable error description
            value: Invalid trust value
            peer_i: Source peer ID
            peer_j: Target peer ID
        """
        super().__init__(message)
        self.value = value
        self.peer_i = peer_i
        self.peer_j = peer_j


class InsufficientPeersError(EigenTrustError):
    """Raised when simulation has insufficient peers (minimum 2 required)."""

    def __init__(self, message: str, peer_count: int):
        """Initialize insufficient peers error.

        Args:
            message: Human-readable error description
            peer_count: Actual number of peers
        """
        super().__init__(message)
        self.peer_count = peer_count


class OrphanInteractionError(EigenTrustError):
    """Raised when interaction references non-existent peer."""

    def __init__(self, message: str, peer_id: str):
        """Initialize orphan interaction error.

        Args:
            message: Human-readable error description
            peer_id: ID of non-existent peer
        """
        super().__init__(message)
        self.peer_id = peer_id


class InsufficientInteractions(EigenTrustError):
    """Raised when trying to run algorithm without interaction history."""

    def __init__(self, message: str, interaction_count: int):
        """Initialize insufficient interactions error.

        Args:
            message: Human-readable error description
            interaction_count: Actual number of interactions
        """
        super().__init__(message)
        self.interaction_count = interaction_count


class TrustScoreError(EigenTrustError):
    """Raised when trust scores violate invariants (e.g., sum != 1.0)."""

    def __init__(self, message: str, scores: dict[str, float], total: float):
        """Initialize trust score error.

        Args:
            message: Human-readable error description
            scores: Peer ID to trust score mapping
            total: Sum of all trust scores
        """
        super().__init__(message)
        self.scores = scores
        self.total = total
