"""CLI entry point for EigenTrust demonstration.

Implements command-line interface using Typer framework.
"""

import json
from pathlib import Path
from typing import Annotated

import typer

from eigentrust.simulation.network import create_network
from eigentrust.utils.io import load_simulation, save_simulation

app = typer.Typer(
    name="eigentrust",
    help="EigenTrust P2P trust algorithm demonstration",
    add_completion=False,
)


@app.command()
def create(
    peers: Annotated[
        int,
        typer.Option(help="Number of peers in network (2-500)"),
    ] = 10,
    output: Annotated[
        Path,
        typer.Option(help="Output file path for simulation"),
    ] = Path("simulation.json"),
    seed: Annotated[
        int | None,
        typer.Option(help="Random seed for reproducibility"),
    ] = None,
    preset: Annotated[
        str,
        typer.Option(help="Peer distribution preset: random, uniform, adversarial"),
    ] = "random",
    verbose: Annotated[
        bool,
        typer.Option(help="Enable verbose logging"),
    ] = False,
) -> None:
    """Create a new peer network simulation with configured characteristics."""
    try:
        # Create network
        if verbose:
            typer.echo(f"Creating simulation with {peers} peers using '{preset}' preset...")

        sim = create_network(peer_count=peers, preset=preset, seed=seed)

        # Save to file
        save_simulation(sim, output)

        # Output success message
        typer.echo(f"Created simulation with {len(sim.peers)} peers")
        typer.echo(f"Simulation ID: {sim.simulation_id}")

        if preset == "adversarial":
            # Count peer types
            good_peers = sum(1 for p in sim.peers if p.competence <= 0.2 and p.maliciousness <= 0.2)
            bad_peers = sum(1 for p in sim.peers if p.competence >= 0.8 and p.maliciousness >= 0.8)
            neutral_peers = len(sim.peers) - good_peers - bad_peers

            typer.echo(f"  - {good_peers} good peers (competent & altruistic)")
            typer.echo(f"  - {neutral_peers} neutral peers")
            typer.echo(f"  - {bad_peers} bad peers (incompetent & malicious)")

        typer.echo(f"Saved to: {output}")

        # Exit successfully
        raise typer.Exit(0)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def simulate(
    input: Annotated[
        Path,
        typer.Option(help="Input simulation file"),
    ],
    interactions: Annotated[
        int,
        typer.Option(help="Number of interactions to simulate"),
    ] = 100,
    output: Annotated[
        Path,
        typer.Option(help="Output file path"),
    ] = Path("simulation_with_interactions.json"),
    preferential_attachment: Annotated[
        bool,
        typer.Option(
            "--preferential-attachment/--random",
            help="Use Barabási-Albert preferential attachment (default: random)",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(help="Enable verbose logging"),
    ] = False,
) -> None:
    """Simulate peer-to-peer interactions in the network."""
    try:
        # Load simulation
        if verbose:
            typer.echo(f"Loading simulation from {input}...")
        sim = load_simulation(input)

        # Simulate interactions
        if verbose:
            mode = "preferential attachment" if preferential_attachment else "random"
            typer.echo(f"Simulating {interactions} peer-to-peer interactions ({mode})...")

        new_interactions = sim.simulate_interactions(
            interactions, use_preferential_attachment=preferential_attachment
        )

        # Save updated simulation
        save_simulation(sim, output)

        # Output summary
        typer.echo(f"Simulated {len(new_interactions)} interactions")
        typer.echo(f"Total interactions: {len(sim.interactions)}")

        # Count outcomes
        from eigentrust.domain.interaction import InteractionOutcome

        success_count = sum(1 for i in new_interactions if i.outcome == InteractionOutcome.SUCCESS)
        failure_count = len(new_interactions) - success_count
        typer.echo(f"  - Successes: {success_count}")
        typer.echo(f"  - Failures: {failure_count}")

        typer.echo(f"Saved to: {output}")
        raise typer.Exit(0)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def run(
    input: Annotated[
        Path,
        typer.Option(help="Input simulation file"),
    ],
    max_iterations: Annotated[
        int,
        typer.Option(help="Maximum EigenTrust iterations"),
    ] = 100,
    epsilon: Annotated[
        float,
        typer.Option(help="Convergence threshold"),
    ] = 0.001,
    output: Annotated[
        Path,
        typer.Option(help="Output file path"),
    ] = Path("simulation_results.json"),
    track_history: Annotated[
        bool,
        typer.Option(help="Track convergence history (needed for convergence visualization)"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(help="Enable verbose logging"),
    ] = False,
) -> None:
    """Run EigenTrust algorithm on simulation."""
    try:
        # Load simulation
        if verbose:
            typer.echo(f"Loading simulation from {input}...")
        sim = load_simulation(input)

        # Check for interactions
        if len(sim.interactions) == 0:
            typer.echo("Warning: No interactions found. Run 'simulate' command first.", err=True)

        # Run EigenTrust algorithm
        if verbose:
            typer.echo(
                f"Running EigenTrust algorithm (max_iterations={max_iterations}, epsilon={epsilon})..."
            )

        trust_scores = sim.run_algorithm(
            max_iterations=max_iterations, epsilon=epsilon, track_history=track_history
        )

        # Save results
        save_simulation(sim, output)

        # Output results
        typer.echo(f"Algorithm completed in {trust_scores.iteration_count} iterations")
        typer.echo(f"Converged: {trust_scores.converged}")
        typer.echo(f"Final delta: {trust_scores.final_delta:.6f}")

        # Show top trust scores
        typer.echo("\nTop Trust Scores:")
        sorted_scores = sorted(trust_scores.scores.items(), key=lambda x: x[1], reverse=True)
        for i, (peer_id, score) in enumerate(sorted_scores[:5], 1):
            peer = next(p for p in sim.peers if p.peer_id == peer_id)
            typer.echo(
                f"  {i}. {peer.display_name}: {score:.4f} "
                f"[comp={peer.competence:.2f}, mal={peer.maliciousness:.2f}]"
            )

        if len(sorted_scores) > 5:
            typer.echo(f"  ... ({len(sorted_scores) - 5} more)")

        typer.echo(f"\nSaved to: {output}")
        raise typer.Exit(0)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def info(
    input: Annotated[
        Path,
        typer.Option(help="Input simulation file"),
    ],
    format: Annotated[
        str,
        typer.Option(help="Output format: text, json"),
    ] = "text",
) -> None:
    """Display information about a simulation file."""
    try:
        # Load simulation
        sim = load_simulation(input)

        if format == "json":
            # Output as JSON
            output = {
                "simulation_id": sim.simulation_id,
                "created_at": sim.created_at.isoformat(),
                "state": sim.state.value,
                "peers": len(sim.peers),
                "interactions": len(sim.interactions),
            }
            typer.echo(json.dumps(output, indent=2))
        else:
            # Output as text
            typer.echo(f"Simulation ID: {sim.simulation_id}")
            typer.echo(f"Created: {sim.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            typer.echo(f"State: {sim.state.value}")
            typer.echo(f"Peers: {len(sim.peers)}")
            typer.echo(f"Interactions: {len(sim.interactions)}")

            if sim.peers:
                typer.echo("\nPeer Characteristics:")
                for i, peer in enumerate(sim.peers[:10], 1):  # Show first 10
                    typer.echo(
                        f"  {peer.display_name} "
                        f"[{peer.competence:.2f}, {peer.maliciousness:.2f}]"
                    )
                if len(sim.peers) > 10:
                    typer.echo(f"  ... ({len(sim.peers) - 10} more)")

        raise typer.Exit(0)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def visualize_matrix(
    input: Annotated[
        Path,
        typer.Option(help="Input simulation file"),
    ],
    output: Annotated[
        Path,
        typer.Option(help="Output image file path"),
    ] = Path("trust_matrix.png"),
    title: Annotated[
        str | None,
        typer.Option(help="Title for the visualization"),
    ] = None,
    colormap: Annotated[
        str,
        typer.Option(help="Matplotlib colormap (viridis, plasma, inferno, magma, etc.)"),
    ] = "viridis",
    dpi: Annotated[
        int,
        typer.Option(help="Resolution (DPI) for output image"),
    ] = 300,
    annotate: Annotated[
        bool | None,
        typer.Option(help="Force show/hide cell annotations (auto if not specified)"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(help="Enable verbose logging"),
    ] = False,
) -> None:
    """Visualize trust matrix as heatmap."""
    try:
        # Load simulation
        if verbose:
            typer.echo(f"Loading simulation from {input}...")
        sim = load_simulation(input)

        # Check for algorithm results
        if not any(p.global_trust is not None for p in sim.peers):
            typer.echo("Warning: No trust scores found. Run 'run' command first.", err=True)

        # Create visualizer
        if verbose:
            typer.echo("Generating trust matrix visualization...")

        from eigentrust.visualization.matrix_viz import MatrixVisualizer

        visualizer = MatrixVisualizer(colormap=colormap, dpi=dpi)

        # Generate visualization
        visualizer.visualize(
            simulation=sim, output_path=output, title=title, show_annotations=annotate
        )

        # Output success
        typer.echo(f"Trust matrix visualization saved to: {output}")
        typer.echo(f"Matrix size: {len(sim.peers)}×{len(sim.peers)}")
        raise typer.Exit(0)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def visualize_graph(
    input: Annotated[
        Path,
        typer.Option(help="Input simulation file"),
    ],
    output: Annotated[
        Path,
        typer.Option(help="Output image file path"),
    ] = Path("trust_graph.png"),
    title: Annotated[
        str | None,
        typer.Option(help="Title for the visualization"),
    ] = None,
    layout: Annotated[
        str,
        typer.Option(help="Graph layout algorithm (spring, circular, kamada_kawai)"),
    ] = "spring",
    edge_threshold: Annotated[
        float,
        typer.Option(help="Minimum trust value to show edge"),
    ] = 0.01,
    dpi: Annotated[
        int,
        typer.Option(help="Resolution (DPI) for output image"),
    ] = 300,
    show_labels: Annotated[
        bool,
        typer.Option(help="Show peer names as labels"),
    ] = True,
    verbose: Annotated[
        bool,
        typer.Option(help="Enable verbose logging"),
    ] = False,
) -> None:
    """Visualize trust network as directed graph."""
    try:
        # Load simulation
        if verbose:
            typer.echo(f"Loading simulation from {input}...")
        sim = load_simulation(input)

        # Create visualizer
        if verbose:
            typer.echo("Generating trust graph visualization...")

        from eigentrust.visualization.graph_viz import GraphVisualizer

        visualizer = GraphVisualizer(
            dpi=dpi, edge_threshold=edge_threshold, layout_algorithm=layout
        )

        # Generate visualization
        visualizer.visualize(
            simulation=sim, output_path=output, title=title, show_labels=show_labels
        )

        # Output success
        typer.echo(f"Trust graph visualization saved to: {output}")
        typer.echo(f"Network: {len(sim.peers)} peers")
        raise typer.Exit(0)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def visualize_convergence(
    input: Annotated[
        Path,
        typer.Option(help="Input simulation file (must have convergence history)"),
    ],
    output: Annotated[
        Path,
        typer.Option(help="Output image file path"),
    ] = Path("convergence.png"),
    title: Annotated[
        str | None,
        typer.Option(help="Title for the visualization"),
    ] = None,
    top_n: Annotated[
        int,
        typer.Option(help="Number of top peers to highlight"),
    ] = 5,
    dpi: Annotated[
        int,
        typer.Option(help="Resolution (DPI) for output image"),
    ] = 300,
    verbose: Annotated[
        bool,
        typer.Option(help="Enable verbose logging"),
    ] = False,
) -> None:
    """Visualize algorithm convergence history."""
    try:
        # Load simulation
        if verbose:
            typer.echo(f"Loading simulation from {input}...")
        sim = load_simulation(input)

        # Check for convergence history
        if not sim.convergence_history:
            typer.echo(
                "Error: No convergence history found. Run 'run' command with --track-history flag.",
                err=True,
            )
            raise typer.Exit(1)

        # Create visualizer
        if verbose:
            typer.echo("Generating convergence visualization...")

        from eigentrust.visualization.formatters import ConvergencePlotter

        plotter = ConvergencePlotter(dpi=dpi, show_top_n=top_n)

        # Generate visualization
        plotter.visualize(simulation=sim, output_path=output, title=title)

        # Output success
        typer.echo(f"Convergence visualization saved to: {output}")
        typer.echo(f"Iterations: {len(sim.convergence_history) - 1}")
        raise typer.Exit(0)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def all(
    peers: Annotated[
        int,
        typer.Option(help="Number of peers in network"),
    ] = 10,
    interactions: Annotated[
        int,
        typer.Option(help="Number of interactions to simulate"),
    ] = 100,
    max_iterations: Annotated[
        int,
        typer.Option(help="Maximum EigenTrust iterations"),
    ] = 100,
    epsilon: Annotated[
        float,
        typer.Option(help="Convergence threshold"),
    ] = 0.001,
    preset: Annotated[
        str,
        typer.Option(help="Peer distribution preset"),
    ] = "random",
    output_dir: Annotated[
        Path,
        typer.Option(help="Output directory for all files"),
    ] = Path("."),
    seed: Annotated[
        int | None,
        typer.Option(help="Random seed for reproducibility"),
    ] = None,
    preferential_attachment: Annotated[
        bool,
        typer.Option(
            "--preferential-attachment/--random",
            help="Use Barabási-Albert preferential attachment (default: random)",
        ),
    ] = False,
) -> None:
    """Run complete EigenTrust pipeline: create -> simulate -> run -> visualize."""
    try:
        # Create output directory if needed
        output_dir.mkdir(parents=True, exist_ok=True)

        typer.echo("=" * 60)
        typer.echo("EigenTrust Complete Pipeline")
        typer.echo("=" * 60)

        # Step 1: Create network
        typer.echo("\n[1/5] Creating peer network...")
        from eigentrust.simulation.network import create_network

        sim = create_network(peer_count=peers, preset=preset, seed=seed)
        network_file = output_dir / "network.json"
        from eigentrust.utils.io import save_simulation

        save_simulation(sim, network_file)
        typer.echo(f"  ✓ Created {len(sim.peers)} peers")

        # Step 2: Simulate interactions
        mode = "preferential attachment" if preferential_attachment else "random selection"
        typer.echo(f"\n[2/5] Simulating {interactions} interactions ({mode})...")
        sim.simulate_interactions(interactions, use_preferential_attachment=preferential_attachment)
        sim_file = output_dir / "simulation.json"
        save_simulation(sim, sim_file)

        from eigentrust.domain.interaction import InteractionOutcome

        success_count = sum(1 for i in sim.interactions if i.outcome == InteractionOutcome.SUCCESS)
        typer.echo(f"  ✓ Simulated {len(sim.interactions)} interactions")
        typer.echo(f"    - Successes: {success_count}")
        typer.echo(f"    - Failures: {len(sim.interactions) - success_count}")

        # Step 3: Run EigenTrust algorithm
        typer.echo("\n[3/5] Running EigenTrust algorithm...")
        trust_scores = sim.run_algorithm(
            max_iterations=max_iterations, epsilon=epsilon, track_history=True
        )
        results_file = output_dir / "results.json"
        save_simulation(sim, results_file)
        typer.echo(f"  ✓ Algorithm completed in {trust_scores.iteration_count} iterations")
        typer.echo(f"    - Converged: {trust_scores.converged}")

        # Step 4: Generate visualizations
        typer.echo("\n[4/5] Generating visualizations...")

        # Matrix visualization
        from eigentrust.visualization.matrix_viz import MatrixVisualizer

        matrix_viz = MatrixVisualizer()
        matrix_file = output_dir / "trust_matrix.png"
        matrix_viz.visualize(sim, matrix_file)
        typer.echo(f"  ✓ Trust matrix: {matrix_file}")

        # Graph visualization
        from eigentrust.visualization.graph_viz import GraphVisualizer

        graph_viz = GraphVisualizer()
        graph_file = output_dir / "trust_graph.png"
        graph_viz.visualize(sim, graph_file)
        typer.echo(f"  ✓ Trust graph: {graph_file}")

        # Convergence visualization
        from eigentrust.visualization.formatters import ConvergencePlotter

        conv_plotter = ConvergencePlotter()
        conv_file = output_dir / "convergence.png"
        conv_plotter.visualize(sim, conv_file)
        typer.echo(f"  ✓ Convergence plot: {conv_file}")

        # Step 5: Summary
        typer.echo("\n[5/5] Summary")
        typer.echo(f"  Peers: {len(sim.peers)}")
        typer.echo(f"  Interactions: {len(sim.interactions)}")
        typer.echo(f"  Iterations: {trust_scores.iteration_count}")
        typer.echo(f"  Converged: {trust_scores.converged}")

        # Show top trust scores
        typer.echo("\n  Top 5 Trust Scores:")
        sorted_scores = sorted(trust_scores.scores.items(), key=lambda x: x[1], reverse=True)
        for i, (peer_id, score) in enumerate(sorted_scores[:5], 1):
            peer = next(p for p in sim.peers if p.peer_id == peer_id)
            typer.echo(
                f"    {i}. {peer.display_name}: {score:.4f} "
                f"[comp={peer.competence:.2f}, mal={peer.maliciousness:.2f}]"
            )

        typer.echo(f"\n✓ Complete! All files saved to: {output_dir}")
        typer.echo("=" * 60)

    except typer.Exit:
        # Re-raise typer exits without modification
        raise
    except Exception as e:
        typer.echo(f"\nError: {e}", err=True)
        raise typer.Exit(1)


@app.callback()
def version_callback(
    version: Annotated[
        bool | None,
        typer.Option("--version", help="Show version"),
    ] = None,
) -> None:
    """Show version callback."""
    if version:
        typer.echo("eigentrust version 0.1.0")
        raise typer.Exit(0)


if __name__ == "__main__":
    app()
