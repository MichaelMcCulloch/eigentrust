"""Trust matrix column normalization for EigenTrust.

Provides functions to normalize trust matrices to column-stochastic form.
"""

import torch


def normalize_columns(matrix: torch.Tensor) -> torch.Tensor:
    """Normalize matrix columns to sum to 1.0 (column-stochastic).

    Each column j represents trust assigned TO peer j by all other peers.
    After normalization, column sums equal 1.0 (required for EigenTrust).

    Args:
        matrix: Trust matrix tensor (N×N)

    Returns:
        Column-normalized matrix tensor

    Raises:
        ValueError: If matrix contains negative values

    Example:
        >>> matrix = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
        >>> normalized = normalize_columns(matrix)
        >>> normalized.sum(dim=0)  # Column sums
        tensor([1., 1.])
    """
    # Validate non-negative values
    if (matrix < 0).any():
        raise ValueError("Trust matrix must contain only non-negative values")

    # Compute column sums
    column_sums = matrix.sum(dim=0)

    # Handle zero columns (peers with no incoming trust)
    # Replace zeros with 1.0 to avoid division by zero
    # Zero columns will remain zero after normalization
    column_sums = torch.where(column_sums == 0, torch.ones_like(column_sums), column_sums)

    # Normalize: divide each column by its sum
    normalized = matrix / column_sums.unsqueeze(0)

    return normalized
