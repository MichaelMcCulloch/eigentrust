"""Unit tests for Interaction value object (T030)."""

from datetime import datetime
from uuid import uuid4

import pytest

from eigentrust.domain.interaction import Interaction, InteractionOutcome


def test_should_create_interaction_with_valid_data():
    """Test that Interaction can be created with valid data."""
    source_id = uuid4()
    target_id = uuid4()

    interaction = Interaction(
        source_peer_id=source_id, target_peer_id=target_id, outcome=InteractionOutcome.SUCCESS
    )

    assert interaction.source_peer_id == source_id
    assert interaction.target_peer_id == target_id
    assert interaction.outcome == InteractionOutcome.SUCCESS
    assert isinstance(interaction.timestamp, datetime)
    assert isinstance(interaction.interaction_id, type(uuid4()))


def test_should_reject_interaction_with_same_source_and_target():
    """Test that Interaction rejects same peer as source and target."""
    peer_id = uuid4()

    with pytest.raises(ValueError, match="Source and target must be different"):
        Interaction(
            source_peer_id=peer_id, target_peer_id=peer_id, outcome=InteractionOutcome.SUCCESS
        )


def test_should_create_interaction_with_failure_outcome():
    """Test that Interaction can be created with FAILURE outcome."""
    source_id = uuid4()
    target_id = uuid4()

    interaction = Interaction(
        source_peer_id=source_id, target_peer_id=target_id, outcome=InteractionOutcome.FAILURE
    )

    assert interaction.outcome == InteractionOutcome.FAILURE


def test_should_be_immutable():
    """Test that Interaction is immutable (value object)."""
    source_id = uuid4()
    target_id = uuid4()

    interaction = Interaction(
        source_peer_id=source_id, target_peer_id=target_id, outcome=InteractionOutcome.SUCCESS
    )

    # Attempting to modify should raise error
    with pytest.raises(AttributeError):
        interaction.outcome = InteractionOutcome.FAILURE


def test_should_have_unique_interaction_ids():
    """Test that each Interaction gets a unique ID."""
    source_id = uuid4()
    target_id = uuid4()

    interaction1 = Interaction(
        source_peer_id=source_id, target_peer_id=target_id, outcome=InteractionOutcome.SUCCESS
    )

    interaction2 = Interaction(
        source_peer_id=source_id, target_peer_id=target_id, outcome=InteractionOutcome.SUCCESS
    )

    assert interaction1.interaction_id != interaction2.interaction_id
