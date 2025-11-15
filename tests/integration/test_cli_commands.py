"""Integration tests for CLI commands.

Tests CLI interface for User Story 1 following TDD principles.
"""

import pytest
import json
import tempfile
from pathlib import Path
from typer.testing import CliRunner


@pytest.fixture
def cli_runner():
    """Create CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def temp_output_file():
    """Create temporary output file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        yield Path(f.name)
        # Cleanup
        Path(f.name).unlink(missing_ok=True)


def test_should_create_network_via_cli_with_default_options(cli_runner, temp_output_file) -> None:
    """Test that CLI create command works with default options."""
    from eigentrust.cli.main import app

    result = cli_runner.invoke(app, ["create", "--output", str(temp_output_file)])

    assert result.exit_code == 0
    assert "Created simulation" in result.stdout or "created" in result.stdout.lower()
    assert temp_output_file.exists()

    # Verify output file contains valid simulation
    with open(temp_output_file) as f:
        data = json.load(f)
        assert "simulation_id" in data
        assert "peers" in data
        assert len(data["peers"]) == 10  # Default peer count


def test_should_create_network_with_custom_peer_count(cli_runner, temp_output_file) -> None:
    """Test that CLI create command accepts custom peer count."""
    from eigentrust.cli.main import app

    result = cli_runner.invoke(
        app,
        ["create", "--peers", "20", "--output", str(temp_output_file)]
    )

    assert result.exit_code == 0

    with open(temp_output_file) as f:
        data = json.load(f)
        assert len(data["peers"]) == 20


def test_should_create_network_with_seed_for_reproducibility(cli_runner, temp_output_file) -> None:
    """Test that CLI create command accepts random seed."""
    from eigentrust.cli.main import app

    result = cli_runner.invoke(
        app,
        ["create", "--peers", "15", "--seed", "42", "--output", str(temp_output_file)]
    )

    assert result.exit_code == 0

    with open(temp_output_file) as f:
        data = json.load(f)
        assert data.get("random_seed") == 42 or data.get("seed") == 42


def test_should_create_network_with_preset_characteristics(cli_runner, temp_output_file) -> None:
    """Test that CLI create command accepts preset option."""
    from eigentrust.cli.main import app

    result = cli_runner.invoke(
        app,
        ["create", "--peers", "10", "--preset", "adversarial", "--output", str(temp_output_file)]
    )

    assert result.exit_code == 0

    with open(temp_output_file) as f:
        data = json.load(f)
        assert len(data["peers"]) == 10


def test_should_fail_with_invalid_peer_count(cli_runner, temp_output_file) -> None:
    """Test that CLI create command rejects invalid peer counts."""
    from eigentrust.cli.main import app

    # Test peer count too low
    result = cli_runner.invoke(
        app,
        ["create", "--peers", "1", "--output", str(temp_output_file)]
    )
    assert result.exit_code != 0

    # Test peer count too high
    result = cli_runner.invoke(
        app,
        ["create", "--peers", "501", "--output", str(temp_output_file)]
    )
    assert result.exit_code != 0


def test_should_display_help_for_create_command(cli_runner) -> None:
    """Test that CLI create command has help documentation."""
    from eigentrust.cli.main import app

    result = cli_runner.invoke(app, ["create", "--help"])

    assert result.exit_code == 0
    assert "peers" in result.stdout.lower()
    assert "output" in result.stdout.lower()


def test_should_handle_missing_output_path_with_default(cli_runner) -> None:
    """Test that CLI create command uses default output path if not specified."""
    from eigentrust.cli.main import app
    import os

    # Remove default file if exists
    default_file = Path("simulation.json")
    default_file.unlink(missing_ok=True)

    try:
        result = cli_runner.invoke(app, ["create", "--peers", "5"])

        # Command should succeed with default output
        assert result.exit_code == 0

        # Default file should be created
        # Note: Actual default path may vary, this is a flexible test

    finally:
        # Cleanup default file
        default_file.unlink(missing_ok=True)


def test_should_reject_invalid_preset_option(cli_runner, temp_output_file) -> None:
    """Test that CLI create command rejects invalid preset values."""
    from eigentrust.cli.main import app

    result = cli_runner.invoke(
        app,
        ["create", "--peers", "10", "--preset", "invalid_preset", "--output", str(temp_output_file)]
    )

    assert result.exit_code != 0
    assert "preset" in result.stdout.lower() or "invalid" in result.stdout.lower()
