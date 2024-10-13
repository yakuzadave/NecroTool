from rich.console import Console
from rich.table import Table
from game_logic import GameLogic

class UserInterface:
    def __init__(self, console: Console, game_logic: GameLogic):
        self.console = console
        self.game_logic = game_logic

    def process_command(self, command: str):
        parts = command.lower().split()
        if not parts:
            return

        if parts[0] == 'help':
            self.show_help()
        elif parts[0] == 'status':
            self.show_status()
        elif parts[0] == 'move':
            if len(parts) == 4:
                result = self.game_logic.move_fighter(parts[1], int(parts[2]), int(parts[3]))
                self.console.print(f"Move {'successful' if result else 'failed'}")
            else:
                self.console.print("Invalid move command. Use: move <fighter_name> <x> <y>")
        elif parts[0] == 'attack':
            if len(parts) == 3:
                result = self.game_logic.attack(parts[1], parts[2])
                self.console.print(result)
            else:
                self.console.print("Invalid attack command. Use: attack <attacker_name> <target_name>")
        elif parts[0] == 'end_turn':
            self.game_logic.next_turn()
            self.console.print(f"Turn ended. Active gang: {self.game_logic.get_active_gang().name}")
        elif parts[0] == 'save':
            self.game_logic.save_game_state()
            self.console.print("Game state saved.")
        elif parts[0] == 'map':
            self.show_battlefield()
        else:
            self.console.print("Unknown command. Type 'help' for a list of commands.")

    def show_help(self):
        self.console.print("Available commands:")
        self.console.print("  help - Show this help message")
        self.console.print("  status - Show current game status")
        self.console.print("  move <fighter_name> <x> <y> - Move a fighter")
        self.console.print("  attack <attacker_name> <target_name> - Attack a target")
        self.console.print("  end_turn - End the current turn")
        self.console.print("  save - Save the current game state")
        self.console.print("  map - Show the battlefield map")
        self.console.print("  quit - Exit the game")

    def show_status(self):
        for gang in self.game_logic.game_state.gangs:
            table = Table(title=f"{gang.name} Gang")
            table.add_column("Name", style="cyan")
            table.add_column("Wounds", style="magenta")
            table.add_column("Weapon", style="green")

            for fighter in gang.fighters:
                table.add_row(fighter.name, str(fighter.wounds), fighter.weapons[0].name)

            self.console.print(table)

        self.console.print(f"Current Turn: {self.game_logic.game_state.current_turn}")
        self.console.print(f"Active Gang: {self.game_logic.get_active_gang().name}")

    def show_battlefield(self):
        battlefield_state = self.game_logic.get_battlefield_state()
        self.console.print("[bold]Battlefield Map:[/bold]")
        self.console.print(battlefield_state)
        self.console.print("Legend: . = Open, # = Cover, 1-2 = Elevation")
