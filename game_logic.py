import logging
import d20
import random
from models import GameState, Gang, Ganger, Weapon, WeaponProfile, CombatRound, CombatPhase, PhaseName, Scenario, ScenarioObjective, Battlefield, Tile
from typing import List, Optional, Dict, Union, Any
from database import Database
from rich.table import Table

class GameLogic:
    def __init__(self, db: Database):
        self.db = db
        self.game_state = self._initialize_game_state()
        self.active_fighter_index = 0
        self.create_new_combat_round()  # Initialize the first combat round
        logging.info("GameLogic initialized")

    # ... [previous methods remain unchanged]

    def move_fighter(self, fighter_name: str, x: int, y: int) -> bool:
        fighter = self._get_fighter_by_name(fighter_name)
        if not fighter:
            return False
        
        if fighter.x is None or fighter.y is None:
            # Set initial position to (0, 0) if not set
            fighter.x, fighter.y = 0, 0
        
        # Calculate Manhattan distance
        distance = abs(fighter.x - x) + abs(fighter.y - y)
        
        if distance > fighter.movement:
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
                    if tile.type == 'open':
                        state += "."
                    elif tile.type == 'cover':
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

    # ... [rest of the methods remain unchanged]
