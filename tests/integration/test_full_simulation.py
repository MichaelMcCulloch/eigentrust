"""Integration test for full algorithm execution (T036)."""

import pytest
import torch
from uuid import uuid4

from eigentrust.domain.simulation import Simulation
from eigentrust.domain.peer import Peer
from eigentrust.simulation.interactions import simulate_interactions
from eigentrust.algorithms.eigentrust import compute_eigentrust
from eigentrust.algorithms.normalization import normalize_columns


def test_should_execute_full_eigentrust_pipeline():
    """Test complete pipeline: create peers -> simulate -> build matrix -> run algorithm."""
    # Create simulation with peers
    simulation = Simulation()

    # Add peers with different characteristics
    peer1 = Peer(competence=0.1, maliciousness=0.1)  # Good peer
    peer2 = Peer(competence=0.9, maliciousness=0.9)  # Bad peer
    peer3 = Peer(competence=0.5, maliciousness=0.5)  # Neutral peer

    simulation.add_peer(peer1)
    simulation.add_peer(peer2)
    simulation.add_peer(peer3)

    # Simulate interactions
    interactions = simulate_interactions(simulation.peers, num_interactions=30, seed=42)
    for interaction in interactions:
        simulation.add_interaction(interaction)

    # Run EigenTrust algorithm
    result = simulation.run_algorithm(max_iterations=100, epsilon=0.001)

    # Verify results
    assert result.converged is True
    assert result.iteration_count < 100
    assert len(result.scores) == 3

    # Verify trust scores sum to 1.0
    total_trust = sum(result.scores.values())
    assert abs(total_trust - 1.0) < 1e-6

    # Good peer should have higher trust than bad peer
    assert result.scores[peer1.peer_id] > result.scores[peer2.peer_id]


def test_should_handle_simulation_with_many_peers():
    """Test algorithm with larger network (10 peers)."""
    simulation = Simulation()

    # Create 10 peers with random characteristics
    import random
    random.seed(123)

    peers = []
    for _ in range(10):
        competence = random.uniform(0.0, 1.0)
        maliciousness = random.uniform(0.0, 1.0)
        peer = Peer(competence=competence, maliciousness=maliciousness)
        simulation.add_peer(peer)
        peers.append(peer)

    # Simulate many interactions
    interactions = simulate_interactions(simulation.peers, num_interactions=100, seed=123)
    for interaction in interactions:
        simulation.add_interaction(interaction)

    # Run algorithm
    result = simulation.run_algorithm(max_iterations=100, epsilon=0.001)

    # Verify convergence
    assert result.converged is True
    assert len(result.scores) == 10

    # All scores should be positive and sum to 1
    assert all(score > 0 for score in result.scores.values())
    assert abs(sum(result.scores.values()) - 1.0) < 1e-6


def test_should_track_convergence_history():
    """Test that algorithm tracks trust score evolution."""
    simulation = Simulation()

    # Add 3 peers
    for _ in range(3):
        peer = Peer(competence=0.3, maliciousness=0.3)
        simulation.add_peer(peer)

    # Simulate interactions
    interactions = simulate_interactions(simulation.peers, num_interactions=20, seed=99)
    for interaction in interactions:
        simulation.add_interaction(interaction)

    # Run with history tracking
    result = simulation.run_algorithm(max_iterations=100, epsilon=0.001, track_history=True)

    # Verify history is tracked
    assert len(result.history) > 0
    assert len(result.history) == result.iteration_count

    # Each snapshot should have trust scores for all peers
    for snapshot in result.history:
        assert len(snapshot.trust_scores) == 3
        assert abs(sum(snapshot.trust_scores.values()) - 1.0) < 1e-6


def test_should_handle_cold_start():
    """Test algorithm with no interactions (cold start)."""
    simulation = Simulation()

    # Add peers but NO interactions
    for _ in range(5):
        peer = Peer(competence=0.5, maliciousness=0.5)
        simulation.add_peer(peer)

    # Run algorithm with uniform pre-trust
    result = simulation.run_algorithm(max_iterations=100, epsilon=0.001)

    # Should converge to uniform distribution
    expected_trust = 1.0 / 5
    for score in result.scores.values():
        assert abs(score - expected_trust) < 0.01

    assert result.converged is True


def test_should_fail_with_insufficient_peers():
    """Test that simulation requires at least 2 peers."""
    simulation = Simulation()

    # Add only 1 peer
    peer = Peer(competence=0.5, maliciousness=0.5)
    simulation.add_peer(peer)

    # Should raise error when running algorithm
    with pytest.raises(ValueError, match="at least 2 peers"):
        simulation.run_algorithm(max_iterations=100, epsilon=0.001)
