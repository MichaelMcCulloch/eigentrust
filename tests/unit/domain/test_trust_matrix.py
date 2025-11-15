"""Unit tests for TrustMatrix entity (T031)."""

from uuid import uuid4

import pytest
import torch

from eigentrust.domain.trust_matrix import TrustMatrix


def test_should_create_trust_matrix_from_tensor():
    """Test that TrustMatrix can be created with valid tensor."""
    peer_ids = [uuid4() for _ in range(3)]
    matrix = torch.tensor([[0.0, 0.5, 0.5], [0.3, 0.0, 0.7], [0.4, 0.6, 0.0]])

    trust_matrix = TrustMatrix(
        matrix=matrix, peer_mapping={peer_ids[0]: 0, peer_ids[1]: 1, peer_ids[2]: 2}
    )

    assert trust_matrix.matrix.shape == (3, 3)
    assert len(trust_matrix.peer_mapping) == 3


def test_should_reject_non_square_matrix():
    """Test that TrustMatrix rejects non-square matrices."""
    peer_ids = [uuid4() for _ in range(2)]
    matrix = torch.tensor([[0.0, 0.5], [0.3, 0.7], [0.4, 0.6]])

    with pytest.raises(ValueError, match="must be square"):
        TrustMatrix(matrix=matrix, peer_mapping={peer_ids[0]: 0, peer_ids[1]: 1})


def test_should_reject_negative_values():
    """Test that TrustMatrix rejects negative trust values."""
    peer_ids = [uuid4() for _ in range(2)]
    matrix = torch.tensor([[0.0, -0.5], [0.3, 0.0]])

    with pytest.raises(ValueError, match="non-negative"):
        TrustMatrix(matrix=matrix, peer_mapping={peer_ids[0]: 0, peer_ids[1]: 1})


def test_should_get_trust_value_between_peers():
    """Test getting trust value between two peers."""
    peer1 = uuid4()
    peer2 = uuid4()
    peer3 = uuid4()

    matrix = torch.tensor([[0.0, 0.6, 0.4], [0.3, 0.0, 0.7], [0.5, 0.5, 0.0]])

    trust_matrix = TrustMatrix(matrix=matrix, peer_mapping={peer1: 0, peer2: 1, peer3: 2})

    # Peer 1 trusts Peer 2 with 0.6
    assert trust_matrix.get_trust(peer1, peer2) == pytest.approx(0.6)
    # Peer 2 trusts Peer 3 with 0.7
    assert trust_matrix.get_trust(peer2, peer3) == pytest.approx(0.7)


def test_should_set_trust_value_between_peers():
    """Test setting trust value between two peers."""
    peer1 = uuid4()
    peer2 = uuid4()

    matrix = torch.zeros(2, 2)
    trust_matrix = TrustMatrix(matrix=matrix, peer_mapping={peer1: 0, peer2: 1})

    trust_matrix.set_trust(peer1, peer2, 0.8)

    assert trust_matrix.get_trust(peer1, peer2) == pytest.approx(0.8)


def test_should_reject_trust_value_out_of_range():
    """Test that setting trust value outside [0,1] raises error."""
    peer1 = uuid4()
    peer2 = uuid4()

    matrix = torch.zeros(2, 2)
    trust_matrix = TrustMatrix(matrix=matrix, peer_mapping={peer1: 0, peer2: 1})

    with pytest.raises(ValueError, match="must be in range"):
        trust_matrix.set_trust(peer1, peer2, 1.5)

    with pytest.raises(ValueError, match="must be in range"):
        trust_matrix.set_trust(peer1, peer2, -0.1)


def test_should_export_to_numpy():
    """Test exporting matrix to NumPy array."""
    peer_ids = [uuid4() for _ in range(2)]
    matrix = torch.tensor([[0.0, 0.5], [0.5, 0.0]])

    trust_matrix = TrustMatrix(matrix=matrix, peer_mapping={peer_ids[0]: 0, peer_ids[1]: 1})

    numpy_matrix = trust_matrix.to_numpy()

    assert numpy_matrix.shape == (2, 2)
    assert numpy_matrix[0, 1] == pytest.approx(0.5)
