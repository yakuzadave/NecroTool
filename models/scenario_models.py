# scenario_models.py
from pydantic import BaseModel, Field
from typing import List, Optional

# Represents an objective in a scenario, with rewards and status.
class ScenarioObjective(BaseModel):
    name: str = Field(..., description="The name of the objective, e.g., Capture the Flag, Defend the Territory.")
    description: Optional[str] = Field(None, description="A detailed description of the objective and how it impacts gameplay.")
    rewards: Optional[str] = Field(None, description="Rewards for completing the objective, such as credits or reputation.")
    completed: bool = Field(False, description="Indicates whether the objective has been completed.")
    points: int = Field(0, description="Victory points awarded for completing this objective.")

# Represents a deployment zone within a scenario, where gangs start the game.
class ScenarioDeploymentZone(BaseModel):
    name: str = Field(..., description="The name of the deployment zone, e.g., Zone A, Northern Sector.")
    description: Optional[str] = Field(None, description="A detailed description of the deployment zone.")
    starting_positions: Optional[str] = Field(None, description="Information about starting positions for each gang.")

# Represents a special rule within a scenario, detailing its effect on gameplay.
class ScenarioSpecialRule(BaseModel):
    name: str = Field(..., description="The name of the special rule, e.g., Toxic Fog, Reinforcements.")
    effect: Optional[str] = Field(None, description="A description of the effect the special rule has on the scenario.")

# Represents an entire scenario, including objectives, deployment zones, and special rules.
class Scenario(BaseModel):
    name: str = Field(..., description="The name of the scenario, e.g., Ambush, Turf War.")
    description: Optional[str] = Field(None, description="A detailed description of the scenario, including lore or fluff.")
    objectives: List[ScenarioObjective] = Field(..., description="List of objectives that gangs must accomplish during the scenario.")
    deployment_zones: List[ScenarioDeploymentZone] = Field(..., description="List of deployment zones available in the scenario.")
    special_rules: Optional[List[ScenarioSpecialRule]] = Field(None, description="List of special rules that modify how the scenario is played.")
    max_gangs: Optional[int] = Field(2, description="The maximum number of gangs that can participate in the scenario.")
    duration: Optional[str] = Field(None, description="The expected duration of the scenario, e.g., '3-5 turns' or 'Until all objectives are completed'.")
    rewards: Optional[str] = Field(None, description="General rewards for winning the scenario, e.g., credits, territory, reputation.")