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
        finally:
            logging.info(f"Command executed: {command}")
            self.console.print("[bold green]Command executed successfully.[/bold green]")

    def _create_gang_status_table(self) -> Table:
        """Creates a table for displaying gang member status."""
        table = Table(show_header=True, header_style="bold magenta")
        columns = ["Name", "Role", "M", "WS", "BS", "S", "T", "W", "I", "A", "Ld", "Cl", "Will", "Int", "XP", "Active"]
        for col in columns:
            table.add_column(col, justify="right" if col not in ["Name", "Role"] else "left")
        return table

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

    # Rest of the file remains unchanged
