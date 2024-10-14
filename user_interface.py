from rich.console import Console
from rich.table import Table
from game_logic import GameLogic
import json

class UserInterface:
    def __init__(self, console: Console, game_logic: GameLogic):
        self.console = console
        self.game_logic = game_logic

    def process_command(self, command: str):
        self.console.print(f"[bold cyan]Processing command:[/bold cyan] {command}")
        try:
            parts = command.lower().split()
            if not parts:
                raise ValueError("Empty command")

            if parts[0] == 'help':
                self.show_help()
            elif parts[0] == 'status':
                self.show_status()
            elif parts[0] == 'move':
                if len(parts) != 4:
                    raise ValueError("Invalid move command. Use: move <fighter_name> <x> <y>")
                result = self.game_logic.move_fighter(parts[1], int(parts[2]), int(parts[3]))
                self.console.print(f"Move {'successful' if result else 'failed'}")
            elif parts[0] == 'attack':
                if len(parts) != 3:
                    raise ValueError("Invalid attack command. Use: attack <attacker_name> <target_name>")
                result = self.game_logic.attack(parts[1], parts[2])
                self.console.print(result)
            elif parts[0] == 'end_activation':
                result = self.game_logic.end_fighter_activation()
                self.console.print(result)
            elif parts[0] == 'save':
                self.game_logic.save_game_state()
                self.console.print("Game state saved.")
            elif parts[0] == 'map':
                self.show_battlefield()
            elif parts[0] == 'objectives':
                self.show_mission_objectives()
            elif parts[0] == 'victory_points':
                self.show_victory_points()
            elif parts[0] == 'create_gang_member':
                if len(parts) < 3:
                    raise ValueError("Invalid create_gang_member command. Use: create_gang_member <gang_name> <member_data_json>")
                gang_name = parts[1]
                member_data_json = " ".join(parts[2:])
                try:
                    member_data = json.loads(member_data_json)
                    result = self.game_logic.create_custom_gang_member(gang_name, member_data)
                    self.console.print(result)
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON format for member data")
            else:
                raise ValueError(f"Unknown command: {parts[0]}")
        except ValueError as e:
            self.console.print(f"[bold red]Error:[/bold red] {str(e)}")
        except Exception as e:
            self.console.print(f"[bold red]An unexpected error occurred:[/bold red] {str(e)}")

    def show_help(self):
        self.console.print("[bold]Available commands:[/bold]")
        self.console.print("  help - Show this help message")
        self.console.print("  status - Show detailed status of all gang members")
        self.console.print("  move <fighter_name> <x> <y> - Move the active fighter")
        self.console.print("  attack <attacker_name> <target_name> - Attack with the active fighter")
        self.console.print("  end_activation - End the current fighter's activation")
        self.console.print("  save - Save the current game state")
        self.console.print("  map - Show the battlefield map")
        self.console.print("  objectives - Show current mission objectives")
        self.console.print("  victory_points - Show current victory points")
        self.console.print("  create_gang_member <gang_name> <member_data_json> - Create a custom gang member")
        self.console.print("  quit - Exit the game")

    def show_status(self):
        for gang in self.game_logic.game_state.gangs:
            self.console.print(f"\n[bold]{gang.name} Gang[/bold] (Credits: {gang.credits}, Victory Points: {gang.victory_points})")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Name", style="cyan")
            table.add_column("Role", style="green")
            table.add_column("M", justify="right")
            table.add_column("WS", justify="right")
            table.add_column("BS", justify="right")
            table.add_column("S", justify="right")
            table.add_column("T", justify="right")
            table.add_column("W", justify="right")
            table.add_column("I", justify="right")
            table.add_column("A", justify="right")
            table.add_column("Ld", justify="right")
            table.add_column("Cl", justify="right")
            table.add_column("Wil", justify="right")
            table.add_column("Int", justify="right")
            table.add_column("XP", justify="right")
            table.add_column("Active", justify="right")

            for member in gang.members:
                is_active = (gang == self.game_logic.get_active_gang() and
                             member == self.game_logic.get_active_fighter())
                table.add_row(
                    member.name, member.role,
                    str(member.movement), str(member.weapon_skill), str(member.ballistic_skill),
                    str(member.strength), str(member.toughness), str(member.wounds),
                    str(member.initiative), str(member.attacks), str(member.leadership),
                    str(member.cool), str(member.willpower), str(member.intelligence),
                    str(member.xp), "Yes" if is_active else "No"
                )

            self.console.print(table)

            for member in gang.members:
                self.console.print(f"\n[bold]{member.name}[/bold]")
                self.console.print(f"  Weapons:")
                for weapon in member.weapons:
                    self.console.print(f"    - {weapon.name} (Range: {weapon.range}, S: {weapon.strength}, AP: {weapon.armor_penetration}, D: {weapon.damage}, Ammo: {weapon.ammo})")
                    if weapon.traits:
                        self.console.print(f"      Traits: {', '.join(weapon.traits)}")
                if member.equipment:
                    self.console.print(f"  Equipment:")
                    for item in member.equipment:
                        self.console.print(f"    - {item.name}: {item.description}")
                if member.skills:
                    self.console.print(f"  Skills: {', '.join(member.skills)}")
                if member.special_rules:
                    self.console.print(f"  Special Rules:")
                    for rule in member.special_rules:
                        self.console.print(f"    - {rule.name}: {rule.description}")
                if member.injuries:
                    self.console.print(f"  Injuries: {', '.join(member.injuries)}")

        self.console.print(f"\nCurrent Turn: {self.game_logic.game_state.current_turn}")
        self.console.print(f"Active Gang: {self.game_logic.get_active_gang().name}")
        self.console.print(f"Active Fighter: {self.game_logic.get_active_fighter().name}")

    def show_battlefield(self):
        battlefield_state = self.game_logic.get_battlefield_state()
        self.console.print("[bold]Battlefield Map:[/bold]")
        self.console.print(battlefield_state)
        self.console.print("Legend: . = Open, # = Cover, 1-2 = Elevation")

    def show_mission_objectives(self):
        self.console.print("[bold]Mission Objectives:[/bold]")
        for objective in self.game_logic.game_state.mission_objectives:
            status = "[green]Completed[/green]" if objective.completed else "[yellow]In Progress[/yellow]"
            self.console.print(f"- {objective.name} ({objective.points} points): {objective.description} - {status}")

    def show_victory_points(self):
        self.console.print("[bold]Current Victory Points:[/bold]")
        results = self.game_logic.calculate_victory_points()
        for result in results:
            self.console.print(f"{result['gang']}: {result['victory_points']} points")

        if self.game_logic.is_game_over():
            winner = self.game_logic.get_winner()
            self.console.print(f"\n[bold green]{winner}[/bold green]")