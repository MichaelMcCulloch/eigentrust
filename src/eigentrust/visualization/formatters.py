"""Convergence visualization formatters for EigenTrust.

Provides plots showing trust score evolution over iterations.
"""

import warnings
from pathlib import Path

import matplotlib.pyplot as plt

from eigentrust.domain.simulation import Simulation


class ConvergencePlotter:
    """Visualizer for algorithm convergence tracking.

    Renders trust score evolution and convergence metrics over iterations.

    Attributes:
        dpi: Resolution for saved images
        show_top_n: Number of top peers to highlight in plots
    """

    def __init__(self, dpi: int = 300, show_top_n: int = 5):
        """Initialize convergence plotter.

        Args:
            dpi: Resolution for saved images (default: 300)
            show_top_n: Number of peers to highlight (default: 5)
        """
        self.dpi = dpi
        self.show_top_n = show_top_n

    def visualize(
        self, simulation: Simulation, output_path: Path, title: str | None = None
    ) -> None:
        """Generate convergence visualization with trust evolution and delta plots.

        Args:
            simulation: Simulation with convergence history
            output_path: Path to save the visualization
            title: Optional title for the plot

        Raises:
            ValueError: If simulation has no convergence history
        """
        if not simulation.convergence_history:
            raise ValueError("Simulation has no convergence history. Run with track_history=True")

        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Plot 1: Trust scores over iterations
        self._plot_trust_evolution(ax1, simulation)

        # Plot 2: Delta (convergence metric) over iterations
        self._plot_convergence_delta(ax2, simulation)

        # Add main title
        if title is None:
            title = f"EigenTrust Convergence ({len(simulation.peers)} peers, {len(simulation.convergence_history)-1} iterations)"
        fig.suptitle(title, fontsize=14, fontweight="bold")

        # Save figure
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Tight layout not applied")
            try:
                plt.tight_layout()
            except (ValueError, UserWarning):
                # Tight layout may fail with complex plots - ignore and use bbox_inches='tight' instead
                pass
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)

    def _plot_trust_evolution(self, ax, simulation: Simulation) -> None:
        """Plot trust scores over iterations.

        Args:
            ax: Matplotlib axis
            simulation: Simulation with convergence history
        """
        history = simulation.convergence_history

        # Extract iterations
        iterations = [h["iteration"] for h in history]

        # Get final scores to determine top peers
        final_scores = history[-1]["trust_scores"]
        sorted_peers = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        top_peer_ids = [peer_id for peer_id, _ in sorted_peers[: self.show_top_n]]

        # Plot trust score evolution for top peers
        for peer_id in top_peer_ids:
            scores = [h["trust_scores"][peer_id] for h in history]
            peer = next(p for p in simulation.peers if p.peer_id == peer_id)
            ax.plot(
                iterations,
                scores,
                marker="o",
                markersize=3,
                label=f"{peer.display_name} (final: {final_scores[peer_id]:.4f})",
                linewidth=2,
            )

        # Plot average for all other peers (gray line)
        other_peer_ids = [p.peer_id for p in simulation.peers if p.peer_id not in top_peer_ids]
        if other_peer_ids:
            avg_scores = []
            for h in history:
                avg = sum(h["trust_scores"][pid] for pid in other_peer_ids) / len(other_peer_ids)
                avg_scores.append(avg)
            ax.plot(
                iterations,
                avg_scores,
                color="gray",
                linestyle="--",
                linewidth=1.5,
                alpha=0.5,
                label=f"Average of other {len(other_peer_ids)} peers",
            )

        ax.set_xlabel("Iteration", fontsize=12)
        ax.set_ylabel("Trust Score", fontsize=12)
        ax.set_title("Trust Score Evolution Over Iterations", fontsize=13, fontweight="bold")
        ax.legend(loc="best", fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, None)  # Start y-axis at 0

    def _plot_convergence_delta(self, ax, simulation: Simulation) -> None:
        """Plot convergence delta (change) over iterations.

        Args:
            ax: Matplotlib axis
            simulation: Simulation with convergence history
        """
        history = simulation.convergence_history

        # Extract iterations and deltas (skip iteration 0 which has delta=1.0)
        iterations = [h["iteration"] for h in history[1:]]
        deltas = [h["delta"] for h in history[1:]]

        # Plot delta on log scale
        ax.semilogy(
            iterations,
            deltas,
            marker="o",
            markersize=4,
            color="darkblue",
            linewidth=2,
            label="Change in trust scores (||t_new - t_old||)",
        )

        # Add horizontal line for epsilon threshold if available
        if simulation.convergence_history:
            # Try to get epsilon from the simulation's last run
            # We'll use a reasonable default if not available
            epsilon = 0.001  # Default value
            ax.axhline(
                y=epsilon,
                color="red",
                linestyle="--",
                linewidth=2,
                label=f"Convergence threshold (ε = {epsilon})",
            )

        ax.set_xlabel("Iteration", fontsize=12)
        ax.set_ylabel("Delta (log scale)", fontsize=12)
        ax.set_title("Convergence Metric Over Iterations", fontsize=13, fontweight="bold")
        ax.legend(loc="best", fontsize=10)
        ax.grid(True, alpha=0.3, which="both")

        # Add annotation for convergence point if converged
        if len(deltas) > 0:
            converged_idx = None
            for i, delta in enumerate(deltas):
                if delta < epsilon:
                    converged_idx = i
                    break

            if converged_idx is not None:
                converged_at = iterations[converged_idx]
                converged_delta = deltas[converged_idx]

                # Position annotation in data coordinates
                # For log scale y-axis, we need to position in log space
                y_min, y_max = ax.get_ylim()
                x_min, x_max = ax.get_xlim()

                # Place text in the middle-right area of the plot
                text_x = x_min + 0.6 * (x_max - x_min)
                # In log space, geometric mean for y position
                text_y = (y_max * y_min) ** 0.5

                ax.annotate(
                    f"Converged at iteration {converged_at}",
                    xy=(converged_at, converged_delta),
                    xytext=(text_x, text_y),
                    arrowprops=dict(arrowstyle="->", color="green", lw=2),
                    fontsize=10,
                    color="green",
                    fontweight="bold",
                    bbox=dict(
                        boxstyle="round,pad=0.5", facecolor="white", edgecolor="green", alpha=0.8
                    ),
                )
