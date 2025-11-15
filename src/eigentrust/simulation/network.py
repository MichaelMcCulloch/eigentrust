"""Network creation functionality.

Provides functions to create peer networks with different characteristic distributions.
"""

import random
from typing import Optional
from eigentrust.domain import InsufficientPeersError, InvalidPeerCharacteristics
from eigentrust.domain.simulation import Simulation
from eigentrust.simulation.behaviors import (
    generate_random_characteristics,
    generate_adversarial_characteristics,
)


def create_network(
    peer_count: int,
    preset: str = "random",
    seed: Optional[int] = None,
) -> Simulation:
    """Create a new peer network simulation with configured characteristics.

    Args:
        peer_count: Number of peers to create (must be 2-500)
        preset: Characteristic distribution preset (random, uniform, adversarial)
        seed: Optional random seed for reproducibility

    Returns:
        New Simulation with configured peers

    Raises:
        InsufficientPeersError: If peer_count < 2
        InvalidPeerCharacteristics: If peer_count > 500
        ValueError: If preset is invalid
    """
    # Validate peer count
    if peer_count < 2:
        raise InsufficientPeersError(
            "At least 2 peers required to create network",
            peer_count=peer_count,
        )

    if peer_count > 500:
        raise InvalidPeerCharacteristics(
            f"Maximum 500 peers allowed, got {peer_count}",
            competence=0.0,
            maliciousness=0.0,
        )

    # Validate preset
    valid_presets = ["random", "uniform", "adversarial"]
    if preset not in valid_presets:
        raise ValueError(
            f"Invalid preset '{preset}'. "
            f"Must be one of: {', '.join(valid_presets)}"
        )

    # Create simulation
    sim = Simulation(random_seed=seed)

    # Set random seed if provided
    if seed is not None:
        random.seed(seed)

    # Generate peers based on preset
    for i in range(peer_count):
        if preset == "random":
            competence, maliciousness = generate_random_characteristics()
        elif preset == "uniform":
            competence, maliciousness = 0.5, 0.5
        elif preset == "adversarial":
            competence, maliciousness = generate_adversarial_characteristics(
                peer_index=i,
                total_peers=peer_count,
            )

        # Add peer to simulation
        sim.add_peer(competence=competence, maliciousness=maliciousness)

    return sim


def create_network_with_characteristics(
    characteristics: list[tuple[float, float]],
    seed: Optional[int] = None,
) -> Simulation:
    """Create network with explicitly specified peer characteristics.

    Useful for testing and reproducible scenarios.

    Args:
        characteristics: List of (competence, maliciousness) tuples
        seed: Optional random seed

    Returns:
        New Simulation with specified peers

    Raises:
        InsufficientPeersError: If fewer than 2 characteristics provided
    """
    if len(characteristics) < 2:
        raise InsufficientPeersError(
            "At least 2 peers required to create network",
            peer_count=len(characteristics),
        )

    sim = Simulation(random_seed=seed)

    for competence, maliciousness in characteristics:
        sim.add_peer(competence=competence, maliciousness=maliciousness)

    return sim
