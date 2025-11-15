"""Unit tests for EigenTrust power iteration (T033)."""

import torch

from eigentrust.algorithms.eigentrust import compute_eigentrust


def test_should_converge_for_simple_network():
    """Test that EigenTrust converges for a simple 3-peer network."""
    # Column-stochastic trust matrix
    trust_matrix = torch.tensor(
        [[0.0, 0.5, 0.5], [0.5, 0.0, 0.5], [0.5, 0.5, 0.0]], dtype=torch.float32
    )

    pre_trust = torch.ones(3) / 3.0

    global_trust, iterations, converged = compute_eigentrust(
        trust_matrix=trust_matrix, pre_trust=pre_trust, max_iterations=100, epsilon=0.001
    )

    assert converged is True
    assert iterations < 100
    assert torch.allclose(global_trust.sum(), torch.tensor(1.0), atol=1e-6)
    assert all(score >= 0.0 for score in global_trust)


def test_should_return_trust_scores_summing_to_one():
    """Test that global trust scores sum to 1.0."""
    trust_matrix = torch.tensor(
        [[0.0, 0.7, 0.3], [0.5, 0.0, 0.5], [0.4, 0.6, 0.0]], dtype=torch.float32
    )

    pre_trust = torch.ones(3) / 3.0

    global_trust, _, _ = compute_eigentrust(
        trust_matrix=trust_matrix, pre_trust=pre_trust, max_iterations=100, epsilon=0.001
    )

    assert torch.allclose(global_trust.sum(), torch.tensor(1.0), atol=1e-6)


def test_should_assign_higher_trust_to_well_connected_peers():
    """Test that peers with more incoming trust get higher scores."""
    # Peer 2 is trusted by everyone
    trust_matrix = torch.tensor(
        [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.5, 0.5, 0.0]], dtype=torch.float32
    )

    pre_trust = torch.ones(3) / 3.0

    global_trust, _, _ = compute_eigentrust(
        trust_matrix=trust_matrix, pre_trust=pre_trust, max_iterations=100, epsilon=0.001
    )

    # Peer 2 (index 2) should have highest trust
    assert global_trust[2] > global_trust[0]
    assert global_trust[2] > global_trust[1]


def test_should_handle_uniform_network():
    """Test EigenTrust on uniform network (all peers equal)."""
    n = 5
    # Uniform trust: each peer trusts all others equally
    trust_matrix = torch.ones(n, n) / (n - 1)
    trust_matrix.fill_diagonal_(0.0)

    # Renormalize columns
    trust_matrix = trust_matrix / trust_matrix.sum(dim=0, keepdim=True)

    pre_trust = torch.ones(n) / n

    global_trust, iterations, converged = compute_eigentrust(
        trust_matrix=trust_matrix, pre_trust=pre_trust, max_iterations=100, epsilon=0.001
    )

    # All peers should have equal trust (1/n)
    expected_trust = torch.ones(n) / n
    assert torch.allclose(global_trust, expected_trust, atol=0.01)
    assert converged is True


def test_should_not_converge_if_max_iterations_reached():
    """Test that convergence fails if max iterations exceeded."""
    # Difficult matrix that converges slowly
    trust_matrix = torch.tensor(
        [[0.0, 0.45, 0.55], [0.55, 0.0, 0.45], [0.45, 0.55, 0.0]], dtype=torch.float32
    )

    pre_trust = torch.ones(3) / 3.0

    # Set very low max_iterations
    global_trust, iterations, converged = compute_eigentrust(
        trust_matrix=trust_matrix, pre_trust=pre_trust, max_iterations=2, epsilon=0.001
    )

    assert converged is False
    assert iterations == 2


def test_should_handle_isolated_peer():
    """Test that algorithm handles peer with no incoming trust."""
    # Peer 0 has no incoming trust
    trust_matrix = torch.tensor(
        [[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [1.0, 1.0, 0.0]], dtype=torch.float32
    )

    # Normalize columns
    column_sums = trust_matrix.sum(dim=0)
    column_sums[column_sums == 0] = 1.0  # Prevent division by zero
    trust_matrix = trust_matrix / column_sums

    pre_trust = torch.ones(3) / 3.0

    global_trust, _, converged = compute_eigentrust(
        trust_matrix=trust_matrix, pre_trust=pre_trust, max_iterations=100, epsilon=0.001
    )

    # Peer 0 should have very low trust
    assert global_trust[0] < global_trust[1]
    assert global_trust[0] < global_trust[2]
    assert converged is True
