from pydantic import BaseModel, Field, validator
from typing import List, Optional
from models import Weapon, WeaponTrait, WeaponProfile, Equipment, SpecialRule, GangMember, ArmorModel

class WeaponTraitInput(BaseModel):
    name: str
    description: Optional[str] = None

class WeaponProfileInput(BaseModel):
    range: str
    strength: int
    armor_penetration: int
    damage: int
    ammo_roll: Optional[str] = None
    special_rules: Optional[List[str]] = None

class WeaponInput(BaseModel):
    name: str
    weapon_type: str
    cost: Optional[int] = None
    rarity: Optional[str] = None
    traits: Optional[List[WeaponTraitInput]] = None
    profiles: List[WeaponProfileInput]
    is_unwieldy: Optional[bool] = False
    description: Optional[str] = None

class EquipmentInput(BaseModel):
    name: str
    description: str

class SpecialRuleInput(BaseModel):
    name: str
    description: str
    effect: str

class ArmorInput(BaseModel):
    name: str = Field(..., description="Name of the armor")
    protection_value: int = Field(..., ge=0, le=6, description="Protection value of the armor, between 0 and 6")
    locations: List[str] = Field(..., description="Body locations covered by the armor")
    special_rules: List[str] = Field(default_factory=list, description="Special rules associated with the armor")

class GangMemberInput(BaseModel):
    name: str = Field(..., description="Name of the gang member")
    gang: str = Field(..., description="Gang to which this member belongs (e.g., Goliath, Escher, Cawdor)")
    role: str = Field(..., description="Role in the gang (e.g., Leader, Champion, Ganger, Juve)")
    movement: int = Field(..., ge=1, le=10, description="Movement characteristic")
    weapon_skill: int = Field(..., ge=2, le=6, description="Weapon Skill (WS) characteristic, between 2+ and 6+")
    ballistic_skill: int = Field(..., ge=2, le=6, description="Ballistic Skill (BS) characteristic, between 2+ and 6+")
    strength: int = Field(..., ge=1, le=10, description="Strength characteristic")
    toughness: int = Field(..., ge=1, le=10, description="Toughness characteristic")
    wounds: int = Field(..., ge=1, le=5, description="Wounds characteristic, minimum 1")
    initiative: int = Field(..., ge=2, le=6, description="Initiative characteristic, between 2+ and 6+")
    attacks: int = Field(..., ge=1, le=5, description="Number of attacks")
    leadership: int = Field(..., ge=2, le=10, description="Leadership characteristic, between 2 and 10")
    cool: int = Field(..., ge=2, le=10, description="Cool characteristic, between 2 and 10")
    willpower: int = Field(..., ge=2, le=10, description="Willpower characteristic, between 2 and 10")
    intelligence: int = Field(..., ge=2, le=10, description="Intelligence characteristic, between 2 and 10")
    credits_value: int = Field(..., ge=0, description="Credits value assigned to this gang member for balancing purposes")
    outlaw: bool = Field(False, description="Indicates if the gang member belongs to an outlaw gang")
    weapons: List[WeaponInput] = Field(..., min_items=1, description="List of weapons carried by the gang member")
    equipment: List[EquipmentInput] = Field(default_factory=list, description="List of equipment carried by the gang member")
    skills: List[str] = Field(default_factory=list, description="List of skills the gang member possesses (e.g., Nerves of Steel, Combat Master)")
    special_rules: List[SpecialRuleInput] = Field(default_factory=list, description="List of special rules that apply to the gang member")
    armor: Optional[ArmorInput] = Field(None, description="Armor worn by the gang member")

    @validator('role')
    def validate_role(cls, v):
        valid_roles = ['Leader', 'Champion', 'Ganger', 'Juve']
        if v.capitalize() not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        return v.capitalize()

def create_gang_member(input_data: dict) -> GangMember:
    """
    Create a GangMember instance from input data, using Pydantic for validation.

    Args:
        input_data (dict): A dictionary containing the gang member data.

    Returns:
        GangMember: A validated GangMember instance.

    Raises:
        ValueError: If the input data is invalid.
    """
    try:
        validated_input = GangMemberInput(**input_data)
        
        weapons = [
            Weapon(
                name=w.name,
                weapon_type=w.weapon_type,
                cost=w.cost,
                rarity=w.rarity,
                traits=[WeaponTrait(**t.dict()) for t in (w.traits or [])],
                profiles=[WeaponProfile(**p.dict()) for p in w.profiles],
                is_unwieldy=w.is_unwieldy,
                description=w.description
            )
            for w in validated_input.weapons
        ]
        equipment = [Equipment(**e.dict()) for e in validated_input.equipment]
        special_rules = [SpecialRule(**s.dict()) for s in validated_input.special_rules]
        armor = ArmorModel(**validated_input.armor.dict()) if validated_input.armor else None

        return GangMember(
            **validated_input.dict(exclude={'weapons', 'equipment', 'special_rules', 'armor'}),
            weapons=weapons,
            equipment=equipment,
            special_rules=special_rules,
            armor=armor,
            xp=0
        )
    except ValueError as e:
        raise ValueError(f"Invalid gang member data: {str(e)}")
