import logging
from rich.console import Console
from rich.table import Table
from game_logic import GameLogic
import json
from typing import Dict, Any, List, Optional

class UserInterface:
    """
    Manages the user interface for the Necromunda simulation.
    """

    def __init__(self, console: Console, game_logic: GameLogic):
        """
        Initialize the UserInterface instance.

        Args:
            console (Console): The Rich console for output.
            game_logic (GameLogic): The game logic instance.
        """
        self.console = console
        self.game_logic = game_logic
        logging.info("UserInterface initialized")

    def process_command(self, command: str) -> None:
        """
        Process a user command.

        Args:
            command (str): The command to process.
        """
        self.console.print(f"[bold cyan]Processing command:[/bold cyan] {command}")
        try:
            parts = command.lower().split()
            if not parts:
                raise ValueError("Empty command")

            command_handlers = {
                'help': self.show_help,
                'status': self.show_status,
                'move': self._handle_move,
                'attack': self._handle_attack,
                'end_activation': self._handle_end_activation,
                'save': self._handle_save,
                'map': self.show_battlefield,
                'objectives': self.show_mission_objectives,
                'victory_points': self.show_victory_points,
                'create_gang_member': self._handle_create_gang_member,
                'use_consumable': self._handle_use_consumable,
                'show_equipment': self._handle_show_equipment
            }

            handler = command_handlers.get(parts[0])
            if handler:
                handler(parts[1:] if len(parts) > 1 else [])
            else:
                raise ValueError(f"Unknown command: {parts[0]}")

        except ValueError as e:
            self.console.print(f"[bold red]Error:[/bold red] {str(e)}")
            logging.warning(f"Command processing error: {str(e)}")
        except Exception as e:
            self.console.print(f"[bold red]An unexpected error occurred:[/bold red] {str(e)}")
            logging.error(f"Unexpected error in process_command: {str(e)}", exc_info=True)

    def show_help(self, _: Optional[List[str]] = None) -> None:
        """Display help information."""
        self.console.print("[bold]Available commands:[/bold]")
        help_text = [
            ("help", "Show this help message"),
            ("status", "Show detailed status of all gang members"),
            ("move <fighter_name> <x> <y>", "Move the active fighter"),
            ("attack <attacker_name> <target_name>", "Attack with the active fighter"),
            ("end_activation", "End the current fighter's activation"),
            ("save", "Save the current game state"),
            ("map", "Show the battlefield map"),
            ("objectives", "Show current mission objectives"),
            ("victory_points", "Show current victory points"),
            ("create_gang_member <gang_name> <member_data_json>", "Create a custom gang member"),
            ("use_consumable <fighter_name> <consumable_name>", "Use a consumable item"),
            ("show_equipment <fighter_name>", "Show equipment details for a fighter"),
            ("quit", "Exit the game")
        ]
        for command, description in help_text:
            self.console.print(f"  {command} - {description}")

    def show_status(self, _: Optional[List[str]] = None) -> None:
        """Display the status of all gang members."""
        for gang in self.game_logic.game_state.gangs:
            self._display_gang_status(gang)

        self.console.print(f"\nCurrent Turn: {self.game_logic.game_state.current_turn}")
        self.console.print(f"Active Gang: {self.game_logic.get_active_gang().name}")
        self.console.print(f"Active Fighter: {self.game_logic.get_active_fighter().name}")

    def _display_gang_status(self, gang: Any) -> None:
        """
        Display the status of a single gang.

        Args:
            gang (Any): The gang to display status for.
        """
        self.console.print(f"\n[bold]{gang.name} Gang[/bold] (Credits: {gang.credits}, Victory Points: {gang.victory_points})")
        table = self._create_gang_status_table()

        for member in gang.members:
            is_active = (gang == self.game_logic.get_active_gang() and
                         member == self.game_logic.get_active_fighter())
            self._add_member_to_status_table(table, member, is_active)

        self.console.print(table)
        self._display_member_details(gang)

    def _create_gang_status_table(self) -> Table:
        """Create and return a Rich Table for gang status."""
        table = Table(show_header=True, header_style="bold magenta")
        columns = ["Name", "Role", "M", "WS", "BS", "S", "T", "W", "I", "A", "Ld", "Cl", "Wil", "Int", "XP", "Active"]
        for col in columns:
            table.add_column(col, justify="right" if col not in ["Name", "Role"] else "left")
        return table

    def _add_member_to_status_table(self, table: Table, member: Any, is_active: bool) -> None:
        """
        Add a gang member to the status table.

        Args:
            table (Table): The Rich Table to add the member to.
            member (Any): The gang member to add.
            is_active (bool): Whether the member is currently active.
        """
        table.add_row(
            member.name, member.role,
            str(member.movement), str(member.weapon_skill), str(member.ballistic_skill),
            str(member.strength), str(member.toughness), str(member.wounds),
            str(member.initiative), str(member.attacks), str(member.leadership),
            str(member.cool), str(member.willpower), str(member.intelligence),
            str(member.xp), "Yes" if is_active else "No"
        )

    def _display_member_details(self, gang: Any) -> None:
        """
        Display detailed information for each gang member.

        Args:
            gang (Any): The gang whose members to display.
        """
        for member in gang.members:
            self.console.print(f"\n[bold]{member.name}[/bold]")
            self._display_weapons(member)
            self._display_equipment(member)
            self._display_consumables(member)
            self._display_skills_and_rules(member)

    def _display_weapons(self, member: Any) -> None:
        """Display weapons for a gang member."""
        self.console.print("  Weapons:")
        for weapon in member.weapons:
            self.console.print(f"    - {weapon.name} (Type: {weapon.weapon_type})")
            for profile in weapon.profiles:
                self.console.print(f"      Range: {profile.range}, S: {profile.strength}, AP: {profile.armor_penetration}, D: {profile.damage}, Ammo: {profile.ammo_roll}")
            if weapon.traits:
                self.console.print(f"      Traits: {', '.join([trait.name for trait in weapon.traits])}")

    def _display_equipment(self, member: Any) -> None:
        """Display equipment for a gang member."""
        if member.equipment:
            self.console.print("  Equipment:")
            for item in member.equipment:
                self.console.print(f"    - {item.name}: {item.description}")
                if item.special_rules:
                    self.console.print(f"      Special Rules: {', '.join(item.special_rules)}")
                if item.modifiers:
                    self.console.print(f"      Modifiers: {', '.join(item.modifiers)}")

    def _display_consumables(self, member: Any) -> None:
        """Display consumables for a gang member."""
        if member.consumables:
            self.console.print("  Consumables:")
            for item in member.consumables:
                self.console.print(f"    - {item.name} (Uses: {item.uses}): {item.effect}")

    def _display_skills_and_rules(self, member: Any) -> None:
        """Display skills and special rules for a gang member."""
        if member.skills:
            self.console.print(f"  Skills: {', '.join(member.skills)}")
        if member.special_rules:
            self.console.print("  Special Rules:")
            for rule in member.special_rules:
                self.console.print(f"    - {rule.name}: {rule.description}")
        if member.injuries:
            self.console.print(f"  Injuries: {', '.join(member.injuries)}")

    def _handle_move(self, args: list) -> None:
        """Handle the move command."""
        if len(args) != 3:
            raise ValueError("Invalid move command. Use: move <fighter_name> <x> <y>")
        result = self.game_logic.move_fighter(args[0], int(args[1]), int(args[2]))
        self.console.print(f"Move {'successful' if result else 'failed'}")

    def _handle_attack(self, args: list) -> None:
        """Handle the attack command."""
        if len(args) != 2:
            raise ValueError("Invalid attack command. Use: attack <attacker_name> <target_name>")
        result = self.game_logic.attack(args[0], args[1])
        self.console.print(result)

    def _handle_end_activation(self, _: list) -> None:
        """Handle the end_activation command."""
        result = self.game_logic.end_fighter_activation()
        self.console.print(result)

    def _handle_save(self, _: list) -> None:
        """Handle the save command."""
        self.game_logic.save_game_state()
        self.console.print("Game state saved.")

    def show_battlefield(self, _: Optional[List[str]] = None) -> None:
        """Display the battlefield map."""
        battlefield_state = self.game_logic.get_battlefield_state()
        self.console.print("[bold]Battlefield Map:[/bold]")
        self.console.print(battlefield_state)
        self.console.print("Legend: . = Open, # = Cover, 1-2 = Elevation")

    def show_mission_objectives(self, _: Optional[List[str]] = None) -> None:
        """Display the current mission objectives."""
        self.console.print("[bold]Mission Objectives:[/bold]")
        for objective in self.game_logic.game_state.mission_objectives:
            status = "[green]Completed[/green]" if objective.completed else "[yellow]In Progress[/yellow]"
            self.console.print(f"- {objective.name} ({objective.points} points): {objective.description} - {status}")

    def show_victory_points(self, _: Optional[List[str]] = None) -> None:
        """Display the current victory points for each gang."""
        self.console.print("[bold]Current Victory Points:[/bold]")
        results = self.game_logic.calculate_victory_points()
        for result in results:
            self.console.print(f"{result['gang']}: {result['victory_points']} points")

        if self.game_logic.is_game_over():
            winner = self.game_logic.get_winner()
            self.console.print(f"\n[bold green]{winner}[/bold green]")

    def _handle_create_gang_member(self, args: list) -> None:
        """Handle the create_gang_member command."""
        if len(args) < 2:
            raise ValueError("Invalid create_gang_member command. Use: create_gang_member <gang_name> <member_data_json>")
        gang_name = args[0]
        member_data_json = " ".join(args[1:])
        try:
            member_data = json.loads(member_data_json)
            result = self.game_logic.create_custom_gang_member(gang_name, member_data)
            self.console.print(result)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for member data")

    def _handle_use_consumable(self, args: list) -> None:
        """Handle the use_consumable command."""
        if len(args) != 2:
            raise ValueError("Invalid use_consumable command. Use: use_consumable <fighter_name> <consumable_name>")
        fighter_name, consumable_name = args
        result = self.game_logic.use_consumable(fighter_name, consumable_name)
        self.console.print(result)

    def _handle_show_equipment(self, args: list) -> None:
        """Handle the show_equipment command."""
        if len(args) != 1:
            raise ValueError("Invalid show_equipment command. Use: show_equipment <fighter_name>")
        fighter_name = args[0]
        fighter = self.game_logic._get_fighter_by_name(fighter_name)
        if fighter:
            self.console.print(f"[bold]{fighter.name}'s Equipment:[/bold]")
            self._display_equipment(fighter)
        else:
            self.console.print(f"Fighter {fighter_name} not found.")