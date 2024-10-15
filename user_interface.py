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
                'advance_phase': self._handle_advance_phase
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
            ("quit", "Exit the game")
        ]
        for command, description in help_text:
            self.console.print(f"  {command} - {description}")

    def show_status(self, _: Optional[List[str]] = None) -> None:
        for gang in self.game_logic.game_state.gangs:
            self._display_gang_status(gang)

        self.console.print(f"\nCurrent Turn: {self.game_logic.game_state.current_turn}")
        self.console.print(f"Active Gang: {self.game_logic.get_active_gang().name}")
        self.console.print(f"Active Fighter: {self.game_logic.get_active_fighter().name}")
        
        self._display_combat_round_info()

    def _display_gang_status(self, gang: Any) -> None:
        self.console.print(f"\n[bold]{gang.name} Gang[/bold] (Credits: {gang.credits}, Victory Points: {gang.victory_points})")
        table = self._create_gang_status_table()

        for member in gang.members:
            is_active = (gang == self.game_logic.get_active_gang() and
                         member == self.game_logic.get_active_fighter())
            self._add_member_to_status_table(table, member, is_active)

        self.console.print(table)
        self._display_member_details(gang)

    def _create_gang_status_table(self) -> Table:
        table = Table(show_header=True, header_style="bold magenta")
        columns = ["Name", "Role", "M", "WS", "BS", "S", "T", "W", "I", "A", "Ld", "Cl", "Wil", "Int", "XP", "Active"]
        for col in columns:
            table.add_column(col, justify="right" if col not in ["Name", "Role"] else "left")
        return table

    def _add_member_to_status_table(self, table: Table, member: Any, is_active: bool) -> None:
        table.add_row(
            member.name, member.role,
            str(member.movement), str(member.weapon_skill), str(member.ballistic_skill),
            str(member.strength), str(member.toughness), str(member.wounds),
            str(member.initiative), str(member.attacks), str(member.leadership),
            str(member.cool), str(member.willpower), str(member.intelligence),
            str(member.xp), "Yes" if is_active else "No"
        )

    def _display_member_details(self, gang: Any) -> None:
        for member in gang.members:
            self.console.print(f"\n[bold]{member.name}[/bold]")
            self._display_weapons(member)
            self._display_equipment(member)
            self._display_consumables(member)
            self._display_skills_and_rules(member)

    def _display_weapons(self, member: Any) -> None:
        self.console.print("  Weapons:")
        for weapon in member.weapons:
            self.console.print(f"    - {weapon.name} (Type: {weapon.weapon_type})")
            for profile in weapon.profiles:
                self.console.print(f"      Range: {profile.range}, S: {profile.strength}, AP: {profile.armor_penetration}, D: {profile.damage}, Ammo: {profile.ammo_roll}")
            if weapon.traits:
                self.console.print(f"      Traits: {', '.join([trait.name for trait in weapon.traits])}")

    def _display_equipment(self, member: Any) -> None:
        if member.equipment:
            self.console.print("  Equipment:")
            for item in member.equipment:
                self.console.print(f"    - {item.name}: {item.description}")
                if item.special_rules:
                    self.console.print(f"      Special Rules: {', '.join(item.special_rules)}")
                if item.modifiers:
                    self.console.print(f"      Modifiers: {', '.join(item.modifiers)}")

    def _display_consumables(self, member: Any) -> None:
        if member.consumables:
            self.console.print("  Consumables:")
            for item in member.consumables:
                self.console.print(f"    - {item.name} (Uses: {item.uses}): {item.effect}")

    def _display_skills_and_rules(self, member: Any) -> None:
        if member.skills:
            self.console.print(f"  Skills: {', '.join(member.skills)}")
        if member.special_rules:
            self.console.print("  Special Rules:")
            for rule in member.special_rules:
                self.console.print(f"    - {rule.name}: {rule.description}")
        if member.injuries:
            self.console.print(f"  Injuries: {', '.join(member.injuries)}")

    def _handle_move(self, args: list) -> None:
        if len(args) != 3:
            raise ValueError("Invalid move command. Use: move <fighter_name> <x> <y>")
        result = self.game_logic.move_fighter(args[0], int(args[1]), int(args[2]))
        self.console.print(f"Move {'successful' if result else 'failed'}")

    def _handle_attack(self, args: list) -> None:
        if len(args) != 2:
            raise ValueError("Invalid attack command. Use: attack <attacker_name> <target_name>")
        result = self.game_logic.attack(args[0], args[1])
        self.console.print(result)

    def _handle_end_activation(self, _: list) -> None:
        result = self.game_logic.end_fighter_activation()
        self.console.print(result)

    def _handle_save(self, _: list) -> None:
        self.game_logic.save_game_state()
        self.console.print("Game state saved.")

    def show_battlefield(self, _: Optional[List[str]] = None) -> None:
        battlefield_state = self.game_logic.get_battlefield_state()
        self.console.print("[bold]Battlefield Map:[/bold]")
        self.console.print(battlefield_state)
        self.console.print("Legend: . = Open, # = Cover, 1-2 = Elevation")

    def show_victory_points(self, _: Optional[List[str]] = None) -> None:
        self.console.print("[bold]Current Victory Points:[/bold]")
        results = self.game_logic.calculate_victory_points()
        for result in results:
            self.console.print(f"{result['gang']}: {result['victory_points']} points")

        if self.game_logic.is_game_over():
            winner = self.game_logic.get_winner()
            self.console.print(f"\n[bold green]{winner}[/bold green]")

    def _handle_create_gang_member(self, args: list) -> None:
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
        if len(args) != 2:
            raise ValueError("Invalid use_consumable command. Use: use_consumable <fighter_name> <consumable_name>")
        fighter_name, consumable_name = args
        result = self.game_logic.use_consumable(fighter_name, consumable_name)
        self.console.print(result)

    def _handle_show_equipment(self, args: list) -> None:
        if len(args) != 1:
            raise ValueError("Invalid show_equipment command. Use: show_equipment <fighter_name>")
        fighter_name = args[0]
        fighter = self.game_logic._get_fighter_by_name(fighter_name)
        if fighter:
            self.console.print(f"[bold]{fighter.name}'s Equipment:[/bold]")
            self._display_equipment(fighter)
        else:
            self.console.print(f"Fighter {fighter_name} not found.")

    def show_scenario(self, _: Optional[List[str]] = None) -> None:
        scenario = self.game_logic.get_scenario()
        if scenario:
            self.console.print(f"[bold]Current Scenario: {scenario.name}[/bold]")
            self.console.print(f"Description: {scenario.description}")
            self.console.print("\n[bold]Objectives:[/bold]")
            for objective in scenario.objectives:
                status = "[green]Completed[/green]" if objective.completed else "[yellow]In Progress[/yellow]"
                self.console.print(f"- {objective.name} ({objective.points} points): {objective.description} - {status}")
            self.console.print("\n[bold]Deployment Zones:[/bold]")
            for zone in scenario.deployment_zones:
                self.console.print(f"- {zone.name}: {zone.description}")
            if scenario.special_rules:
                self.console.print("\n[bold]Special Rules:[/bold]")
                for rule in scenario.special_rules:
                    self.console.print(f"- {rule.name}: {rule.effect}")
            self.console.print(f"\nDuration: {scenario.duration}")
            self.console.print(f"Rewards: {scenario.rewards}")
        else:
            self.console.print("[bold red]No scenario is currently set.[/bold red]")

    def check_scenario_objectives(self, _: Optional[List[str]] = None) -> None:
        self.game_logic.check_scenario_objectives()
        self.show_mission_objectives()

    def show_mission_objectives(self, _: Optional[List[str]] = None) -> None:
        scenario = self.game_logic.get_scenario()
        if scenario:
            self.console.print("[bold]Mission Objectives:[/bold]")
            for objective in scenario.objectives:
                status = "[green]Completed[/green]" if objective.completed else "[yellow]In Progress[/yellow]"
                self.console.print(f"- {objective.name} ({objective.points} points): {objective.description} - {status}")
        else:
            self.console.print("[bold red]No scenario is currently set.[/bold red]")

    def _display_combat_round_info(self) -> None:
        current_round = self.game_logic.get_current_combat_round()
        if current_round:
            self.console.print(f"\n[bold]Current Combat Round: {current_round.round_number}[/bold]")
            current_phase = self.game_logic.get_current_combat_phase()
            if current_phase:
                self.console.print(f"Current Phase: {current_phase.name}")
                self.console.print(f"Description: {current_phase.description}")
                if current_phase.actions:
                    self.console.print(f"Available Actions: {', '.join(current_phase.actions)}")
            if current_round.special_rules:
                self.console.print(f"Special Rules: {', '.join(current_round.special_rules)}")
            if current_round.summary:
                self.console.print(f"Round Summary: {current_round.summary}")

    def _handle_show_combat_round(self, _: list) -> None:
        self._display_combat_round_info()

    def _handle_advance_phase(self, _: list) -> None:
        self.game_logic.advance_combat_phase()
        self.console.print("Advanced to the next combat phase.")
        self._display_combat_round_info()