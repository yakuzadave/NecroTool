import logging
import argparse
from rich.console import Console
from user_interface import UserInterface
from game_logic import GameLogic
from database import initialize_database
from cli import run_cli, test_mode


def setup_logging() -> None:
    """Set up logging configuration with Rich for improved output."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("game_log.log"),
            logging.StreamHandler()
        ]
    )
    logging.info("Logging setup complete.")


def create_sample_scenario():
    """Create and return a sample scenario for the game."""
    from models import (
        Scenario,
        ScenarioObjective,
        ScenarioDeploymentZone,
        ScenarioSpecialRule
    )
    return Scenario(
        name="Turf War",
        description="Two gangs fight for control of a valuable territory.",
        objectives=[
            ScenarioObjective(
                name="Control Central Zone",
                description="Have more fighters than the enemy in the central 4x4 area at the end of the game.",
                points=3
            ),
            ScenarioObjective(
                name="Eliminate Enemy Leader",
                description="Take the enemy gang's leader out of action.",
                points=2
            )
        ],
        deployment_zones=[
            ScenarioDeploymentZone(
                name="North Zone",
                description="Deploy within 6\" of the north table edge."
            ),
            ScenarioDeploymentZone(
                name="South Zone",
                description="Deploy within 6\" of the south table edge."
            )
        ],
        special_rules=[
            ScenarioSpecialRule(
                name="Hazardous Terrain",
                effect="Fighters moving through the central zone must pass an Initiative check or become Pinned."
            )
        ],
        max_gangs=2,
        duration="6 turns",
        rewards="The winning gang gains control of the territory, earning 100 credits per post-battle sequence."
    )


def initialize_game(game_logic: GameLogic, console: Console) -> None:
    """
    Initialize the game with default settings and a sample scenario.

    Args:
        game_logic (GameLogic): The main game logic object.
        console (Console): The Rich console object for output.
    """
    console.print("[bold green]Welcome to Necromunda Simulation![/bold green]")
    scenario = create_sample_scenario()
    game_logic.game_state.scenario = scenario
    console.print(f"[bold blue]Scenario Loaded:[/bold blue] {scenario.name}")
    console.print(f"[dim]{scenario.description}[/dim]")
    logging.info("Sample scenario initialized.")


def main() -> None:
    """
    Main function to run the Necromunda Simulation.

    Supports both interactive CLI mode and test mode through command-line arguments.
    """
    parser = argparse.ArgumentParser(description='Necromunda Text-Based Simulation')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    args = parser.parse_args()

    setup_logging()
    console = Console()
    db = initialize_database()
    game_logic = GameLogic(db)
    initialize_game(game_logic, console)
    ui = UserInterface(console, game_logic)

    if args.test:
        console.print("[bold yellow]Running in Test Mode...[/bold yellow]")
        test_mode(game_logic, ui, console)
    else:
        console.print("[bold cyan]Starting Interactive Mode...[/bold cyan]")
        run_cli(game_logic, ui, console)


if __name__ == "__main__":
    main()
