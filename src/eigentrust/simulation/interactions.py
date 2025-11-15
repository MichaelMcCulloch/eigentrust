"""Interaction simulation for EigenTrust.

Simulates peer-to-peer interactions based on peer characteristics.
"""

import random
from typing import List, Optional
from collections import defaultdict

from eigentrust.domain.peer import Peer
from eigentrust.domain.interaction import Interaction, InteractionOutcome


def compute_interaction_outcome(peer: Peer, partner: Peer) -> InteractionOutcome:
    """Compute outcome of interaction based on peer characteristics.

    Success probability formula:
        P(success) = (1 - competence) * (1 - maliciousness) + noise

    Where:
        - competence: 0.0 = hypercompetent, 1.0 = incompetent
        - maliciousness: 0.0 = altruistic, 1.0 = malicious
        - noise: small random factor for realism

    Args:
        peer: Peer providing service (target)
        partner: Peer requesting service (source)

    Returns:
        InteractionOutcome.SUCCESS or InteractionOutcome.FAILURE

    Example:
        >>> peer = Peer(competence=0.0, maliciousness=0.0)  # Good peer
        >>> partner = Peer(competence=0.5, maliciousness=0.5)
        >>> outcome = compute_interaction_outcome(peer, partner)
        >>> # Good peer has high success probability
    """
    # Base success rate: inversely related to incompetence
    technical_success = 1.0 - peer.competence

    # Maliciousness reduces willingness to help
    cooperation_factor = 1.0 - peer.maliciousness

    # Combined probability
    base_prob = technical_success * cooperation_factor

    # Add small random noise for realism
    noise = random.gauss(0, 0.05)
    final_prob = max(0.0, min(1.0, base_prob + noise))

    # Determine outcome
    return InteractionOutcome.SUCCESS if random.random() < final_prob else InteractionOutcome.FAILURE


def simulate_interactions(
    peers: List[Peer],
    num_interactions: int,
    seed: Optional[int] = None,
    use_preferential_attachment: bool = True
) -> List[Interaction]:
    """Simulate interactions between peers with optional preferential attachment.

    Uses Barabási-Albert inspired preferential attachment where peers with more
    successful past interactions are more likely to be selected as targets.
    This creates scale-free, small-world network properties.

    Args:
        peers: List of peers in the network
        num_interactions: Number of interactions to simulate
        seed: Optional random seed for reproducibility
        use_preferential_attachment: If True, use preferential attachment based
            on peer degree/success. If False, use uniform random selection.

    Returns:
        List of Interaction objects

    Raises:
        ValueError: If fewer than 2 peers provided

    Example:
        >>> peer1 = Peer(competence=0.1, maliciousness=0.1)
        >>> peer2 = Peer(competence=0.9, maliciousness=0.9)
        >>> interactions = simulate_interactions([peer1, peer2], 10, seed=42)
        >>> len(interactions)
        10
    """
    if len(peers) < 2:
        raise ValueError("Need at least 2 peers to simulate interactions")

    # Set random seed for reproducibility
    if seed is not None:
        random.seed(seed)

    interactions = []

    # Track peer interaction counts for preferential attachment
    # Format: {peer_id: successful_interactions_count}
    peer_success_counts = defaultdict(int)

    # Initialize all peers with a small base count to avoid zero probability
    for peer in peers:
        peer_success_counts[peer.peer_id] = 1

    for _ in range(num_interactions):
        # Select source uniformly (requesters chosen randomly)
        source = random.choice(peers)

        # Select target based on preferential attachment or uniformly
        if use_preferential_attachment:
            # Build probability distribution based on success counts
            # Peers with more successful interactions are more likely to be selected
            available_targets = [p for p in peers if p.peer_id != source.peer_id]
            weights = [peer_success_counts[p.peer_id] for p in available_targets]
            total_weight = sum(weights)

            if total_weight > 0:
                probabilities = [w / total_weight for w in weights]
                target = random.choices(available_targets, weights=probabilities, k=1)[0]
            else:
                # Fallback to uniform if no weights
                target = random.choice(available_targets)
        else:
            # Uniform random selection (original behavior)
            available_targets = [p for p in peers if p.peer_id != source.peer_id]
            target = random.choice(available_targets)

        # Compute outcome based on target peer's characteristics
        outcome = compute_interaction_outcome(target, source)

        # Update success counts for preferential attachment
        if outcome == InteractionOutcome.SUCCESS:
            peer_success_counts[target.peer_id] += 1

        # Create interaction record
        interaction = Interaction(
            source_peer_id=source.peer_id,
            target_peer_id=target.peer_id,
            outcome=outcome
        )

        interactions.append(interaction)

    return interactions
