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

    # ... [previous methods remain unchanged]

    def _handle_move(self, args: list) -> None:
        """Handles the move command."""
        if len(args) != 3:
            raise ValueError("Invalid move command. Use: move <fighter_name> <x> <y>")
        result = self.game_logic.move_fighter(args[0], int(args[1]), int(args[2]))
        self.console.print(f"Move {'successful' if result else 'failed'}")

    def show_battlefield(self, _: Optional[List[str]] = None) -> None:
        """Displays the current battlefield map."""
        battlefield_state = self.game_logic.get_battlefield_state()
        self.console.print("[bold]Battlefield Map:[/bold]")
        self.console.print(battlefield_state)
        self.console.print("Legend: . = Open, # = Cover, 1-2 = Elevation")

    def show_victory_points(self, _: Optional[List[str]] = None) -> None:
        """Displays the current victory points for each gang."""
        self.console.print("[bold]Current Victory Points:[/bold]")
        results = self.game_logic.calculate_victory_points()
        for result in results:
            self.console.print(f"{result['gang']}: {result['victory_points']} points")

        if self.game_logic.is_game_over():
            winner = self.game_logic.get_winner()
            self.console.print(f"\n[bold green]{winner}[/bold green]")

    def show_scenario(self, _: Optional[List[str]] = None) -> None:
        """Displays information about the current scenario."""
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
        """Checks and updates the status of scenario objectives."""
        self.game_logic.check_scenario_objectives()
        self.show_mission_objectives()

    # ... [other methods remain unchanged]
