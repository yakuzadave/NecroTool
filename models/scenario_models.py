from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt
from typing import List, Optional, Union, Dict, Tuple

class ScenarioObjective(BaseModel):
    name: str = Field(..., description="Name of the objective.")
    description: Optional[str] = Field(None, description="Detailed description of the objective.")
    # Use a structured reward model or at least make it a list of strings if multiple rewards:
    rewards: Optional[List[str]] = Field(None, description="List of rewards for completing the objective.")
    completed: bool = Field(False, description="Whether the objective is completed.")
    points: NonNegativeInt = Field(0, description="Victory points awarded for completing this objective.")

class ScenarioDeploymentZone(BaseModel):
    name: str = Field(..., description="Name of the deployment zone.")
    description: Optional[str] = Field(None, description="Detailed description of the zone.")
    # Consider a structured approach:
    # For example, a list of tuples representing coordinates or a dict mapping gang names to coordinates.
    # Here we assume a simple dict: { "GangName": (x, y) }
    starting_positions: Optional[Dict[str, Tuple[int,int]]] = Field(
        None,
        description="A mapping of gang names to their starting coordinates, e.g., {'Red Runners': (0,0)}."
    )

class ScenarioSpecialRule(BaseModel):
    name: str = Field(..., description="Name of the special rule.")
    # Instead of just a string, consider making 'effect' more structured if we need to parse it.
    effect: Optional[str] = Field(None, description="Description of the rule's effect on gameplay.")

# Consider a structured rewards model for the scenario itself
class ScenarioRewards(BaseModel):
    credits: NonNegativeInt = 0
    reputation: NonNegativeInt = 0
    items: Optional[List[str]] = None  # e.g. special equipment

class Scenario(BaseModel):
    name: str = Field(..., description="Name of the scenario.")
    description: Optional[str] = Field(None, description="Detailed description of the scenario.")
    # Provide defaults so the model is easier to use:
    objectives: List[ScenarioObjective] = Field(default_factory=list, description="List of scenario objectives.")
    deployment_zones: List[ScenarioDeploymentZone] = Field(default_factory=list, description="List of deployment zones.")
    special_rules: List[ScenarioSpecialRule] = Field(default_factory=list, description="List of special rules.")

    max_gangs: PositiveInt = Field(2, description="The maximum number of gangs that can participate.")
    # For duration, consider using either an integer number of turns or a tuple (min_turns, max_turns) or a union:
    duration: Optional[Union[str, int, Tuple[int,int]]] = Field(
        None,
        description="The expected duration of the scenario. Can be a string ('3-5 turns'), an integer (5 turns), or a tuple (3,5)."
    )
    # Use a structured rewards model to simplify parsing in code:
    rewards: Optional[ScenarioRewards] = Field(None, description="Rewards for winning the scenario.")
