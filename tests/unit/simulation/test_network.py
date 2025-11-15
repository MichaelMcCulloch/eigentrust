"""Unit tests for network creation functionality.

Tests peer network initialization and configuration following TDD principles.
"""

import pytest


def test_should_create_network_with_specified_peer_count() -> None:
    """Test that network creation generates correct number of peers."""
    from eigentrust.simulation.network import create_network

    sim = create_network(peer_count=10)

    assert len(sim.peers) == 10


def test_should_create_network_with_random_characteristics() -> None:
    """Test that random preset assigns random characteristics to peers."""
    from eigentrust.simulation.network import create_network

    sim = create_network(peer_count=20, preset="random", seed=42)

    assert len(sim.peers) == 20

    # All peers should have characteristics in [0.0, 1.0]
    for peer in sim.peers:
        assert 0.0 <= peer.competence <= 1.0
        assert 0.0 <= peer.maliciousness <= 1.0

    # At least some variation (not all identical)
    competences = [p.competence for p in sim.peers]
    assert len(set(competences)) > 1  # At least 2 different values


def test_should_create_network_with_uniform_characteristics() -> None:
    """Test that uniform preset assigns [0.5, 0.5] to all peers."""
    from eigentrust.simulation.network import create_network

    sim = create_network(peer_count=10, preset="uniform")

    assert len(sim.peers) == 10

    # All peers should have [0.5, 0.5]
    for peer in sim.peers:
        assert peer.competence == 0.5
        assert peer.maliciousness == 0.5


def test_should_create_network_with_adversarial_mix() -> None:
    """Test that adversarial preset creates mix of good and bad peers."""
    from eigentrust.simulation.network import create_network

    sim = create_network(peer_count=30, preset="adversarial", seed=123)

    assert len(sim.peers) == 30

    # Should have mix of good (low comp, low mal), bad (high comp, high mal)
    good_peers = [p for p in sim.peers if p.competence <= 0.2 and p.maliciousness <= 0.2]
    bad_peers = [p for p in sim.peers if p.competence >= 0.8 and p.maliciousness >= 0.8]

    # Should have at least some good and some bad peers
    assert len(good_peers) > 0
    assert len(bad_peers) > 0


def test_should_use_random_seed_for_reproducibility() -> None:
    """Test that same seed produces identical networks."""
    from eigentrust.simulation.network import create_network

    sim1 = create_network(peer_count=15, preset="random", seed=42)
    sim2 = create_network(peer_count=15, preset="random", seed=42)

    assert len(sim1.peers) == len(sim2.peers)

    # Characteristics should be identical with same seed
    for p1, p2 in zip(sim1.peers, sim2.peers):
        assert p1.competence == p2.competence
        assert p1.maliciousness == p2.maliciousness


def test_should_validate_minimum_peer_count() -> None:
    """Test that network creation requires at least 2 peers."""
    from eigentrust.domain import InsufficientPeersError
    from eigentrust.simulation.network import create_network

    # Should raise error for 0 peers
    with pytest.raises(InsufficientPeersError):
        create_network(peer_count=0)

    # Should raise error for 1 peer
    with pytest.raises(InsufficientPeersError):
        create_network(peer_count=1)

    # Should work for 2 peers
    sim = create_network(peer_count=2)
    assert len(sim.peers) == 2


def test_should_validate_maximum_peer_count() -> None:
    """Test that network creation enforces maximum peer count (500)."""
    from eigentrust.domain import InvalidPeerCharacteristics
    from eigentrust.simulation.network import create_network

    # Should raise error for >500 peers
    with pytest.raises((InvalidPeerCharacteristics, ValueError)) as exc_info:
        create_network(peer_count=501)

    assert "500" in str(exc_info.value) or "maximum" in str(exc_info.value).lower()


def test_should_assign_unique_display_names_to_peers() -> None:
    """Test that peers get unique, readable display names."""
    from eigentrust.simulation.network import create_network

    sim = create_network(peer_count=10)

    display_names = [p.display_name for p in sim.peers]

    # All should be non-empty
    assert all(len(name) > 0 for name in display_names)

    # All should be unique
    assert len(set(display_names)) == len(display_names)

    # Should contain "Peer" prefix
    assert all("Peer" in name for name in display_names)


def test_should_handle_invalid_preset_gracefully() -> None:
    """Test that invalid preset raises appropriate error."""
    from eigentrust.simulation.network import create_network

    with pytest.raises(ValueError) as exc_info:
        create_network(peer_count=10, preset="invalid_preset")

    assert "preset" in str(exc_info.value).lower()
