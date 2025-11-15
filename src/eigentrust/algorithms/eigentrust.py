"""Core EigenTrust algorithm implementation.

Computes global trust scores using power iteration method.
"""

from datetime import datetime

import torch

from eigentrust.algorithms.convergence import check_convergence


def compute_eigentrust(
    trust_matrix: torch.Tensor,
    pre_trust: torch.Tensor,
    max_iterations: int = 100,
    epsilon: float = 0.001,
    norm_type: str = "l1",
    alpha: float = 0.15,
) -> tuple[torch.Tensor, int, bool]:
    """Compute global trust scores using EigenTrust power iteration with damping.

    Implements the EigenTrust algorithm from Kamvar et al. 2003:
        t_{k+1} = (1 - α) * C^T * t_k + α * p

    Where:
        - C is the column-normalized trust matrix
        - t is the trust vector
        - p is the pre-trust vector (prior distribution)
        - α is the damping factor (teleportation probability)

    The damping factor prevents convergence to uniform distribution and
    ensures that pre-trust influences the final scores.

    Args:
        trust_matrix: Column-stochastic trust matrix (N×N)
        pre_trust: Pre-trust/prior distribution vector (N,)
        max_iterations: Maximum number of iterations
        epsilon: Convergence threshold
        norm_type: Type of norm for convergence check ('l1' or 'l2')
        alpha: Damping factor in [0, 1]. Higher values give more weight to pre-trust.
            Typical value is 0.15 (same as PageRank). Set to 0.0 to disable damping.

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
        raise ValueError(
            f"Pre-trust vector size ({pre_trust.shape[0]}) must match matrix size ({n})"
        )

    # Ensure pre-trust sums to 1.0
    if not torch.allclose(pre_trust.sum(), torch.tensor(1.0), atol=1e-6):
        pre_trust = pre_trust / pre_trust.sum()

    # Initialize trust vector
    t = pre_trust.clone()

    # Power iteration with damping
    for iteration in range(max_iterations):
        # Compute next trust vector with damping:
        # t_new = (1 - alpha) * C^T * t + alpha * p
        trust_propagation = torch.matmul(trust_matrix.T, t)
        t_new = (1.0 - alpha) * trust_propagation + alpha * pre_trust

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


def compute_eigentrust_with_history(
    trust_matrix: torch.Tensor,
    pre_trust: torch.Tensor,
    peer_ids: list[str],
    max_iterations: int = 100,
    epsilon: float = 0.001,
    norm_type: str = "l1",
    alpha: float = 0.15,
) -> tuple[torch.Tensor, int, bool, list[dict]]:
    """Compute EigenTrust with iteration-by-iteration history tracking.

    Args:
        trust_matrix: Column-stochastic trust matrix (N×N)
        pre_trust: Pre-trust/prior distribution vector (N,)
        peer_ids: List of peer IDs corresponding to matrix indices
        max_iterations: Maximum number of iterations
        epsilon: Convergence threshold
        norm_type: Type of norm for convergence check
        alpha: Damping factor for pre-trust (default: 0.15)

    Returns:
        Tuple of (global_trust, iterations, converged, history):
            - global_trust: Final trust score vector
            - iterations: Number of iterations executed
            - converged: Whether algorithm converged
            - history: List of ConvergenceSnapshot dicts per iteration
    """
    # Validate inputs
    if trust_matrix.dim() != 2 or trust_matrix.shape[0] != trust_matrix.shape[1]:
        raise ValueError("Trust matrix must be square")

    n = trust_matrix.shape[0]
    if pre_trust.shape[0] != n:
        raise ValueError(
            f"Pre-trust vector size ({pre_trust.shape[0]}) must match matrix size ({n})"
        )

    if len(peer_ids) != n:
        raise ValueError(f"Number of peer IDs ({len(peer_ids)}) must match matrix size ({n})")

    # Ensure pre-trust sums to 1.0
    if not torch.allclose(pre_trust.sum(), torch.tensor(1.0), atol=1e-6):
        pre_trust = pre_trust / pre_trust.sum()

    # Initialize trust vector and history
    t = pre_trust.clone()
    history = []

    # Record initial state (iteration 0)
    trust_scores_dict = {peer_ids[i]: float(t[i].item()) for i in range(n)}
    history.append(
        {
            "iteration": 0,
            "trust_scores": trust_scores_dict,
            "delta": 1.0,  # Initial delta is large
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    # Power iteration with damping
    for iteration in range(max_iterations):
        # Compute next trust vector with damping:
        # t_new = (1 - alpha) * C^T * t + alpha * p
        trust_propagation = torch.matmul(trust_matrix.T, t)
        t_new = (1.0 - alpha) * trust_propagation + alpha * pre_trust

        # Normalize to ensure sum = 1.0
        t_new = t_new / t_new.sum()

        # Check convergence
        status = check_convergence(t, t_new, epsilon, norm_type=norm_type)

        # Record this iteration
        trust_scores_dict = {peer_ids[i]: float(t_new[i].item()) for i in range(n)}
        history.append(
            {
                "iteration": iteration + 1,
                "trust_scores": trust_scores_dict,
                "delta": status.delta,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        if status.converged:
            return t_new, iteration + 1, True, history

        # Update for next iteration
        t = t_new

    # Max iterations reached without convergence
    return t, max_iterations, False, history
