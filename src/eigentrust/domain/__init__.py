"""Domain entities and custom exceptions for EigenTrust.

This module defines the domain model following Domain-Driven Design principles,
including custom exceptions for handling domain-specific errors.
"""


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
