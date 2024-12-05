from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt
from typing import List, Optional
from enum import Enum


class Rarity(str, Enum):
    COMMON = "Common"
    RARE = "Rare"
    ILLEGAL = "Illegal"
    EXOTIC = "Exotic"


class SpecialRule(BaseModel):
    """Represents a special rule or effect associated with an item."""
    name: str = Field(..., description="Name of the special rule.")
    effect: Optional[str] = Field(None, description="Description of the rule's effect on gameplay.")
    condition: Optional[str] = Field(None, description="Conditions under which the rule applies, if any.")


class Modifier(BaseModel):
    """Represents a stat modifier provided by an item."""
    stat: str = Field(..., description="The stat being modified, e.g., 'Strength', 'Toughness'.")
    value: int = Field(..., description="The value of the modifier, can be positive or negative.")
    condition: Optional[str] = Field(None, description="Conditions under which the modifier applies, if any.")


class Consumable(BaseModel):
    """Represents a consumable item used in battles or campaigns."""
    name: str = Field(..., description="Name of the consumable item (e.g., Stimm-Slug Stash, Medipack).")
    cost: Optional[PositiveInt] = Field(None, description="Credit cost of the consumable.")
    rarity: Optional[Rarity] = Field(None, description="Rarity level of the consumable.")
    uses: PositiveInt = Field(..., description="Number of uses the consumable item has.")
    effect: Optional[str] = Field(None, description="Effect or benefit provided by the consumable item.")
    side_effects: Optional[str] = Field(None, description="Negative side effects of using the consumable item.")
    description: Optional[str] = Field(None, description="Detailed description of the consumable.")
    special_rules: List[SpecialRule] = Field(default_factory=list, description="Special rules associated with the consumable.")

    def use(self) -> bool:
        """Use one charge of the consumable, if available."""
        if self.uses > 0:
            self.uses -= 1
            return True
        return False

    def is_exhausted(self) -> bool:
        """Check if the consumable is out of uses."""
        return self.uses <= 0


class Equipment(BaseModel):
    """Represents an equipment item with various gameplay effects."""
    name: str = Field(..., description="Name of the equipment (e.g., Grapnel Launcher, Photo-Visor).")
    cost: Optional[PositiveInt] = Field(None, description="Credit cost of the equipment.")
    rarity: Optional[Rarity] = Field(None, description="Rarity level of the equipment.")
    weight: Optional[str] = Field(None, description="Weight category of the equipment (e.g., Light, Medium, Heavy).")
    special_rules: List[SpecialRule] = Field(default_factory=list, description="Special rules associated with the equipment.")
    modifiers: List[Modifier] = Field(default_factory=list, description="Stat modifiers provided by the equipment.")
    is_restricted: bool = Field(False, description="Indicates if the equipment is restricted and requires special permission.")
    description: Optional[str] = Field(None, description="Detailed description of the equipment.")

    def has_rule(self, rule_name: str) -> bool:
        """Check if the equipment has a specific special rule."""
        return any(rule.name == rule_name for rule in self.special_rules)

    def applicable_modifiers(self, stat: str) -> List[Modifier]:
        """Get modifiers applicable to a specific stat."""
        return [mod for mod in self.modifiers if mod.stat == stat]

