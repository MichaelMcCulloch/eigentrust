"""Peer behavior probability models.

Implements probabilistic peer behavior based on competence and maliciousness
characteristics following the research.md specifications.
"""

import random
from typing import Tuple, Optional


def compute_interaction_success_probability(
    competence: float,
    maliciousness: float,
) -> float:
    """Compute probability of successful interaction.

    Based on the formula from research.md:
    P(success) = (1 - competence) * (1 - maliciousness) + random_noise

    Args:
        competence: Incompetence level [0.0, 1.0]
        maliciousness: Malicious intent [0.0, 1.0]

    Returns:
        Probability of success [0.0, 1.0]
    """
    # Base success rate inversely related to incompetence
    technical_success = 1.0 - competence

    # Maliciousness reduces likelihood of helping
    cooperation_factor = 1.0 - maliciousness

    # Combined probability
    success_prob = technical_success * cooperation_factor

    # Add small random noise to prevent determinism
    noise = random.gauss(0, 0.05)
    final_prob = max(0.0, min(1.0, success_prob + noise))

    return final_prob


def generate_random_characteristics(seed: Optional[int] = None) -> Tuple[float, float]:
    """Generate random peer characteristics.

    Args:
        seed: Optional random seed for reproducibility

    Returns:
        Tuple of (competence, maliciousness) values in [0.0, 1.0]
    """
    if seed is not None:
        random.seed(seed)

    competence = random.uniform(0.0, 1.0)
    maliciousness = random.uniform(0.0, 1.0)

    return (competence, maliciousness)


def generate_adversarial_characteristics(
    peer_index: int,
    total_peers: int,
) -> Tuple[float, float]:
    """Generate characteristics for adversarial network preset.

    Creates a mix of:
    - 30% good peers [0.0-0.2, 0.0-0.2]
    - 40% neutral peers [0.4-0.6, 0.4-0.6]
    - 30% bad peers [0.8-1.0, 0.8-1.0]

    Args:
        peer_index: Index of peer being created (0-based)
        total_peers: Total number of peers in network

    Returns:
        Tuple of (competence, maliciousness) values
    """
    # Determine peer category based on index
    good_count = int(total_peers * 0.3)
    neutral_count = int(total_peers * 0.4)

    if peer_index < good_count:
        # Good peer: low competence (skilled), low maliciousness (helpful)
        competence = random.uniform(0.0, 0.2)
        maliciousness = random.uniform(0.0, 0.2)
    elif peer_index < good_count + neutral_count:
        # Neutral peer: moderate characteristics
        competence = random.uniform(0.4, 0.6)
        maliciousness = random.uniform(0.4, 0.6)
    else:
        # Bad peer: high competence (unskilled), high maliciousness (harmful)
        competence = random.uniform(0.8, 1.0)
        maliciousness = random.uniform(0.8, 1.0)

    return (competence, maliciousness)
