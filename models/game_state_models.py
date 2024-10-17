# game_state_models.py
from pydantic import BaseModel, Field
from typing import List, Optional
from .gang_models import Gang
from .battlefield_models import Battlefield
from .scenario_models import Scenario
from .combat_models import CombatRound

# Represents the state of the game, including gangs, battlefield, scenario, and combat rounds.
class GameState(BaseModel):
    gangs: List[Gang]  # List of gangs participating in the game.
    battlefield: Battlefield  # Representation of the battlefield.
    current_turn: int = 1  # Current turn number.
    active_gang_index: int = 0  # Index of the currently active gang.
    scenario: Optional[Scenario] = Field(None, description="The current scenario being played")
    max_turns: int = Field(10, description="Maximum number of turns for the game")
    combat_rounds: List[CombatRound] = Field(default_factory=list, description="List of combat rounds in the game")
