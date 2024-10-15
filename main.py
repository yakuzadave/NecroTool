import logging
from rich.console import Console
from user_interface import UserInterface
from game_logic import GameLogic
from database import initialize_database
import d20
from typing import List
import json

MAX_TEST_COMMANDS = 50

def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_test_commands() -> List[str]:
    """
    Return a list of test commands for the Necromunda simulation.
    
    Returns:
        List[str]: A list of commands to test various aspects of the simulation.
    """
    return [
        "help",
        "status",
        "map",
        "objectives",
        "show_combat_round",
        "attack Crusher Venom",
        "end_activation",
        "attack Venom Crusher",
        "end_activation",
        "advance_phase",
        "show_combat_round",
        "move Smasher 2 3",
        "end_activation",
        "move Shadow 1 2",
        "end_activation",
        "advance_phase",
        "show_combat_round",
        "attack Smasher Shadow",
        "end_activation",
        "attack Shadow Smasher",
        "end_activation",
        "advance_phase",
        "show_combat_round",
        "status",
        "objectives",
        "victory_points",
        "quit"
    ]

def main() -> None:
    """
    Main function to run the Necromunda Simulation.
    
    This function initializes the game, processes test commands, and handles the main game loop.
    """
    setup_logging()
    console = Console()
    db = initialize_database()
    game_logic = GameLogic(db)
    ui = UserInterface(console, game_logic)

    console.print("[bold green]Welcome to the Necromunda Simulation![/bold green]")
    console.print("Enter 'help' for a list of commands.")

    # Initialize the first combat round
    game_logic.create_new_combat_round()

    test_commands = get_test_commands()

    if not test_commands:
        logging.error("No test commands available.")
        console.print("[bold red]Error: No test commands available.[/bold red]")
        return

    try:
        for i, command in enumerate(test_commands[:MAX_TEST_COMMANDS], 1):
            console.print(f"\n[bold cyan]Executing command {i}/{len(test_commands)}:[/bold cyan] {command}")
            if command.lower() == 'quit':
                break
            else:
                ui.process_command(command)
            logging.info(f"Command executed: {command}")
            console.print("[bold green]Command executed successfully.[/bold green]")
    except KeyboardInterrupt:
        logging.info("Simulation interrupted by user.")
        console.print("[bold yellow]Simulation interrupted by user.[/bold yellow]")
    except Exception as e:
        logging.error(f"An unexpected error occurred in main loop: {str(e)}", exc_info=True)
        console.print(f"[bold red]An unexpected error occurred in main loop:[/bold red] {str(e)}")
    finally:
        console.print("[bold red]Exiting Necromunda Simulation. Goodbye![/bold red]")
        logging.info("Necromunda Simulation ended.")

if __name__ == "__main__":
    main()
