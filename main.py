from rich.console import Console
from user_interface import UserInterface
from game_logic import GameLogic
from database import initialize_database

def main():
    console = Console()
    db = initialize_database()
    game_logic = GameLogic(db)
    ui = UserInterface(console, game_logic)

    console.print("[bold green]Welcome to the Necromunda Simulation![/bold green]")
    console.print("Enter 'help' for a list of commands.")

    while True:
        command = console.input("[bold cyan]Enter command:[/bold cyan] ")
        if command.lower() == 'quit':
            break
        ui.process_command(command)

    console.print("[bold red]Exiting Necromunda Simulation. Goodbye![/bold red]")

if __name__ == "__main__":
    main()
