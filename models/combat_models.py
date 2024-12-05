from pydantic import BaseModel, Field, PositiveInt
from typing_extensions import Annotated
from typing import List, Optional
from enum import Enum

class PhaseName(str, Enum):
    PRIORITY = "Priority Phase"
    ACTION = "Action Phase"
    END = "End Phase"

class ActionType(str, Enum):
    SIMPLE = "Simple"
    BASIC = "Basic"
    DOUBLE = "Double"

class Action(BaseModel):
    """Represents an action a fighter can perform."""
    name: str = Field(..., description="Name of the action, e.g., Move, Shoot, Charge.")
    action_type: ActionType = Field(..., description="Type of action: Simple, Basic, or Double.")
    description: Optional[str] = Field(None, description="Detailed description of the action.")
    conditions: Optional[str] = Field(None, description="Conditions under which the action can be performed.")
    effect: Optional[str] = Field(None, description="Effect of the action on gameplay.")

class CombatPhase(BaseModel):
    """Represents a phase of combat."""
    name: PhaseName = Field(..., description="Name of the phase: Priority Phase, Action Phase, or End Phase.")
    description: Optional[str] = Field(None, description="Detailed description of what happens during this phase.")
    actions: List[Action] = Field(default_factory=list, description="List of actions that can be taken during this phase.")

    def log_phase_summary(self) -> str:
        """Generate a summary of the phase."""
        actions_summary = ", ".join(action.name for action in self.actions)
        return f"{self.name.value}: Actions available - {actions_summary}"

class CombatRound(BaseModel):
    """Represents a combat round, including its phases and events."""
    round_number: PositiveInt = Field(..., description="The number of the combat round, starting from 1.")
    phases: List[CombatPhase] = Field(..., description="List of phases that occur in this round of combat.")
    special_rules: List[str] = Field(default_factory=list, description="Special rules or events specific to this round.")
    summary: Optional[str] = Field(None, description="A summary of key events that took place during this round.")
    event_log: List[str] = Field(default_factory=list, description="Log of significant events in this round.")

    def add_event(self, event: str):
        """Log an event in the combat round."""
        self.event_log.append(event)

    def summarize_round(self):
        """Summarize the round based on phases and logged events."""
        phase_summaries = "\n".join(phase.log_phase_summary() for phase in self.phases)
        events = "\n".join(self.event_log)
        self.summary = f"Round {self.round_number} Summary:\n{phase_summaries}\nEvents:\n{events}"
