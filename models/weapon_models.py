
# weapon_models.py
from pydantic import BaseModel, Field
from typing import List, Optional

# Represents a specific trait associated with a weapon (e.g., Rapid Fire, Knockback).
class WeaponTrait(BaseModel):
    name: str = Field(..., description="The name of the weapon trait (e.g., Rapid Fire, Knockback, Unwieldy).")
    description: Optional[str] = Field(None, description="A description of the trait and its effect on the weapon or ganger.")

# Represents a firing mode or melee profile for a weapon.
class WeaponProfile(BaseModel):
    range: str = Field(..., description="The range of the weapon, e.g., 'Short: 0-8', 'Long: 8-24'.")
    strength: int = Field(..., description="The strength value of the weapon.")
    armor_penetration: int = Field(..., description="The armor penetration value of the weapon.")
    damage: int = Field(..., description="The damage dealt by the weapon when it successfully wounds.")
    ammo_roll: Optional[str] = Field(None, description="The ammo roll required to avoid running out of ammo, e.g., '4+'.")
    special_rules: Optional[List[str]] = Field(None, description="Any special rules associated with this profile.")

# Represents a weapon, including its traits, profiles, and cost.
class Weapon(BaseModel):
    name: str = Field(..., description="The name of the weapon, e.g., Lasgun, Bolt Pistol.")
    weapon_type: str = Field(..., description="The type of the weapon, e.g., Basic, Pistol, Heavy, Melee.")
    cost: Optional[int] = Field(None, description="The credit cost of the weapon, used for gang management purposes.")
    rarity: Optional[str] = Field(None, description="The rarity level of the weapon, used to determine availability in trading post.")
    traits: Optional[List[WeaponTrait]] = Field(None, description="Traits or special abilities associated with the weapon.")
    profiles: List[WeaponProfile] = Field(..., description="List of weapon profiles representing different firing modes or melee stats.")
    is_unwieldy: Optional[bool] = Field(False, description="Indicates whether the weapon is unwieldy, adding penalties to movement or attack.")
    description: Optional[str] = Field(None, description="A detailed description of the weapon, including lore or fluff.")
