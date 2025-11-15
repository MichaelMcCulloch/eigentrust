"""File I/O utilities for saving and loading simulations.

Provides JSON and Pickle serialization for simulation state.
"""

import json
import pickle
from pathlib import Path
from typing import Any, Dict


def save_json(data: Dict[str, Any], file_path: str | Path) -> None:
    """Save data to JSON file.

    Args:
        data: Dictionary to serialize
        file_path: Path to output file

    Raises:
        IOError: If file cannot be written
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_json(file_path: str | Path) -> Dict[str, Any]:
    """Load data from JSON file.

    Args:
        file_path: Path to input file

    Returns:
        Deserialized dictionary

    Raises:
        FileNotFoundError: If file does not exist
        json.JSONDecodeError: If file is not valid JSON
    """
    path = Path(file_path)

    with open(path, "r") as f:
        return json.load(f)


def save_pickle(data: Any, file_path: str | Path) -> None:
    """Save data to pickle file.

    Args:
        data: Object to serialize (typically PyTorch tensors)
        file_path: Path to output file

    Raises:
        IOError: If file cannot be written
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "wb") as f:
        pickle.dump(data, f)


def load_pickle(file_path: str | Path) -> Any:
    """Load data from pickle file.

    Args:
        file_path: Path to input file

    Returns:
        Deserialized object

    Raises:
        FileNotFoundError: If file does not exist
        pickle.UnpicklingError: If file is not valid pickle
    """
    path = Path(file_path)

    with open(path, "rb") as f:
        return pickle.load(f)


def file_exists(file_path: str | Path) -> bool:
    """Check if file exists.

    Args:
        file_path: Path to check

    Returns:
        True if file exists, False otherwise
    """
    return Path(file_path).exists()


def save_simulation(simulation: "Simulation", file_path: str | Path) -> None:
    """Save simulation to JSON file.

    Args:
        simulation: Simulation object to save
        file_path: Path to output file

    Raises:
        IOError: If file cannot be written
    """
    from eigentrust.domain.simulation import Simulation

    data = simulation.to_dict()
    save_json(data, file_path)


def load_simulation(file_path: str | Path) -> "Simulation":
    """Load simulation from JSON file.

    Args:
        file_path: Path to input file

    Returns:
        Loaded Simulation object

    Raises:
        FileNotFoundError: If file does not exist
        json.JSONDecodeError: If file is not valid JSON
    """
    from eigentrust.domain.simulation import Simulation

    data = load_json(file_path)
    return Simulation.from_dict(data)
