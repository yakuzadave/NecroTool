from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt
from typing import List, Optional, Union, Dict, Tuple, Annotated

class ScenarioObjective(BaseModel):
    """Represents an objective in a scenario that can be completed for rewards."""
    name: Annotated[str, Field(description="Name of the objective.")]
    description: Annotated[Optional[str], Field(description="Detailed description of the objective.")]
    rewards: Annotated[Optional[List[str]], Field(description="List of rewards for completing the objective.")]
    completed: Annotated[bool, Field(default=False, description="Whether the objective is completed.")]
    points: Annotated[NonNegativeInt, Field(default=0, description="Victory points awarded for completing this objective.")]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Capture Territory",
                    "description": "Control the central objective marker for 2 turns",
                    "rewards": ["100 credits", "Territory card"],
                    "completed": False,
                    "points": 3
                }
            ]
        }
    }

class ScenarioDeploymentZone(BaseModel):
    """Represents a deployment zone in a scenario where gangs can set up."""
    name: Annotated[str, Field(description="Name of the deployment zone.")]
    description: Annotated[Optional[str], Field(description="Detailed description of the zone.")]
    starting_positions: Annotated[Optional[Dict[str, Tuple[int,int]]], Field(
        description="A mapping of gang names to their starting coordinates, e.g., {'Red Runners': (0,0)}."
    )]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "North Zone",
                    "description": "Deploy within 6\" of the north table edge",
                    "starting_positions": {
                        "Goliaths": (0, 0),
                        "Eschers": (1, 0)
                    }
                }
            ]
        }
    }

class ScenarioSpecialRule(BaseModel):
    """Represents a special rule that applies to a specific scenario."""
    name: Annotated[str, Field(description="Name of the special rule.")]
    effect: Annotated[Optional[str], Field(description="Description of the rule's effect on gameplay.")]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Darkness",
                    "effect": "All shooting attacks suffer -1 to hit"
                }
            ]
        }
    }

class ScenarioRewards(BaseModel):
    """Represents the rewards available for completing a scenario."""
    credits: Annotated[NonNegativeInt, Field(default=0)]
    reputation: Annotated[NonNegativeInt, Field(default=0)]
    items: Annotated[Optional[List[str]], Field(default=None, description="Special equipment rewards")]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "credits": 100,
                    "reputation": 5,
                    "items": ["Rare Weapon", "Territory Card"]
                }
            ]
        }
    }

class Scenario(BaseModel):
    """Represents a complete scenario with all its components."""
    name: Annotated[str, Field(description="Name of the scenario.")]
    description: Annotated[Optional[str], Field(description="Detailed description of the scenario.")]
    objectives: Annotated[List[ScenarioObjective], Field(default_factory=list, description="List of scenario objectives.")]
    deployment_zones: Annotated[List[ScenarioDeploymentZone], Field(default_factory=list, description="List of deployment zones.")]
    special_rules: Annotated[List[ScenarioSpecialRule], Field(default_factory=list, description="List of special rules.")]
    max_gangs: Annotated[PositiveInt, Field(default=2, description="The maximum number of gangs that can participate.")]
    duration: Annotated[Optional[Union[str, int, Tuple[int,int]]], Field(
        description="The expected duration of the scenario. Can be a string ('3-5 turns'), an integer (5 turns), or a tuple (3,5)."
    )]
    rewards: Annotated[Optional[ScenarioRewards], Field(description="Rewards for winning the scenario.")]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Territory War",
                    "description": "A battle for control of valuable territory",
                    "objectives": [],
                    "deployment_zones": [],
                    "special_rules": [],
                    "max_gangs": 2,
                    "duration": "6 turns",
                    "rewards": {
                        "credits": 200,
                        "reputation": 10,
                        "items": ["Territory Card"]
                    }
                }
            ]
        }
    }
