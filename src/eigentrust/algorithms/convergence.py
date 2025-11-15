"""Convergence detection for EigenTrust algorithm.

Provides functions to check if trust scores have converged.
"""

from typing import NamedTuple

import torch


class ConvergenceStatus(NamedTuple):
    """Status of convergence check.

    Attributes:
        converged: Whether trust scores have converged
        delta: Magnitude of change (norm of difference)
    """

    converged: bool
    delta: float


def check_convergence(
    t_old: torch.Tensor, t_new: torch.Tensor, epsilon: float, norm_type: str = "l1"
) -> ConvergenceStatus:
    """Check if trust scores have converged.

    Convergence is detected when the change between iterations
    is below the threshold epsilon.

    Args:
        t_old: Previous iteration trust scores
        t_new: Current iteration trust scores
        epsilon: Convergence threshold
        norm_type: Type of norm to use ('l1' or 'l2')

    Returns:
        ConvergenceStatus with converged flag and delta value

    Raises:
        ValueError: If vectors have different sizes

    Example:
        >>> t_old = torch.tensor([0.333, 0.333, 0.334])
        >>> t_new = torch.tensor([0.3331, 0.3331, 0.3338])
        >>> status = check_convergence(t_old, t_new, epsilon=0.001)
        >>> status.converged
        True
    """
    # Validate same size
    if t_old.shape != t_new.shape:
        raise ValueError(f"Trust vectors must have same size: {t_old.shape} vs {t_new.shape}")

    # Compute difference vector
    diff = t_new - t_old

    # Compute norm based on type
    if norm_type == "l1":
        delta = torch.norm(diff, p=1).item()
    elif norm_type == "l2":
        delta = torch.norm(diff, p=2).item()
    else:
        raise ValueError(f"Invalid norm type: {norm_type}. Use 'l1' or 'l2'")

    # Check convergence
    converged = delta < epsilon

    return ConvergenceStatus(converged=converged, delta=delta)
