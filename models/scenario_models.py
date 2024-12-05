from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt
from typing import List, Optional, Union, Dict, Tuple, Annotated

class ScenarioObjective(BaseModel):
    name: Annotated[str, Field(description="Name of the objective.")]
    description: Annotated[Optional[str], Field(description="Detailed description of the objective.")]
    # Use a structured reward model or at least make it a list of strings if multiple rewards:
    rewards: Annotated[Optional[List[str]], Field(description="List of rewards for completing the objective.")]
    completed: Annotated[bool, Field(default=False, description="Whether the objective is completed.")]
    points: Annotated[NonNegativeInt, Field(default=0, description="Victory points awarded for completing this objective.")]

class ScenarioDeploymentZone(BaseModel):
    name: Annotated[str, Field(description="Name of the deployment zone.")]
    description: Annotated[Optional[str], Field(description="Detailed description of the zone.")]
    # Consider a structured approach:
    # For example, a list of tuples representing coordinates or a dict mapping gang names to coordinates.
    # Here we assume a simple dict: { "GangName": (x, y) }
    starting_positions: Annotated[Optional[Dict[str, Tuple[int,int]]], Field(
        description="A mapping of gang names to their starting coordinates, e.g., {'Red Runners': (0,0)}."
    )]

class ScenarioSpecialRule(BaseModel):
    name: Annotated[str, Field(description="Name of the special rule.")]
    # Instead of just a string, consider making 'effect' more structured if we need to parse it.
    effect: Annotated[Optional[str], Field(description="Description of the rule's effect on gameplay.")]

# Consider a structured rewards model for the scenario itself
class ScenarioRewards(BaseModel):
    credits: Annotated[NonNegativeInt, Field(default=0)]
    reputation: Annotated[NonNegativeInt, Field(default=0)]
    items: Annotated[Optional[List[str]], Field(default=None, description="Special equipment rewards")]  # e.g. special equipment

class Scenario(BaseModel):
    name: Annotated[str, Field(description="Name of the scenario.")]
    description: Annotated[Optional[str], Field(description="Detailed description of the scenario.")]
    # Provide defaults so the model is easier to use:
    objectives: Annotated[List[ScenarioObjective], Field(default_factory=list, description="List of scenario objectives.")]
    deployment_zones: Annotated[List[ScenarioDeploymentZone], Field(default_factory=list, description="List of deployment zones.")]
    special_rules: Annotated[List[ScenarioSpecialRule], Field(default_factory=list, description="List of special rules.")]

    max_gangs: Annotated[PositiveInt, Field(default=2, description="The maximum number of gangs that can participate.")]
    # For duration, consider using either an integer number of turns or a tuple (min_turns, max_turns) or a union:
    duration: Annotated[Optional[Union[str, int, Tuple[int,int]]], Field(
        description="The expected duration of the scenario. Can be a string ('3-5 turns'), an integer (5 turns), or a tuple (3,5)."
    )]
    # Use a structured rewards model to simplify parsing in code:
    rewards: Annotated[Optional[ScenarioRewards], Field(description="Rewards for winning the scenario.")]
