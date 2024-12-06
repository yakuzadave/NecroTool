from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt
from typing import List, Optional, Annotated
from enum import Enum


class Rarity(str, Enum):
    COMMON = "Common"
    RARE = "Rare"
    ILLEGAL = "Illegal"
    EXOTIC = "Exotic"


class SpecialRule(BaseModel):
    """Represents a special rule or effect associated with an item."""
    name: Annotated[str, Field(description="Name of the special rule.")]
    effect: Annotated[Optional[str], Field(description="Description of the rule's effect on gameplay.")]
    condition: Annotated[Optional[str], Field(description="Conditions under which the rule applies, if any.")]

    model_config = {
        "validate_assignment": True,
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Rapid Fire",
                    "effect": "Allows two shots at -1 to hit",
                    "condition": "When using a Basic weapon"
                }
            ]
        }
    }


class Modifier(BaseModel):
    """Represents a stat modifier provided by an item."""
    stat: Annotated[str, Field(description="The stat being modified, e.g., 'Strength', 'Toughness'.")]
    value: Annotated[int, Field(description="The value of the modifier, can be positive or negative.")]
    condition: Annotated[Optional[str], Field(description="Conditions under which the modifier applies, if any.")]

    model_config = {
        "validate_assignment": True,
        "json_schema_extra": {
            "examples": [
                {
                    "stat": "Strength",
                    "value": 1,
                    "condition": "When in close combat"
                }
            ]
        }
    }


class Consumable(BaseModel):
    """Represents a consumable item used in battles or campaigns."""
    name: Annotated[str, Field(description="Name of the consumable item (e.g., Stimm-Slug Stash, Medipack).")]
    cost: Annotated[Optional[PositiveInt], Field(description="Credit cost of the consumable.")]
    rarity: Annotated[Optional[Rarity], Field(description="Rarity level of the consumable.")]
    uses: Annotated[PositiveInt, Field(description="Number of uses the consumable item has.")]
    effect: Annotated[Optional[str], Field(description="Effect or benefit provided by the consumable item.")]
    side_effects: Annotated[Optional[str], Field(description="Negative side effects of using the consumable item.")]
    description: Annotated[Optional[str], Field(description="Detailed description of the consumable.")]
    special_rules: Annotated[List[SpecialRule], Field(default_factory=list, description="Special rules associated with the consumable.")]

    def use(self) -> bool:
        """Use one charge of the consumable, if available."""
        if self.uses > 0:
            self.uses -= 1
            return True
        return False

    def is_exhausted(self) -> bool:
        """Check if the consumable is out of uses."""
        return self.uses <= 0

    model_config = {
        "validate_assignment": True,
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Stimm-Slug Stash",
                    "cost": 30,
                    "rarity": "Rare",
                    "uses": 3,
                    "effect": "Gain +1 Strength and +1 Toughness for one round",
                    "side_effects": "Take one automatic hit at the end of the round",
                    "description": "A powerful combat stimulant that enhances physical capabilities",
                    "special_rules": [
                        {
                            "name": "Combat Boost",
                            "effect": "Temporary stat increase",
                            "condition": "Must be used before activation"
                        }
                    ]
                }
            ]
        }
    }


class Equipment(BaseModel):
    """Represents an equipment item with various gameplay effects."""
    name: Annotated[str, Field(description="Name of the equipment (e.g., Grapnel Launcher, Photo-Visor).")]
    cost: Annotated[Optional[PositiveInt], Field(description="Credit cost of the equipment.")]
    rarity: Annotated[Optional[Rarity], Field(description="Rarity level of the equipment.")]
    weight: Annotated[Optional[str], Field(description="Weight category of the equipment (e.g., Light, Medium, Heavy).")]
    special_rules: Annotated[List[SpecialRule], Field(default_factory=list, description="Special rules associated with the equipment.")]
    modifiers: Annotated[List[Modifier], Field(default_factory=list, description="Stat modifiers provided by the equipment.")]
    is_restricted: Annotated[bool, Field(default=False, description="Indicates if the equipment is restricted and requires special permission.")]
    description: Annotated[Optional[str], Field(description="Detailed description of the equipment.")]

    def has_rule(self, rule_name: str) -> bool:
        """Check if the equipment has a specific special rule."""
        return any(rule.name == rule_name for rule in self.special_rules)

    def applicable_modifiers(self, stat: str) -> List[Modifier]:
        """Get modifiers applicable to a specific stat."""
        return [mod for mod in self.modifiers if mod.stat == stat]

    model_config = {
        "validate_assignment": True,
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Photo-Visor",
                    "cost": 35,
                    "rarity": "Common",
                    "weight": "Light",
                    "special_rules": [
                        {
                            "name": "Night Vision",
                            "effect": "Ignore darkness penalties",
                            "condition": "When equipped"
                        }
                    ],
                    "modifiers": [
                        {
                            "stat": "Ballistic Skill",
                            "value": 1,
                            "condition": "When shooting at targets in cover"
                        }
                    ],
                    "is_restricted": False,
                    "description": "Advanced optical enhancement device that improves targeting and visibility in low-light conditions."
                }
            ]
        }
    }

