"""Unit tests for convergence detection (T034)."""

import pytest
import torch

from eigentrust.algorithms.convergence import check_convergence, ConvergenceStatus


def test_should_detect_convergence_when_delta_below_epsilon():
    """Test that convergence is detected when change is below threshold."""
    t_old = torch.tensor([0.333, 0.333, 0.334], dtype=torch.float32)
    t_new = torch.tensor([0.3331, 0.3331, 0.3338], dtype=torch.float32)
    epsilon = 0.001

    status = check_convergence(t_old, t_new, epsilon)

    assert status.converged is True
    assert status.delta < epsilon


def test_should_not_converge_when_delta_above_epsilon():
    """Test that convergence is not detected when change is above threshold."""
    t_old = torch.tensor([0.3, 0.3, 0.4], dtype=torch.float32)
    t_new = torch.tensor([0.35, 0.25, 0.4], dtype=torch.float32)
    epsilon = 0.001

    status = check_convergence(t_old, t_new, epsilon)

    assert status.converged is False
    assert status.delta >= epsilon


def test_should_compute_l1_norm_delta():
    """Test that delta is computed as L1 norm of difference."""
    t_old = torch.tensor([0.2, 0.3, 0.5], dtype=torch.float32)
    t_new = torch.tensor([0.25, 0.35, 0.4], dtype=torch.float32)
    epsilon = 0.5

    status = check_convergence(t_old, t_new, epsilon)

    # L1 norm = |0.25-0.2| + |0.35-0.3| + |0.4-0.5| = 0.05 + 0.05 + 0.1 = 0.2
    expected_delta = 0.2
    assert abs(status.delta - expected_delta) < 1e-6


def test_should_handle_identical_vectors():
    """Test convergence check for identical trust vectors."""
    t = torch.tensor([0.333, 0.333, 0.334], dtype=torch.float32)
    epsilon = 0.001

    status = check_convergence(t, t, epsilon)

    assert status.converged is True
    assert status.delta == 0.0


def test_should_use_l2_norm_if_specified():
    """Test that delta can be computed using L2 norm."""
    t_old = torch.tensor([0.2, 0.3, 0.5], dtype=torch.float32)
    t_new = torch.tensor([0.25, 0.35, 0.4], dtype=torch.float32)
    epsilon = 0.5

    status = check_convergence(t_old, t_new, epsilon, norm_type='l2')

    # L2 norm = sqrt((0.05)^2 + (0.05)^2 + (0.1)^2) = sqrt(0.0125) ≈ 0.1118
    expected_delta = 0.1118
    assert abs(status.delta - expected_delta) < 0.001


def test_should_reject_vectors_of_different_sizes():
    """Test that convergence check rejects vectors of different sizes."""
    t_old = torch.tensor([0.5, 0.5], dtype=torch.float32)
    t_new = torch.tensor([0.333, 0.333, 0.334], dtype=torch.float32)
    epsilon = 0.001

    with pytest.raises(ValueError, match="same size"):
        check_convergence(t_old, t_new, epsilon)
