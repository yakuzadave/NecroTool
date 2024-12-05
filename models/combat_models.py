from pydantic import BaseModel, Field, PositiveInt
from typing import List, Optional, Annotated
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
    name: Annotated[str, Field(description="Name of the action, e.g., Move, Shoot, Charge.")]
    action_type: Annotated[ActionType, Field(description="Type of action: Simple, Basic, or Double.")]
    description: Annotated[Optional[str], Field(description="Detailed description of the action.")]
    conditions: Annotated[Optional[str], Field(description="Conditions under which the action can be performed.")]
    effect: Annotated[Optional[str], Field(description="Effect of the action on gameplay.")]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Move",
                    "action_type": "Simple",
                    "description": "Move up to your Movement characteristic in inches",
                    "conditions": "Not engaged in combat",
                    "effect": "Changes position on battlefield"
                }
            ]
        }
    }

class CombatPhase(BaseModel):
    """Represents a phase of combat."""
    name: Annotated[PhaseName, Field(description="Name of the phase: Priority Phase, Action Phase, or End Phase.")]
    description: Annotated[Optional[str], Field(description="Detailed description of what happens during this phase.")]
    actions: Annotated[List[Action], Field(default_factory=list, description="List of actions that can be taken during this phase.")]

    def log_phase_summary(self) -> str:
        """Generate a summary of the phase."""
        actions_summary = ", ".join(action.name for action in self.actions)
        return f"{self.name.value}: Actions available - {actions_summary}"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Action Phase",
                    "description": "Main phase where fighters perform their actions",
                    "actions": []
                }
            ]
        }
    }

class CombatRound(BaseModel):
    """Represents a combat round, including its phases and events."""
    round_number: Annotated[PositiveInt, Field(description="The number of the combat round, starting from 1.")]
    phases: Annotated[List[CombatPhase], Field(description="List of phases that occur in this round of combat.")]
    special_rules: Annotated[List[str], Field(default_factory=list, description="Special rules or events specific to this round.")]
    summary: Annotated[Optional[str], Field(default=None, description="A summary of key events that took place during this round.")]
    event_log: Annotated[List[str], Field(default_factory=list, description="Log of significant events in this round.")]

    def add_event(self, event: str):
        """Log an event in the combat round."""
        self.event_log.append(event)

    def summarize_round(self):
        """Summarize the round based on phases and logged events."""
        phase_summaries = "\n".join(phase.log_phase_summary() for phase in self.phases)
        events = "\n".join(self.event_log)
        self.summary = f"Round {self.round_number} Summary:\n{phase_summaries}\nEvents:\n{events}"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "round_number": 1,
                    "phases": [],
                    "special_rules": [],
                    "summary": None,
                    "event_log": []
                }
            ]
        }
    }
