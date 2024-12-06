from pydantic import BaseModel, Field, model_validator, PositiveInt, NonNegativeInt
from typing import List, Optional, Annotated
from enum import Enum


class WeaponType(str, Enum):
    BASIC = "Basic"
    PISTOL = "Pistol"
    HEAVY = "Heavy"
    MELEE = "Melee"
    SPECIAL = "Special"
    GRENADE = "Grenade"


class Rarity(str, Enum):
    COMMON = "Common"
    RARE = "Rare"
    EXOTIC = "Exotic"
    ILLEGAL = "Illegal"


class WeaponTrait(BaseModel):
    """Represents a specific trait associated with a weapon."""
    name: Annotated[str, Field(description="The name of the weapon trait, e.g., Rapid Fire, Knockback, Unwieldy.")]
    description: Annotated[Optional[str], Field(description="A description of the trait and its effect on the weapon or ganger.")]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Rapid Fire",
                    "description": "Allows the weapon to fire multiple times at a -1 to hit penalty"
                }
            ]
        }
    }


class WeaponProfile(BaseModel):
    """Represents a firing mode or melee profile for a weapon."""
    range: Annotated[str, Field(description="The range of the weapon, e.g., 'Short: 0-8', 'Long: 8-24'.")]
    short_range_modifier: Annotated[Optional[int], Field(description="Modifier to hit rolls at short range.")]
    long_range_modifier: Annotated[Optional[int], Field(description="Modifier to hit rolls at long range.")]
    strength: Annotated[PositiveInt, Field(description="The strength value of the weapon.")]
    armor_penetration: Annotated[NonNegativeInt, Field(description="The armor penetration value of the weapon.")]
    damage: Annotated[PositiveInt, Field(description="The damage dealt by the weapon when it successfully wounds.")]
    ammo_roll: Annotated[Optional[str], Field(description="The ammo roll required to avoid running out of ammo, e.g., '4+'.")]
    blast_radius: Annotated[Optional[str], Field(description="Blast radius of the weapon, if applicable (e.g., '3\" template').")]
    traits: Annotated[List[WeaponTrait], Field(default_factory=list, description="Traits or special abilities associated with this profile.")]

    @model_validator(mode='after')
    def validate_range_structure(self) -> 'WeaponProfile':
        """Ensure the range field has a valid structure."""
        if not self.range or "Short:" not in self.range or "Long:" not in self.range:
            raise ValueError("Range must specify both short and long ranges, e.g., 'Short: 0-8, Long: 8-24'.")
        return self

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "range": "Short: 0-8, Long: 8-24",
                    "short_range_modifier": 0,
                    "long_range_modifier": -1,
                    "strength": 4,
                    "armor_penetration": 1,
                    "damage": 1,
                    "ammo_roll": "4+",
                    "blast_radius": None,
                    "traits": []
                }
            ]
        }
    }


class Weapon(BaseModel):
    """Represents a weapon, including its traits, profiles, and cost."""
    name: Annotated[str, Field(description="The name of the weapon, e.g., Lasgun, Bolt Pistol.")]
    weapon_type: Annotated[WeaponType, Field(description="The type of the weapon, e.g., Basic, Pistol, Heavy, Melee.")]
    cost: Annotated[Optional[PositiveInt], Field(description="The credit cost of the weapon.")]
    rarity: Annotated[Optional[Rarity], Field(description="The rarity level of the weapon.")]
    traits: Annotated[List[WeaponTrait], Field(default_factory=list, description="Traits or special abilities associated with the weapon.")]
    profiles: Annotated[List[WeaponProfile], Field(description="List of weapon profiles representing different firing modes or melee stats.")]
    is_unwieldy: Annotated[bool, Field(default=False, description="Indicates whether the weapon is unwieldy, adding penalties to movement or attack.")]
    description: Annotated[Optional[str], Field(description="A detailed description of the weapon.")]

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Bolt Pistol",
                    "weapon_type": "Pistol",
                    "cost": 25,
                    "rarity": "Common",
                    "traits": [],
                    "profiles": [
                        {
                            "range": "Short: 0-8, Long: 8-16",
                            "short_range_modifier": 0,
                            "long_range_modifier": -1,
                            "strength": 4,
                            "armor_penetration": -1,
                            "damage": 1,
                            "ammo_roll": "6+",
                            "blast_radius": None,
                            "traits": []
                        }
                    ],
                    "is_unwieldy": False,
                    "description": "A compact but powerful pistol that fires mass-reactive bolt ammunition."
                }
            ]
        }
    }

    def calculate_effective_damage(self) -> int:
        """Calculate the effective damage of the weapon based on its profiles.
        
        Returns:
            int: The highest damage value among all weapon profiles
        """
        if not self.profiles:
            return 0
        return max(profile.damage for profile in self.profiles)
