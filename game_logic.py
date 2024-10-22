import logging
import d20
import random
from models import GameState, Gang, Ganger, Weapon, WeaponProfile, CombatRound, CombatPhase, PhaseName, Scenario, ScenarioObjective, Battlefield, Tile, Consumable, Equipment
from typing import List, Optional, Dict, Union, Any
from database import Database
from rich.table import Table
import contextlib

class GameLogic:
    def __init__(self, db: Database):
        self.db = db
        self.game_state = self._initialize_game_state()
        self.active_fighter_index = 0
        self.d20 = d20  # Initialize d20 as an attribute
        self.create_new_combat_round()  # Initialize the first combat round
        logging.info("GameLogic initialized")

    # ... [previous methods remain unchanged]

    def move_fighter(self, fighter_name: str, x: int, y: int) -> bool:
        fighter = self._get_fighter_by_name(fighter_name)
        if not fighter:
            return False
        
        if abs(fighter.x - x) + abs(fighter.y - y) > fighter.movement:
            return False
        
        fighter.x = x
        fighter.y = y
        return True

    def get_battlefield_state(self) -> str:
        battlefield = self.game_state.battlefield
        state = ""
        for y in range(battlefield.height):
            for x in range(battlefield.width):
                tile = next((t for t in battlefield.tiles if t.x == x and t.y == y), None)
                if tile:
                    if tile.type == "open":
                        state += "."
                    elif tile.type == "cover":
                        state += "#"
                    else:
                        state += str(tile.elevation)
                else:
                    state += " "
            state += "\n"
        return state

    def calculate_victory_points(self) -> List[Dict[str, Union[str, int]]]:
        results = []
        for gang in self.game_state.gangs:
            results.append({
                "gang": gang.name,
                "victory_points": gang.victory_points
            })
        return results

    def is_game_over(self) -> bool:
        # Implement game over conditions (e.g., max turns reached, all fighters of a gang are out of action)
        return self.game_state.current_turn > self.game_state.max_turns

    def get_winner(self) -> Optional[str]:
        if not self.is_game_over():
            return None
        results = self.calculate_victory_points()
        winner = max(results, key=lambda x: x["victory_points"])
        return f"The winner is {winner['gang']} with {winner['victory_points']} victory points!"

    def get_scenario(self) -> Optional[Scenario]:
        return self.game_state.scenario

    def check_scenario_objectives(self) -> None:
        if not self.game_state.scenario:
            return
        
        for objective in self.game_state.scenario.objectives:
            # Implement logic to check if the objective is completed
            # This is a placeholder and should be replaced with actual logic
            if not objective.completed:
                objective.completed = random.choice([True, False])
                if objective.completed:
                    for gang in self.game_state.gangs:
                        gang.victory_points += objective.points

    # ... [other methods remain unchanged]
