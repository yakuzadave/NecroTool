from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt
from typing import List, Optional, Dict, Annotated
from enum import Enum


class ArmorType(str, Enum):
    FLACK = "Flak"
    MESH = "Mesh"
    CARAPACE = "Carapace"
    POWER = "Power"
    HAZARD_SUIT = "Hazard Suit"
    FURNACE_PLATES = "Furnace Plates"
    BONE = "Bone"
    STILL_SUIT = "Still Suit"
    ARMORED_UNDERSUIT = "Armored Undersuit"


class WeaponTrait(str, Enum):
    BLAST = "Blast"
    BLAZE = "Blaze"
    MELTA = "Melta"
    PIERCING = "Piercing"
    AP = "AP"  # Armor Piercing


class SaveCondition(BaseModel):
    """Represents conditions under which the armor's save value changes."""
    condition: Annotated[str, Field(description="The condition or trait affecting the save, e.g., 'against Blast'.")]
    save_modifier: Annotated[int, Field(description="The modified save value under this condition, e.g., 5 for 5+ save.")]


class ArmorModifier(BaseModel):
    """Represents an armor's modifier to gameplay effects."""
    type: Annotated[str, Field(description="Type of modifier, e.g., 'Resistance', 'Penalty', 'Save Bonus'.")]
    value: Annotated[int, Field(description="The value of the modifier, can be positive or negative.")]
    applicable_to: Annotated[Optional[List[WeaponTrait]], Field(
        None,
        description="List of weapon traits the modifier applies to, e.g., ['Blast', 'BLAZE']."
    )]
    description: Annotated[Optional[str], Field(None, description="Details about how the modifier works.")]


class Armor(BaseModel):
    """Represents armor with detailed mechanics and interactions."""
    name: Annotated[str, Field(description="Name of the armor.")]
    armor_type: Annotated[ArmorType, Field(description="Type of armor.")]
    save_value: Annotated[int, Field(description="Base armor save value (e.g., 6 for 6+ save).")]
    save_modifier: Annotated[Optional[int], Field(None, description="Modifier to the saving throw.")]
    conditional_saves: Annotated[List[SaveCondition], Field(
        default_factory=list,
        description="List of conditions that modify the save value (e.g., against specific traits)."
    )]
    special_rules: Annotated[List[str], Field(default_factory=list, description="Special rules associated with the armor.")]
    modifiers: Annotated[List[ArmorModifier], Field(
        default_factory=list,
        description="List of modifiers applied by the armor (e.g., resistance to specific traits)."
    )]
    is_bulk: Annotated[bool, Field(False, description="Indicates whether the armor is bulky, affecting movement or agility.")]
    cost: Annotated[Optional[PositiveInt], Field(None, description="The cost of the armor in credits.")]
    rarity: Annotated[Optional[str], Field(None, description="Rarity of the armor, e.g., Common, Rare, Exotic.")]
    weight: Annotated[Optional[float], Field(None, description="Weight of the armor in kilograms, affecting movement penalties.")]
    description: Annotated[Optional[str], Field(None, description="Additional details about the armor.")]

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "name": "Furnace Plates",
                "armor_type": "Furnace Plates",
                "save_value": 6,
                "save_modifier": 1,
                "conditional_saves": [
                    {"condition": "When facing Blast or Blaze traits", "save_modifier": 5}
                ],
                "special_rules": ["Provides +1 Toughness when engaged in melee combat."],
                "modifiers": [
                    {
                        "type": "Resistance",
                        "value": 2,
                        "applicable_to": ["Blast", "Blaze"],
                        "description": "Reduces incoming damage from Blast or Blaze traits by 2."
                    }
                ],
                "is_bulk": True,
                "cost": 30,
                "rarity": "Rare",
                "weight": 5.0,
                "description": "Heavy, bulky armor designed to protect workers in harsh environments."
            }]
        },
        "arbitrary_types_allowed": True,
        "validate_assignment": True
    }
