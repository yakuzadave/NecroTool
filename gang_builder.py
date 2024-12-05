from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import Annotated
from typing import List, Optional
from models import Weapon, WeaponTrait, WeaponProfile, Equipment, SpecialRule, Ganger, Armor
from models.gang_models import GangType, GangerRole


# Input models for traits, weapons, equipment, etc.
class WeaponTraitInput(BaseModel):
    name: str = Field(..., description="Name of the weapon trait.")
    description: Optional[str] = Field(None, description="Description of the weapon trait.")


class WeaponProfileInput(BaseModel):
    range: str = Field(..., description="The range of the weapon profile.")
    strength: int = Field(..., ge=1, description="The strength value of the weapon.")
    armor_penetration: int = Field(..., ge=0, description="The armor penetration of the weapon.")
    damage: int = Field(..., ge=1, description="The damage dealt by the weapon.")
    ammo_roll: Optional[str] = Field(None, description="The ammo roll value of the weapon.")
    traits: Optional[List[WeaponTraitInput]] = Field(default_factory=list, description="Special traits of this profile.")


class WeaponInput(BaseModel):
    name: str = Field(..., description="Name of the weapon.")
    weapon_type: str = Field(..., description="Type of the weapon (e.g., Basic, Heavy).")
    cost: Optional[int] = Field(None, description="Cost of the weapon in credits.")
    rarity: Optional[str] = Field(None, description="Rarity of the weapon.")
    traits: Optional[List[WeaponTraitInput]] = Field(default_factory=list, description="List of traits for the weapon.")
    profiles: List[WeaponProfileInput] = Field(..., description="List of weapon profiles.")
    is_unwieldy: Optional[bool] = Field(False, description="Indicates whether the weapon is unwieldy.")
    description: Optional[str] = Field(None, description="Description or lore about the weapon.")


class EquipmentInput(BaseModel):
    name: str = Field(..., description="Name of the equipment.")
    description: str = Field(..., description="Description of the equipment.")


class SpecialRuleInput(BaseModel):
    name: str = Field(..., description="Name of the special rule.")
    description: str = Field(..., description="Description of the special rule.")
    effect: str = Field(..., description="Effect or impact of the rule.")


class ArmorInput(BaseModel):
    name: str = Field(..., description="Name of the armor.")
    armor_rating: int = Field(..., ge=0, le=6, description="Armor rating between 0 and 6.")
    locations: List[str] = Field(..., description="Body locations covered by the armor.")
    special_rules: Optional[List[str]] = Field(default_factory=list, description="Special rules for the armor.")


# Input model for Ganger creation
class GangerInput(BaseModel):
    name: str = Field(..., description="Name of the ganger.")
    role: GangerRole = Field(..., description="Role of the gang member.")
    gang_affiliation: GangType = Field(..., description="Gang affiliation type.")
    movement: int = Field(..., ge=1, le=10, description="Movement characteristic.")
    weapon_skill: int = Field(..., ge=2, le=6, description="Weapon skill characteristic.")
    ballistic_skill: int = Field(..., ge=2, le=6, description="Ballistic skill characteristic.")
    strength: int = Field(..., ge=1, le=10, description="Strength characteristic.")
    toughness: int = Field(..., ge=1, le=10, description="Toughness characteristic.")
    wounds: int = Field(..., ge=1, le=5, description="Wounds characteristic.")
    initiative: int = Field(..., ge=2, le=6, description="Initiative characteristic.")
    attacks: int = Field(..., ge=1, le=5, description="Number of attacks.")
    leadership: int = Field(..., ge=2, le=10, description="Leadership characteristic.")
    cool: int = Field(..., ge=2, le=10, description="Cool characteristic.")
    will: int = Field(..., ge=2, le=10, description="Will characteristic.")
    intelligence: int = Field(..., ge=2, le=10, description="Intelligence characteristic.")
    credits_value: int = Field(..., ge=0, description="Credits value assigned to this ganger.")
    role: GangerRole = Field(..., description="Role of the gang member.")
    weapons: List[WeaponInput] = Field(..., min_items=1, description="List of weapons carried.")
    equipment: Optional[List[EquipmentInput]] = Field(default_factory=list, description="List of equipment carried.")
    skills: Optional[List[str]] = Field(default_factory=list, description="List of skills possessed.")
    special_rules: Optional[List[SpecialRuleInput]] = Field(default_factory=list, description="Special rules for the ganger.")
    armor: Optional[ArmorInput] = Field(None, description="Armor worn by the ganger.")

    


# Create a Ganger instance
def create_gang_member(input_data: dict) -> Ganger:
    try:
        validated_input = GangerInput(**input_data)

        # Convert input models to game models
        weapons = [
            Weapon(
                name=w.name,
                weapon_type=w.weapon_type,
                cost=w.cost,
                rarity=w.rarity,
                traits=[WeaponTrait(**t.dict()) for t in w.traits],
                profiles=[WeaponProfile(**p.dict()) for p in w.profiles],
                is_unwieldy=w.is_unwieldy,
                description=w.description
            )
            for w in validated_input.weapons
        ]

        equipment = [Equipment(**e.dict()) for e in validated_input.equipment]
        special_rules = [SpecialRule(**s.dict()) for s in validated_input.special_rules]
        armor = Armor(**validated_input.armor.dict()) if validated_input.armor else None

        return Ganger(
            **validated_input.dict(exclude={"weapons", "equipment", "special_rules", "armor"}),
            weapons=weapons,
            equipment=equipment,
            special_rules=special_rules,
            armor=armor,
            xp=0
        )
    except ValueError as e:
        raise ValueError(f"Invalid gang member data: {str(e)}")
