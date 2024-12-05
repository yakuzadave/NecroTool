from pydantic import BaseModel, Field
from typing import List, Optional, Annotated


class RuleEffect(BaseModel):
    """Represents an individual effect of a rule."""
    target: Annotated[str, Field(description="The target of the effect, e.g., 'Movement', 'Strength', 'Cover'.")]
    modifier: Annotated[Optional[int], Field(description="The numeric modifier applied by the rule, if applicable.")]
    description: Annotated[Optional[str], Field(description="A detailed description of the effect.")]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "target": "Movement",
                    "modifier": -1,
                    "description": "Reduces movement by 1 inch"
                }
            ]
        }
    }


class SpecialRule(BaseModel):
    """Represents a special rule with its effects and applicability."""
    name: Annotated[str, Field(description="The name of the special rule, e.g., 'Blinding Fog', 'Rapid Fire'.")]
    description: Annotated[str, Field(description="A detailed description of the rule.")]
    applicability: Annotated[List[str], Field(description="List of areas where the rule applies, e.g., 'Scenarios', 'Weapons', 'Models'.")]
    conditions: Annotated[Optional[str], Field(description="Conditions under which the rule is active.")]
    effects: Annotated[List[RuleEffect], Field(default_factory=list, description="List of effects the rule applies.")]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Rapid Fire",
                    "description": "Allows multiple shots at reduced accuracy",
                    "applicability": ["Weapons", "Shooting Phase"],
                    "conditions": "When using a Basic weapon",
                    "effects": [
                        {
                            "target": "Number of Shots",
                            "modifier": 1,
                            "description": "Adds one additional shot"
                        }
                    ]
                }
            ]
        }
    }

    def summarize_effects(self) -> str:
        """Summarize the effects of the rule for display."""
        return "\n".join(
            f"- {effect.target}: {effect.modifier if effect.modifier is not None else ''} ({effect.description})"
            for effect in self.effects
        )