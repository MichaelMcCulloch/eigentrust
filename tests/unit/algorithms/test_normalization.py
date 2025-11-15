"""Unit tests for trust matrix column normalization (T032)."""

import pytest
import torch

from eigentrust.algorithms.normalization import normalize_columns


def test_should_normalize_matrix_columns_to_sum_one():
    """Test that column normalization makes each column sum to 1.0."""
    matrix = torch.tensor([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0]
    ], dtype=torch.float32)

    normalized = normalize_columns(matrix)

    # Check that each column sums to 1.0
    column_sums = normalized.sum(dim=0)
    assert torch.allclose(column_sums, torch.ones(3), atol=1e-6)


def test_should_handle_zero_columns():
    """Test that normalization handles columns with all zeros."""
    matrix = torch.tensor([
        [1.0, 0.0, 3.0],
        [2.0, 0.0, 6.0],
        [3.0, 0.0, 9.0]
    ], dtype=torch.float32)

    normalized = normalize_columns(matrix)

    # First and third columns should be normalized
    assert torch.allclose(normalized[:, 0].sum(), torch.tensor(1.0), atol=1e-6)
    assert torch.allclose(normalized[:, 2].sum(), torch.tensor(1.0), atol=1e-6)

    # Second column (all zeros) should remain zero or be uniform
    # (depends on implementation choice for cold start)
    assert normalized[:, 1].sum() >= 0.0


def test_should_preserve_zero_values():
    """Test that zero values remain zero after normalization."""
    matrix = torch.tensor([
        [0.0, 2.0, 0.0],
        [4.0, 0.0, 6.0],
        [0.0, 8.0, 0.0]
    ], dtype=torch.float32)

    normalized = normalize_columns(matrix)

    # Zeros should remain zeros
    assert normalized[0, 0] == 0.0
    assert normalized[0, 2] == 0.0
    assert normalized[2, 0] == 0.0
    assert normalized[2, 2] == 0.0


def test_should_handle_already_normalized_matrix():
    """Test that normalizing an already normalized matrix doesn't change it."""
    matrix = torch.tensor([
        [0.2, 0.5, 0.1],
        [0.3, 0.3, 0.4],
        [0.5, 0.2, 0.5]
    ], dtype=torch.float32)

    normalized = normalize_columns(matrix)

    assert torch.allclose(normalized, matrix, atol=1e-6)


def test_should_raise_error_for_negative_values():
    """Test that normalization rejects matrices with negative values."""
    matrix = torch.tensor([
        [1.0, -2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0]
    ], dtype=torch.float32)

    with pytest.raises(ValueError, match="non-negative"):
        normalize_columns(matrix)
