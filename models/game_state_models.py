from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt, model_validator
from typing_extensions import Annotated
from typing import List, Optional
from enum import Enum
from .gang_models import Gang
from .battlefield_models import Battlefield
from .scenario_models import Scenario
from .combat_models import CombatRound


class GamePhase(str, Enum):
    PRE_BATTLE = "Pre-Battle"
    PRIORITY_PHASE = "Priority Phase"
    ACTION_PHASE = "Action Phase"
    END_PHASE = "End Phase"
    POST_BATTLE = "Post-Battle"


class GameState(BaseModel):
    """Represents the state of the game."""
    gangs: List[Gang] = Field(..., description="List of gangs participating in the game.")
    battlefield: Battlefield = Field(..., description="Representation of the battlefield.")
    scenario: Optional[Scenario] = Field(None, description="The current scenario being played.")
    current_turn: PositiveInt = Field(1, description="Current turn number.")
    active_gang_index: NonNegativeInt = Field(0, description="Index of the currently active gang.")
    max_turns: PositiveInt = Field(10, description="Maximum number of turns for the game.")
    combat_rounds: List[CombatRound] = Field(default_factory=list, description="List of combat rounds in the game.")
    game_phase: GamePhase = Field(GamePhase.PRE_BATTLE, description="Current phase of the game.")
    event_log: List[str] = Field(default_factory=list, description="Log of significant game events.")
    fighter_activations: List[str] = Field(default_factory=list, description="Track which fighters have been activated in the current turn.")

    @model_validator(mode='before')
    @classmethod
    def validate_active_gang_index(cls, values):
        """Ensure the active gang index is valid."""
        active_index = values.get("active_gang_index", 0)
        gangs = values.get("gangs", [])
        if not gangs or active_index >= len(gangs):
            raise ValueError("Active gang index must correspond to a valid gang.")
        return values

    def advance_turn(self):
        """Advance the game to the next turn."""
        if self.current_turn < self.max_turns:
            self.current_turn += 1
            self.game_phase = GamePhase.PRIORITY_PHASE
            self.fighter_activations = []
            self.event_log.append(f"Turn {self.current_turn} begins. Priority Phase starts.")
        else:
            self.event_log.append("Maximum number of turns reached. The game ends.")

    def switch_active_gang(self):
        """Switch to the next gang in the turn order."""
        self.active_gang_index = (self.active_gang_index + 1) % len(self.gangs)
        active_gang = self.gangs[self.active_gang_index]
        self.event_log.append(f"Active gang switched to {active_gang.name}.")

    def add_combat_round(self, combat_round: CombatRound):
        """Record a combat round in the game state."""
        self.combat_rounds.append(combat_round)
        self.event_log.append(f"Combat round recorded: {combat_round.summary()}.")

    def activate_fighter(self, fighter_name: str):
        """Activate a fighter for the current turn."""
        if fighter_name in self.fighter_activations:
            raise ValueError(f"Fighter {fighter_name} has already been activated this turn.")
        self.fighter_activations.append(fighter_name)
        self.event_log.append(f"Fighter {fighter_name} activated.")

    def check_end_conditions(self) -> bool:
        """Check if the game has reached an end condition."""
        # Example condition: all gangs but one are out of action
        active_gangs = [gang for gang in self.gangs if any(not member.is_out_of_action for member in gang.members)]
        if len(active_gangs) <= 1:
            self.event_log.append(f"Game ends: {active_gangs[0].name} is the last gang standing." if active_gangs else "Game ends: No gangs remain active.")
            return True
        if self.current_turn >= self.max_turns:
            self.event_log.append("Game ends: Maximum turns reached.")
            return True
        return False

    def resolve_post_battle(self):
        """Handle post-battle sequence."""
        self.game_phase = GamePhase.POST_BATTLE
        self.event_log.append("Post-Battle sequence begins.")
        for gang in self.gangs:
            for member in gang.members:
                if member.is_out_of_action:
                    self.event_log.append(f"Resolving injury for {member.name} in gang {gang.name}.")
                    # Placeholder: Apply injury resolution logic
