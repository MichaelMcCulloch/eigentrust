"""TrustMatrix entity for EigenTrust.

Encapsulates the N×N trust matrix and provides matrix operations.
"""


import numpy as np
import torch


class TrustMatrix:
    """Entity representing the N×N peer trust matrix.

    Encapsulates trust values between peers with matrix operations.

    Attributes:
        matrix: PyTorch tensor of trust values (N×N)
        peer_mapping: Maps peer IDs to matrix indices
        normalized: Whether matrix is column-stochastic
    """

    def __init__(
        self, matrix: torch.Tensor, peer_mapping: dict[str, int], normalized: bool = False
    ):
        """Initialize trust matrix.

        Args:
            matrix: PyTorch tensor of trust values
            peer_mapping: Dictionary mapping peer IDs to matrix indices
            normalized: Whether matrix is already column-normalized

        Raises:
            ValueError: If matrix is not square or contains invalid values
        """
        # Validate square matrix
        if matrix.dim() != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError("Trust matrix must be square")

        # Validate non-negative values
        if (matrix < 0).any():
            raise ValueError("Trust matrix must contain only non-negative values")

        # Validate peer_mapping size matches matrix
        if len(peer_mapping) != matrix.shape[0]:
            raise ValueError("Peer mapping size must match matrix dimensions")

        self._matrix = matrix.clone()  # Store a copy to prevent external modification
        self._peer_mapping = peer_mapping.copy()
        self._normalized = normalized

    @property
    def matrix(self) -> torch.Tensor:
        """Get trust matrix tensor."""
        return self._matrix

    @property
    def peer_mapping(self) -> dict[str, int]:
        """Get peer ID to matrix index mapping."""
        return self._peer_mapping.copy()

    @property
    def normalized(self) -> bool:
        """Check if matrix is column-stochastic."""
        return self._normalized

    def get_trust(self, truster_id: str, trustee_id: str) -> float:
        """Get trust value from truster to trustee.

        Args:
            truster_id: ID of peer assigning trust (row)
            trustee_id: ID of peer being trusted (column)

        Returns:
            Trust value in [0, 1]

        Raises:
            KeyError: If peer ID not in mapping
        """
        i = self._peer_mapping[truster_id]
        j = self._peer_mapping[trustee_id]
        return float(self._matrix[i, j].item())

    def set_trust(self, truster_id: str, trustee_id: str, value: float) -> None:
        """Set trust value from truster to trustee.

        Args:
            truster_id: ID of peer assigning trust
            trustee_id: ID of peer being trusted
            value: Trust value to set

        Raises:
            ValueError: If value not in [0, 1]
            KeyError: If peer ID not in mapping
        """
        if value < 0.0 or value > 1.0:
            raise ValueError(f"Trust value must be in range [0, 1], got {value}")

        i = self._peer_mapping[truster_id]
        j = self._peer_mapping[trustee_id]
        self._matrix[i, j] = value
        self._normalized = False  # Setting values invalidates normalization

    def to_numpy(self) -> np.ndarray:
        """Export matrix as NumPy array for visualization.

        Returns:
            NumPy array of trust values
        """
        return self._matrix.detach().cpu().numpy()

    def normalize_columns(self) -> "TrustMatrix":
        """Normalize matrix to column-stochastic form.

        Each column will sum to 1.0 (required for EigenTrust).

        Returns:
            New TrustMatrix with normalized columns

        Raises:
            ValueError: If normalization fails
        """
        # Compute column sums
        col_sums = self._matrix.sum(dim=0)

        # Handle zero columns (no trust assigned to that peer)
        # Replace zeros with 1.0 to avoid division by zero
        col_sums = torch.where(col_sums == 0, torch.ones_like(col_sums), col_sums)

        # Normalize each column
        normalized_matrix = self._matrix / col_sums.unsqueeze(0)

        # Verify normalization (column sums should be 1.0)
        new_col_sums = normalized_matrix.sum(dim=0)
        if not torch.allclose(new_col_sums, torch.ones_like(new_col_sums), atol=1e-6):
            raise ValueError("Matrix normalization failed: columns do not sum to 1.0")

        return TrustMatrix(
            matrix=normalized_matrix, peer_mapping=self._peer_mapping, normalized=True
        )

    def __repr__(self) -> str:
        """Return string representation of trust matrix."""
        n = self._matrix.shape[0]
        return f"TrustMatrix({n}×{n}, normalized={self._normalized})"

    def __eq__(self, other: object) -> bool:
        """Check equality based on matrix values."""
        if not isinstance(other, TrustMatrix):
            return False
        return torch.allclose(self._matrix, other._matrix, atol=1e-6)
