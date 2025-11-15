"""Trust matrix visualization for EigenTrust.

Provides heatmap rendering of trust matrices with annotations.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from eigentrust.domain.simulation import Simulation
from eigentrust.domain.trust_matrix import TrustMatrix


class MatrixVisualizer:
    """Visualizer for trust matrix heatmaps.

    Renders N×N trust matrices as annotated heatmaps with colorbar.

    Attributes:
        colormap: Matplotlib colormap name
        dpi: Resolution for saved images
        annotate_threshold: Maximum matrix size for cell annotations
    """

    def __init__(self, colormap: str = "viridis", dpi: int = 300, annotate_threshold: int = 20):
        """Initialize matrix visualizer.

        Args:
            colormap: Name of matplotlib colormap (default: viridis)
            dpi: Resolution for saved images (default: 300)
            annotate_threshold: Max size for annotations (default: 20)
        """
        self.colormap = colormap
        self.dpi = dpi
        self.annotate_threshold = annotate_threshold

    def visualize(
        self,
        simulation: Simulation,
        output_path: Path,
        title: str | None = None,
        show_annotations: bool | None = None,
    ) -> None:
        """Generate and save trust matrix heatmap.

        Args:
            simulation: Simulation with trust matrix data
            output_path: Path to save the visualization
            title: Optional title for the plot
            show_annotations: Override automatic annotation decision

        Raises:
            ValueError: If simulation has no trust matrix data
        """
        # Build trust matrix from simulation
        trust_matrix = simulation._build_trust_matrix()
        matrix_np = trust_matrix.to_numpy()

        # Get peer display names for axis labels
        peer_ids = list(trust_matrix.peer_mapping.keys())
        peer_labels = [
            next(p.display_name for p in simulation.peers if p.peer_id == pid) for pid in peer_ids
        ]

        # Determine if we should annotate
        n = len(peer_labels)
        if show_annotations is None:
            show_annotations = n <= self.annotate_threshold

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 8))

        # Render heatmap
        im = ax.imshow(
            matrix_np,
            cmap=self.colormap,
            aspect="auto",
            vmin=0.0,
            vmax=1.0,
            interpolation="nearest",
        )

        # Add colorbar
        plt.colorbar(im, ax=ax, label="Local Trust Value")

        # Set axis labels
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(peer_labels, rotation=45, ha="right")
        ax.set_yticklabels(peer_labels)

        # Add axis titles
        ax.set_xlabel("Trustee (peer being evaluated)")
        ax.set_ylabel("Truster (peer assigning trust)")

        # Add title
        if title is None:
            title = f"Trust Matrix ({n}×{n} peers)"
        ax.set_title(title)

        # Add cell annotations if matrix is small enough
        if show_annotations:
            self._add_annotations(ax, matrix_np, n)

        # Add grid
        ax.set_xticks(np.arange(n) - 0.5, minor=True)
        ax.set_yticks(np.arange(n) - 0.5, minor=True)
        ax.grid(which="minor", color="white", linestyle="-", linewidth=0.5)

        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)

    def _add_annotations(self, ax, matrix: np.ndarray, n: int) -> None:
        """Add value annotations to matrix cells.

        Args:
            ax: Matplotlib axis
            matrix: Trust matrix as numpy array
            n: Matrix dimension
        """
        for i in range(n):
            for j in range(n):
                value = matrix[i, j]

                # Choose text color based on background darkness
                # Use white text on dark backgrounds
                text_color = "white" if value > 0.5 else "black"

                # Format value with 2 decimal places
                ax.text(
                    j, i, f"{value:.2f}", ha="center", va="center", color=text_color, fontsize=8
                )

    def visualize_from_matrix(
        self,
        trust_matrix: TrustMatrix,
        peer_labels: list[str],
        output_path: Path,
        title: str | None = None,
        show_annotations: bool | None = None,
    ) -> None:
        """Visualize trust matrix directly without simulation.

        Args:
            trust_matrix: TrustMatrix entity
            peer_labels: Display names for peers
            output_path: Path to save the visualization
            title: Optional title for the plot
            show_annotations: Override automatic annotation decision
        """
        matrix_np = trust_matrix.to_numpy()
        n = len(peer_labels)

        # Determine if we should annotate
        if show_annotations is None:
            show_annotations = n <= self.annotate_threshold

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 8))

        # Render heatmap
        im = ax.imshow(
            matrix_np,
            cmap=self.colormap,
            aspect="auto",
            vmin=0.0,
            vmax=1.0,
            interpolation="nearest",
        )

        # Add colorbar
        plt.colorbar(im, ax=ax, label="Local Trust Value")

        # Set axis labels
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(peer_labels, rotation=45, ha="right")
        ax.set_yticklabels(peer_labels)

        # Add axis titles
        ax.set_xlabel("Trustee (peer being evaluated)")
        ax.set_ylabel("Truster (peer assigning trust)")

        # Add title
        if title is None:
            title = f"Trust Matrix ({n}×{n} peers)"
        ax.set_title(title)

        # Add cell annotations if matrix is small enough
        if show_annotations:
            self._add_annotations(ax, matrix_np, n)

        # Add grid
        ax.set_xticks(np.arange(n) - 0.5, minor=True)
        ax.set_yticks(np.arange(n) - 0.5, minor=True)
        ax.grid(which="minor", color="white", linestyle="-", linewidth=0.5)

        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
