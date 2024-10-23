import logging
from rich.console import Console
from user_interface import UserInterface
from game_logic import GameLogic
from database import initialize_database

def run_cli(game_logic: GameLogic, ui: UserInterface, console: Console) -> None:
    """
    Run the interactive CLI mode of the Necromunda simulation.
    
    Args:
        game_logic (GameLogic): The game logic instance
        ui (UserInterface): The user interface instance
        console (Console): The rich console instance
    """
    console.print("[bold green]Welcome to the Necromunda Simulation![/bold green]")
    console.print("Enter 'help' for a list of commands.")
    console.print("Enter 'quit' to exit.")

    try:
        while True:
            command = console.input("\n[bold cyan]Enter command:[/bold cyan] ").strip()
            
            if command.lower() == 'quit':
                break
            
            ui.process_command(command)
            
    except KeyboardInterrupt:
        logging.info("Simulation interrupted by user.")
        console.print("[bold yellow]Simulation interrupted by user.[/bold yellow]")
    except Exception as e:
        logging.error(f"An unexpected error occurred in CLI loop: {str(e)}", exc_info=True)
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {str(e)}")
    finally:
        console.print("[bold red]Exiting Necromunda Simulation. Goodbye![/bold red]")
        logging.info("Necromunda Simulation ended.")

def test_mode(game_logic: GameLogic, ui: UserInterface, console: Console) -> None:
    """
    Run the test mode of the Necromunda simulation.
    
    Args:
        game_logic (GameLogic): The game logic instance
        ui (UserInterface): The user interface instance
        console (Console): The rich console instance
    """
    test_commands = [
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
        "move Crusher 2 3",
        "end_activation",
        "move Venom 1 2",
        "end_activation",
        "advance_phase",
        "show_combat_round",
        "attack Crusher Venom",
        "end_activation",
        "attack Venom Crusher",
        "end_activation",
        "advance_phase",
        "show_combat_round",
        "status",
        "objectives",
        "victory_points",
        "quit"
    ]

    if not test_commands:
        logging.error("No test commands available.")
        console.print("[bold red]Error: No test commands available.[/bold red]")
        return

    try:
        for i, command in enumerate(test_commands, 1):
            console.print(f"\n[bold cyan]Executing command {i}/{len(test_commands)}:[/bold cyan] {command}")
            if command.lower() == 'quit':
                break
            ui.process_command(command)
            logging.info(f"Command executed: {command}")
            console.print("[bold green]Command executed successfully.[/bold green]")
    except Exception as e:
        logging.error(f"An unexpected error occurred in test mode: {str(e)}", exc_info=True)
        console.print(f"[bold red]An unexpected error occurred in test mode:[/bold red] {str(e)}")
