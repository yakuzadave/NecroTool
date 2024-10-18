import logging
from rich.console import Console
from rich.table import Table
from game_logic import GameLogic
import json
from typing import Dict, Any, List, Optional

class UserInterface:
    def __init__(self, console: Console, game_logic: GameLogic):
        self.console = console
        self.game_logic = game_logic
        logging.info("UserInterface initialized")

    def process_command(self, command: str) -> None:
        """Processes user commands and executes corresponding methods."""
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
                'show_equipment': self._handle_show_equipment,
                'show_scenario': self.show_scenario,
                'check_objectives': self.check_scenario_objectives,
                'show_combat_round': self._handle_show_combat_round,
                'advance_phase': self._handle_advance_phase,
                'show_fighter': self._handle_show_fighter,
                'use_skill': self._handle_use_skill
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
        """Displays a list of available commands to the user."""
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
            ("show_scenario", "Display information about the current scenario"),
            ("check_objectives", "Check and update scenario objectives"),
            ("show_combat_round", "Display information about the current combat round"),
            ("advance_phase", "Advance to the next combat phase"),
            ("show_fighter <fighter_name>", "Display detailed information about a specific fighter"),
            ("use_skill <fighter_name> <skill_name>", "Use a skill or special ability of a fighter"),
            ("quit", "Exit the game")
        ]
        for command, description in help_text:
            self.console.print(f"  {command} - {description}")

    def _add_member_to_status_table(self, table: Table, member: Any, is_active: bool) -> None:
        """Adds a gang member's information to the status table."""
        table.add_row(
            member.name, member.role,
            str(member.movement), str(member.weapon_skill), str(member.ballistic_skill),
            str(member.strength), str(member.toughness), str(member.wounds),
            str(member.initiative), str(member.attacks), str(member.leadership),
            str(member.cool), str(member.will), str(member.intelligence),
            str(member.xp), "Yes" if is_active else "No"
        )

    # ... [rest of the methods remain unchanged]
