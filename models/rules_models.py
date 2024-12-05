from pydantic import BaseModel, Field
from typing import List, Optional


class RuleEffect(BaseModel):
    """Represents an individual effect of a rule."""
    target: str = Field(..., description="The target of the effect, e.g., 'Movement', 'Strength', 'Cover'.")
    modifier: Optional[int] = Field(None, description="The numeric modifier applied by the rule, if applicable.")
    description: Optional[str] = Field(None, description="A detailed description of the effect.")


class SpecialRule(BaseModel):
    """Represents a special rule with its effects and applicability."""
    name: str = Field(..., description="The name of the special rule, e.g., 'Blinding Fog', 'Rapid Fire'.")
    description: str = Field(..., description="A detailed description of the rule.")
    applicability: List[str] = Field(..., description="List of areas where the rule applies, e.g., 'Scenarios', 'Weapons', 'Models'.")
    conditions: Optional[str] = Field(None, description="Conditions under which the rule is active.")
    effects: List[RuleEffect] = Field(default_factory=list, description="List of effects the rule applies.")

    def summarize_effects(self) -> str:
        """Summarize the effects of the rule for display."""
        return "\n".join(
            f"- {effect.target}: {effect.modifier if effect.modifier is not None else ''} ({effect.description})"
            for effect in self.effects
        )