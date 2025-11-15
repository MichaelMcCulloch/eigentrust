"""Core EigenTrust algorithm implementation.

Computes global trust scores using power iteration method.
"""

import torch
from typing import Tuple

from eigentrust.algorithms.convergence import check_convergence


def compute_eigentrust(
    trust_matrix: torch.Tensor,
    pre_trust: torch.Tensor,
    max_iterations: int = 100,
    epsilon: float = 0.001,
    norm_type: str = 'l1'
) -> Tuple[torch.Tensor, int, bool]:
    """Compute global trust scores using EigenTrust power iteration.

    Implements the EigenTrust algorithm from Kamvar et al. 2003:
        t_{k+1} = C^T * t_k

    Where C is the column-normalized trust matrix and t is the trust vector.
    The algorithm iterates until convergence or max_iterations is reached.

    Args:
        trust_matrix: Column-stochastic trust matrix (N×N)
        pre_trust: Initial trust vector (N,)
        max_iterations: Maximum number of iterations
        epsilon: Convergence threshold
        norm_type: Type of norm for convergence check ('l1' or 'l2')

    Returns:
        Tuple of (global_trust, iterations, converged):
            - global_trust: Final trust score vector
            - iterations: Number of iterations executed
            - converged: Whether algorithm converged

    Example:
        >>> trust_matrix = torch.tensor([[0.0, 0.5], [1.0, 0.5]])
        >>> pre_trust = torch.tensor([0.5, 0.5])
        >>> global_trust, iters, converged = compute_eigentrust(
        ...     trust_matrix, pre_trust, max_iterations=100, epsilon=0.001
        ... )
        >>> converged
        True
        >>> global_trust.sum()  # Should sum to 1.0
        tensor(1.)
    """
    # Validate inputs
    if trust_matrix.dim() != 2 or trust_matrix.shape[0] != trust_matrix.shape[1]:
        raise ValueError("Trust matrix must be square")

    n = trust_matrix.shape[0]
    if pre_trust.shape[0] != n:
        raise ValueError(f"Pre-trust vector size ({pre_trust.shape[0]}) must match matrix size ({n})")

    # Ensure pre-trust sums to 1.0
    if not torch.allclose(pre_trust.sum(), torch.tensor(1.0), atol=1e-6):
        pre_trust = pre_trust / pre_trust.sum()

    # Initialize trust vector
    t = pre_trust.clone()

    # Power iteration
    for iteration in range(max_iterations):
        # Compute next trust vector: t_new = C^T * t
        t_new = torch.matmul(trust_matrix.T, t)

        # Normalize to ensure sum = 1.0 (handle numerical drift)
        t_new = t_new / t_new.sum()

        # Check convergence
        status = check_convergence(t, t_new, epsilon, norm_type=norm_type)

        if status.converged:
            return t_new, iteration + 1, True

        # Update for next iteration
        t = t_new

    # Max iterations reached without convergence
    return t, max_iterations, False
