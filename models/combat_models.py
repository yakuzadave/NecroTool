# combat_models.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class PhaseName(Enum):
    PRIORITY = "Priority Phase"
    MOVEMENT = "Movement Phase"
    SHOOTING = "Shooting Phase"
    CLOSE_COMBAT = "Close Combat Phase"
    END = "End Phase"

# Represents a phase of combat, detailing actions that can be taken.
class CombatPhase(BaseModel):
    name: str = Field(..., description="The name of the phase, e.g., Priority Phase, Movement Phase, Shooting Phase.")
    description: Optional[str] = Field(None, description="A detailed description of what happens during this phase.")
    actions: Optional[List[str]] = Field(None, description="List of actions that can be taken during this phase, e.g., Move, Shoot, Charge.")

# Represents a combat round, including its phases and any special rules.
class CombatRound(BaseModel):
    round_number: int = Field(..., ge=1, description="The number of the combat round, starting from 1.")
    phases: List[CombatPhase] = Field(..., description="List of phases that occur in this round of combat.")
    special_rules: Optional[List[str]] = Field(None, description="Special rules or events that are specific to this round.")
    summary: Optional[str] = Field(None, description="A summary of key events that took place during this round.")
