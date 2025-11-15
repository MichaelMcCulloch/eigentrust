"""Unit tests for interaction outcome computation (T035)."""

import pytest
from unittest.mock import patch
from uuid import uuid4

from eigentrust.domain.peer import Peer
from eigentrust.domain.interaction import InteractionOutcome
from eigentrust.simulation.interactions import compute_interaction_outcome, simulate_interactions


def test_should_compute_success_for_competent_altruistic_peer():
    """Test that competent and altruistic peers have high success rate."""
    # Hypercompetent (0.0) and Altruistic (0.0) peer
    peer = Peer(competence=0.0, maliciousness=0.0)
    partner = Peer(competence=0.5, maliciousness=0.5)

    # Mock random to ensure deterministic test
    with patch('eigentrust.simulation.interactions.random') as mock_random:
        mock_random.random.return_value = 0.5  # Below high success threshold
        mock_random.gauss.return_value = 0.0  # No noise

        outcome = compute_interaction_outcome(peer, partner)

        # (1 - 0.0) * (1 - 0.0) + 0.0 = 1.0
        # Since random.random() = 0.5 < 1.0, should succeed
        assert outcome == InteractionOutcome.SUCCESS


def test_should_compute_failure_for_incompetent_malicious_peer():
    """Test that incompetent and malicious peers have high failure rate."""
    # Incompetent (1.0) and Malicious (1.0) peer
    peer = Peer(competence=1.0, maliciousness=1.0)
    partner = Peer(competence=0.5, maliciousness=0.5)

    with patch('eigentrust.simulation.interactions.random') as mock_random:
        mock_random.random.return_value = 0.1  # Any value > 0
        mock_random.gauss.return_value = 0.0

        outcome = compute_interaction_outcome(peer, partner)

        # (1 - 1.0) * (1 - 1.0) + 0.0 = 0.0
        # Since random.random() = 0.1 > 0.0, should fail
        assert outcome == InteractionOutcome.FAILURE


def test_should_incorporate_randomness_with_noise():
    """Test that noise affects outcome probability."""
    peer = Peer(competence=0.5, maliciousness=0.5)
    partner = Peer(competence=0.5, maliciousness=0.5)

    with patch('eigentrust.simulation.interactions.random') as mock_random:
        # Base probability: (1-0.5)*(1-0.5) = 0.25
        # Add noise: 0.25 + 0.05 = 0.30
        mock_random.gauss.return_value = 0.05
        mock_random.random.return_value = 0.28  # Below 0.30

        outcome = compute_interaction_outcome(peer, partner)

        assert outcome == InteractionOutcome.SUCCESS


def test_should_clamp_probability_to_zero_one_range():
    """Test that probability is clamped to [0, 1] with extreme noise."""
    peer = Peer(competence=0.0, maliciousness=0.0)
    partner = Peer(competence=0.5, maliciousness=0.5)

    with patch('eigentrust.simulation.interactions.random') as mock_random:
        # Base: 1.0, noise: +0.5, clamped to 1.0
        mock_random.gauss.return_value = 0.5
        mock_random.random.return_value = 0.99

        outcome = compute_interaction_outcome(peer, partner)

        # Should succeed since clamped prob = 1.0
        assert outcome == InteractionOutcome.SUCCESS


def test_should_simulate_multiple_interactions():
    """Test simulating multiple interactions between peers."""
    peers = [
        Peer(competence=0.0, maliciousness=0.0),  # Good peer
        Peer(competence=1.0, maliciousness=1.0),  # Bad peer
        Peer(competence=0.5, maliciousness=0.5),  # Neutral peer
    ]

    interactions = simulate_interactions(peers, num_interactions=10, seed=42)

    assert len(interactions) == 10
    assert all(interaction.source_peer_id in [p.peer_id for p in peers] for interaction in interactions)
    assert all(interaction.target_peer_id in [p.peer_id for p in peers] for interaction in interactions)
    # Source and target should be different
    assert all(interaction.source_peer_id != interaction.target_peer_id for interaction in interactions)


def test_should_respect_random_seed_for_reproducibility():
    """Test that same seed produces same interaction sequence."""
    peers = [
        Peer(competence=0.2, maliciousness=0.3),
        Peer(competence=0.7, maliciousness=0.4),
    ]

    interactions1 = simulate_interactions(peers, num_interactions=5, seed=123)
    interactions2 = simulate_interactions(peers, num_interactions=5, seed=123)

    # Same seed should produce identical outcomes
    assert len(interactions1) == len(interactions2)
    for int1, int2 in zip(interactions1, interactions2):
        assert int1.source_peer_id == int2.source_peer_id
        assert int1.target_peer_id == int2.target_peer_id
        assert int1.outcome == int2.outcome
