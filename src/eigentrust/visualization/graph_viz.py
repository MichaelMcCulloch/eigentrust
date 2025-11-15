"""Trust graph visualization for EigenTrust.

Provides network graph rendering with visual encoding for peer characteristics.
"""

import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional, Tuple

from eigentrust.domain.simulation import Simulation


class GraphVisualizer:
    """Visualizer for trust network graphs.

    Renders peer networks as directed graphs with:
    - Node colors encoding maliciousness (red) vs altruism (green)
    - Node sizes encoding competence (larger = more competent)
    - Edge thickness encoding trust weights

    Attributes:
        dpi: Resolution for saved images
        edge_threshold: Minimum trust value to show edge
        layout_algorithm: NetworkX layout algorithm name
    """

    def __init__(
        self,
        dpi: int = 300,
        edge_threshold: float = 0.01,
        layout_algorithm: str = "spring"
    ):
        """Initialize graph visualizer.

        Args:
            dpi: Resolution for saved images (default: 300)
            edge_threshold: Min trust value for edges (default: 0.01)
            layout_algorithm: Layout type (spring, circular, kamada_kawai)
        """
        self.dpi = dpi
        self.edge_threshold = edge_threshold
        self.layout_algorithm = layout_algorithm

    def visualize(
        self,
        simulation: Simulation,
        output_path: Path,
        title: Optional[str] = None,
        show_labels: bool = True
    ) -> None:
        """Generate and save trust graph visualization.

        Args:
            simulation: Simulation with peer and trust data
            output_path: Path to save the visualization
            title: Optional title for the plot
            show_labels: Whether to show peer names as labels

        Raises:
            ValueError: If simulation has insufficient data
        """
        # Build directed graph from simulation
        G = self._build_graph(simulation)

        # Get layout
        pos = self._compute_layout(G)

        # Prepare node visual properties
        node_colors = self._compute_node_colors(simulation)
        node_sizes = self._compute_node_sizes(simulation)

        # Prepare edge visual properties
        edge_widths = self._compute_edge_widths(G)

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))

        # Draw edges with varying thickness
        nx.draw_networkx_edges(
            G, pos,
            width=edge_widths,
            alpha=0.6,
            edge_color='gray',
            arrows=True,
            arrowsize=15,
            arrowstyle='->',
            connectionstyle='arc3,rad=0.1',
            ax=ax
        )

        # Draw nodes with color and size encoding
        nx.draw_networkx_nodes(
            G, pos,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.9,
            ax=ax
        )

        # Draw labels if requested
        if show_labels:
            labels = {
                peer.peer_id: peer.display_name
                for peer in simulation.peers
            }
            nx.draw_networkx_labels(
                G, pos,
                labels=labels,
                font_size=8,
                font_weight='bold',
                ax=ax
            )

        # Add title
        if title is None:
            title = f'Trust Network Graph ({len(simulation.peers)} peers)'
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Add legend
        self._add_legend(ax)

        # Remove axis
        ax.axis('off')

        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)

    def _build_graph(self, simulation: Simulation) -> nx.DiGraph:
        """Build NetworkX directed graph from simulation.

        Args:
            simulation: Simulation with peer and trust data

        Returns:
            NetworkX DiGraph
        """
        G = nx.DiGraph()

        # Add nodes with attributes
        for peer in simulation.peers:
            G.add_node(
                peer.peer_id,
                competence=peer.competence,
                maliciousness=peer.maliciousness,
                global_trust=peer.global_trust or 0.0,
                display_name=peer.display_name
            )

        # Build trust matrix
        trust_matrix = simulation._build_trust_matrix()
        matrix_np = trust_matrix.to_numpy()

        # Add edges for non-zero trust values above threshold
        peer_ids = list(trust_matrix.peer_mapping.keys())
        for i, source_id in enumerate(peer_ids):
            for j, target_id in enumerate(peer_ids):
                if i != j:  # Skip self-loops
                    trust_value = matrix_np[i, j]
                    if trust_value > self.edge_threshold:
                        G.add_edge(
                            source_id,
                            target_id,
                            weight=float(trust_value)
                        )

        return G

    def _compute_layout(self, G: nx.DiGraph) -> dict:
        """Compute force-directed graph layout positions.

        Uses Fruchterman-Reingold force-directed algorithm (spring layout)
        with edge weights to cluster trusted peers together.

        Args:
            G: NetworkX graph

        Returns:
            Dictionary mapping node IDs to (x, y) positions
        """
        if self.layout_algorithm == "spring":
            # Force-directed layout with edge weight consideration
            # k: optimal distance between nodes
            # iterations: more iterations = better layout
            # weight: edge attribute to use for spring force (higher weight = shorter distance)
            return nx.spring_layout(
                G,
                k=2.0,  # Increase spacing
                iterations=100,  # More iterations for better convergence
                weight='weight',  # Use trust weights
                seed=42
            )
        elif self.layout_algorithm == "circular":
            return nx.circular_layout(G)
        elif self.layout_algorithm == "kamada_kawai":
            # Kamada-Kawai also respects edge weights
            return nx.kamada_kawai_layout(G, weight='weight')
        else:
            # Default to force-directed spring layout
            return nx.spring_layout(G, k=2.0, iterations=100, weight='weight', seed=42)

    def _compute_node_colors(self, simulation: Simulation) -> list:
        """Compute node colors based on peer characteristics.

        Color encoding:
        - Red channel: maliciousness (0.0 = low, 1.0 = high)
        - Green channel: altruism (1.0 - maliciousness)
        - Blue channel: fixed at 0.3 for visibility

        Args:
            simulation: Simulation with peer data

        Returns:
            List of RGB tuples for each node
        """
        colors = []
        for peer in simulation.peers:
            r = peer.maliciousness
            g = 1.0 - peer.maliciousness
            b = 0.3
            colors.append((r, g, b))
        return colors

    def _compute_node_sizes(self, simulation: Simulation) -> list:
        """Compute node sizes based on global trust scores.

        Larger nodes = higher trust scores

        Args:
            simulation: Simulation with peer data

        Returns:
            List of node sizes
        """
        base_size = 300
        max_size = 1500
        sizes = []

        # Get trust score range
        trust_scores = [peer.global_trust or 0.0 for peer in simulation.peers]
        min_trust = min(trust_scores) if trust_scores else 0.0
        max_trust = max(trust_scores) if trust_scores else 1.0
        trust_range = max_trust - min_trust if max_trust > min_trust else 1.0

        for peer in simulation.peers:
            trust = peer.global_trust or 0.0
            # Normalize trust to [0, 1]
            normalized_trust = (trust - min_trust) / trust_range if trust_range > 0 else 0.5
            # Scale to size range
            size = base_size + normalized_trust * (max_size - base_size)
            sizes.append(size)
        return sizes

    def _compute_edge_widths(self, G: nx.DiGraph) -> list:
        """Compute edge widths based on trust weights.

        Args:
            G: NetworkX graph with edge weights

        Returns:
            List of edge widths
        """
        base_width = 1.0
        max_width = 5.0
        widths = []

        for u, v, data in G.edges(data=True):
            weight = data.get('weight', 0.0)
            width = base_width + (max_width - base_width) * weight
            widths.append(width)

        return widths

    def _add_legend(self, ax) -> None:
        """Add legend explaining visual encoding.

        Args:
            ax: Matplotlib axis
        """
        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D

        legend_elements = [
            Patch(facecolor=(0.0, 1.0, 0.3), label='Altruistic (low maliciousness)'),
            Patch(facecolor=(1.0, 0.0, 0.3), label='Malicious (high maliciousness)'),
            Line2D([0], [0], marker='o', color='w',
                   markerfacecolor='gray', markersize=14,
                   label='Large = High global trust'),
            Line2D([0], [0], marker='o', color='w',
                   markerfacecolor='gray', markersize=7,
                   label='Small = Low global trust'),
            Line2D([0], [0], color='gray', linewidth=3,
                   label='Thick edge = High local trust'),
            Line2D([0], [0], color='gray', linewidth=1,
                   label='Thin edge = Low local trust'),
        ]

        ax.legend(
            handles=legend_elements,
            loc='upper left',
            fontsize=9,
            framealpha=0.9
        )
