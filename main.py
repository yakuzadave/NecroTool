from rich.console import Console
from user_interface import UserInterface
from game_logic import GameLogic
from database import initialize_database
import d20

def main():
    console = Console()
    db = initialize_database()
    game_logic = GameLogic(db)
    ui = UserInterface(console, game_logic)

    console.print("[bold green]Welcome to the Necromunda Simulation![/bold green]")
    console.print("Enter 'help' for a list of commands.")

    # Test commands
    test_commands = [
        "help",
        "status",
        "map",
        "objectives",
        "attack Crusher Venom",
        "end_activation",
        "attack Venom Crusher",
        "end_activation",
        "attack Smasher Shadow",
        "end_activation",
        "attack Shadow Smasher",
        "end_activation",
        "attack Crusher Venom",
        "end_activation",
        "attack Venom Crusher",
        "end_activation",
        "attack Smasher Shadow",
        "end_activation",
        "attack Shadow Smasher",
        "end_activation",
        "attack Crusher Venom",
        "end_activation",
        "attack Venom Crusher",
        "end_activation",
        "attack Smasher Shadow",
        "end_activation",
        "attack Shadow Smasher",
        "end_activation",
        "status",
        "objectives",
        "victory_points",
        "quit"
    ]

    try:
        for command in test_commands:
            console.print(f"\n[bold cyan]Executing command:[/bold cyan] {command}")
            if command.lower() == 'quit':
                break
            else:
                ui.process_command(command)
            console.print("[bold green]Command executed successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred in main loop:[/bold red] {str(e)}")
    finally:
        console.print("[bold red]Exiting Necromunda Simulation. Goodbye![/bold red]")

if __name__ == "__main__":
    main()
