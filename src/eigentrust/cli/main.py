"""CLI entry point for EigenTrust demonstration.

Implements command-line interface using Typer framework.
"""

import json
import typer
from pathlib import Path
from typing_extensions import Annotated
from eigentrust.simulation.network import create_network
from eigentrust.utils.io import save_simulation, load_simulation

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
        Optional[int],
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
            good_peers = sum(
                1 for p in sim.peers
                if p.competence <= 0.2 and p.maliciousness <= 0.2
            )
            bad_peers = sum(
                1 for p in sim.peers
                if p.competence >= 0.8 and p.maliciousness >= 0.8
            )
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
            typer.echo(f"Simulating {interactions} peer-to-peer interactions...")

        new_interactions = sim.simulate_interactions(interactions)

        # Save updated simulation
        save_simulation(sim, output)

        # Output summary
        typer.echo(f"Simulated {len(new_interactions)} interactions")
        typer.echo(f"Total interactions: {len(sim.interactions)}")

        # Count outcomes
        from eigentrust.domain.interaction import InteractionOutcome
        success_count = sum(
            1 for i in new_interactions
            if i.outcome == InteractionOutcome.SUCCESS
        )
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
            typer.echo(
                "Warning: No interactions found. Run 'simulate' command first.",
                err=True
            )

        # Run EigenTrust algorithm
        if verbose:
            typer.echo(f"Running EigenTrust algorithm (max_iterations={max_iterations}, epsilon={epsilon})...")

        trust_scores = sim.run_algorithm(
            max_iterations=max_iterations,
            epsilon=epsilon,
            track_history=False
        )

        # Save results
        save_simulation(sim, output)

        # Output results
        typer.echo(f"Algorithm completed in {trust_scores.iteration_count} iterations")
        typer.echo(f"Converged: {trust_scores.converged}")
        typer.echo(f"Final delta: {trust_scores.final_delta:.6f}")

        # Show top trust scores
        typer.echo("\nTop Trust Scores:")
        sorted_scores = sorted(
            trust_scores.scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
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


@app.callback()
def version_callback(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", help="Show version"),
    ] = None,
) -> None:
    """Show version callback."""
    if version:
        typer.echo("eigentrust version 0.1.0")
        raise typer.Exit(0)


# Import for type hints
from typing import Optional


if __name__ == "__main__":
    app()
