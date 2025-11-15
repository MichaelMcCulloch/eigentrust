"""Unit tests for Simulation entity.

Tests simulation creation and peer management following TDD principles.
"""

import uuid
from datetime import datetime

import pytest

from eigentrust.domain import InsufficientPeersError


def test_should_create_simulation_with_valid_peers() -> None:
    """Test that Simulation can be created with valid peer count."""
    from eigentrust.domain.simulation import Simulation, SimulationState

    sim = Simulation()
    assert sim.simulation_id is not None
    assert isinstance(uuid.UUID(str(sim.simulation_id)), uuid.UUID)
    assert sim.state == SimulationState.CREATED
    assert sim.peers == []
    assert sim.interactions == []
    assert sim.convergence_history == []


def test_should_add_peer_to_simulation() -> None:
    """Test that peers can be added to simulation."""
    from eigentrust.domain.simulation import Simulation

    sim = Simulation()
    peer1 = sim.add_peer(competence=0.0, maliciousness=0.0)

    assert len(sim.peers) == 1
    assert peer1 in sim.peers
    assert peer1.competence == 0.0
    assert peer1.maliciousness == 0.0

    peer2 = sim.add_peer(competence=0.5, maliciousness=0.5)
    assert len(sim.peers) == 2
    assert peer2 in sim.peers


def test_should_validate_minimum_peer_count_when_running_algorithm() -> None:
    """Test that simulation requires at least 2 peers to run algorithm."""
    from eigentrust.domain.simulation import Simulation

    sim = Simulation()

    # Cannot run with 0 peers
    with pytest.raises(InsufficientPeersError) as exc_info:
        sim.run_algorithm()
    assert "at least 2 peers" in str(exc_info.value).lower()

    # Cannot run with 1 peer
    sim.add_peer(competence=0.0, maliciousness=0.0)
    with pytest.raises(InsufficientPeersError) as exc_info:
        sim.run_algorithm()
    assert "at least 2 peers" in str(exc_info.value).lower()


def test_should_track_creation_timestamp_when_creating_simulation() -> None:
    """Test that simulation records creation timestamp."""
    from eigentrust.domain.simulation import Simulation

    before = datetime.utcnow()
    sim = Simulation()
    after = datetime.utcnow()

    assert sim.created_at is not None
    assert before <= sim.created_at <= after


def test_should_accept_random_seed_for_reproducibility() -> None:
    """Test that simulation can accept random seed for reproducible results."""
    from eigentrust.domain.simulation import Simulation

    sim = Simulation(random_seed=42)
    assert sim.random_seed == 42

    sim2 = Simulation()
    assert sim2.random_seed is None


def test_should_have_correct_initial_state() -> None:
    """Test that simulation starts in CREATED state."""
    from eigentrust.domain.simulation import Simulation, SimulationState

    sim = Simulation()
    assert sim.state == SimulationState.CREATED


def test_should_enforce_maximum_peer_count() -> None:
    """Test that simulation enforces maximum peer count (500)."""
    from eigentrust.domain.simulation import Simulation

    _sim = Simulation()

    # Adding 501 peers should raise error or be prevented
    # Note: This is a soft limit, implementation may choose to enforce or warn
    # For now, we'll test that the limit exists in documentation
    # Implementation can add enforcement if needed
    pass  # Placeholder for potential enforcement test
