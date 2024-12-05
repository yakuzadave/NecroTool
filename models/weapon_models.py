from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt, root_validator
from typing import List, Optional
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
    name: str = Field(..., description="The name of the weapon trait, e.g., Rapid Fire, Knockback, Unwieldy.")
    description: Optional[str] = Field(None, description="A description of the trait and its effect on the weapon or ganger.")


class WeaponProfile(BaseModel):
    """Represents a firing mode or melee profile for a weapon."""
    range: str = Field(..., description="The range of the weapon, e.g., 'Short: 0-8', 'Long: 8-24'.")
    short_range_modifier: Optional[int] = Field(None, description="Modifier to hit rolls at short range.")
    long_range_modifier: Optional[int] = Field(None, description="Modifier to hit rolls at long range.")
    strength: PositiveInt = Field(..., description="The strength value of the weapon.")
    armor_penetration: NonNegativeInt = Field(..., description="The armor penetration value of the weapon.")
    damage: PositiveInt = Field(..., description="The damage dealt by the weapon when it successfully wounds.")
    ammo_roll: Optional[str] = Field(None, description="The ammo roll required to avoid running out of ammo, e.g., '4+'.")
    blast_radius: Optional[str] = Field(None, description="Blast radius of the weapon, if applicable (e.g., '3\" template').")
    traits: List[WeaponTrait] = Field(default_factory=list, description="Traits or special abilities associated with this profile.")

    @root_validator
    def validate_range_structure(cls, values):
        """Ensure the range field has a valid structure."""
        range_value = values.get("range", "")
        if not range_value or "Short:" not in range_value or "Long:" not in range_value:
            raise ValueError("Range must specify both short and long ranges, e.g., 'Short: 0-8, Long: 8-24'.")
        return values


class Weapon(BaseModel):
    """Represents a weapon, including its traits, profiles, and cost."""
    name: str = Field(..., description="The name of the weapon, e.g., Lasgun, Bolt Pistol.")
    weapon_type: WeaponType = Field(..., description="The type of the weapon, e.g., Basic, Pistol, Heavy, Melee.")
    cost: Optional[PositiveInt] = Field(None, description="The credit cost of the weapon.")
    rarity: Optional[Rarity] = Field(None, description="The rarity level of the weapon.")
    traits: List[WeaponTrait] = Field(default_factory=list, description="Traits or special abilities associated with the weapon.")
    profiles: List[WeaponProfile] = Field(..., description="List of weapon profiles representing different firing modes or melee stats.")
    is_unwieldy: bool = Field(False, description="Indicates whether the weapon is unwieldy, adding penalties to movement or attack.")
    description: Optional[str] = Field(None, description="A detailed description of the weapon.")

    def calculate_effective_damage(self) -> int:
        """Calculate the effective damage of the weapon based on its profiles."""
        return max(profile.damage for profile in self.profiles)