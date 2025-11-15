"""Unit tests for Peer entity.

Tests peer validation and characteristic assignment following TDD principles.
"""

import uuid

import pytest

from eigentrust.domain import InvalidPeerCharacteristics


def test_should_validate_competence_range_when_creating_peer() -> None:
    """Test that Peer validates competence is in [0.0, 1.0] range."""
    from eigentrust.domain.peer import Peer

    # Valid competence values should work
    peer1 = Peer(competence=0.0, maliciousness=0.5)
    assert peer1.competence == 0.0

    peer2 = Peer(competence=1.0, maliciousness=0.5)
    assert peer2.competence == 1.0

    peer3 = Peer(competence=0.5, maliciousness=0.5)
    assert peer3.competence == 0.5

    # Invalid competence values should raise error
    with pytest.raises(InvalidPeerCharacteristics) as exc_info:
        Peer(competence=-0.1, maliciousness=0.5)
    assert exc_info.value.competence == -0.1

    with pytest.raises(InvalidPeerCharacteristics) as exc_info:
        Peer(competence=1.1, maliciousness=0.5)
    assert exc_info.value.competence == 1.1


def test_should_validate_maliciousness_range_when_creating_peer() -> None:
    """Test that Peer validates maliciousness is in [0.0, 1.0] range."""
    from eigentrust.domain.peer import Peer

    # Valid maliciousness values should work
    peer1 = Peer(competence=0.5, maliciousness=0.0)
    assert peer1.maliciousness == 0.0

    peer2 = Peer(competence=0.5, maliciousness=1.0)
    assert peer2.maliciousness == 1.0

    # Invalid maliciousness values should raise error
    with pytest.raises(InvalidPeerCharacteristics) as exc_info:
        Peer(competence=0.5, maliciousness=-0.1)
    assert exc_info.value.maliciousness == -0.1

    with pytest.raises(InvalidPeerCharacteristics) as exc_info:
        Peer(competence=0.5, maliciousness=1.5)
    assert exc_info.value.maliciousness == 1.5


def test_should_assign_unique_id_when_creating_peer() -> None:
    """Test that each peer gets a unique UUID identifier."""
    from eigentrust.domain.peer import Peer

    peer1 = Peer(competence=0.0, maliciousness=0.0)
    peer2 = Peer(competence=0.0, maliciousness=0.0)

    assert peer1.peer_id is not None
    assert peer2.peer_id is not None
    assert peer1.peer_id != peer2.peer_id

    # Should be valid UUIDs
    assert isinstance(uuid.UUID(str(peer1.peer_id)), uuid.UUID)


def test_should_store_characteristics_when_creating_peer() -> None:
    """Test that peer correctly stores competence and maliciousness characteristics."""
    from eigentrust.domain.peer import Peer

    # Hypercompetent and altruistic [0.0, 0.0]
    peer1 = Peer(competence=0.0, maliciousness=0.0)
    assert peer1.competence == 0.0
    assert peer1.maliciousness == 0.0

    # Incompetent and malicious [1.0, 1.0]
    peer2 = Peer(competence=1.0, maliciousness=1.0)
    assert peer2.competence == 1.0
    assert peer2.maliciousness == 1.0

    # Hypercompetent and malicious [0.0, 1.0]
    peer3 = Peer(competence=0.0, maliciousness=1.0)
    assert peer3.competence == 0.0
    assert peer3.maliciousness == 1.0

    # Incompetent and altruistic [1.0, 0.0]
    peer4 = Peer(competence=1.0, maliciousness=0.0)
    assert peer4.competence == 1.0
    assert peer4.maliciousness == 0.0

    # Neutral [0.5, 0.5]
    peer5 = Peer(competence=0.5, maliciousness=0.5)
    assert peer5.competence == 0.5
    assert peer5.maliciousness == 0.5


def test_should_initialize_empty_local_trust_when_creating_peer() -> None:
    """Test that peer starts with empty local trust dictionary."""
    from eigentrust.domain.peer import Peer

    peer = Peer(competence=0.5, maliciousness=0.5)
    assert peer.local_trust == {}


def test_should_have_no_global_trust_initially_when_creating_peer() -> None:
    """Test that peer starts with no global trust score (None)."""
    from eigentrust.domain.peer import Peer

    peer = Peer(competence=0.5, maliciousness=0.5)
    assert peer.global_trust is None


def test_should_generate_display_name_when_creating_peer() -> None:
    """Test that peer has a human-readable display name."""
    from eigentrust.domain.peer import Peer

    peer = Peer(competence=0.5, maliciousness=0.5)
    assert peer.display_name is not None
    assert len(peer.display_name) > 0
    assert "Peer" in peer.display_name
