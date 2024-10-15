from pydantic import BaseModel, Field, validator
from typing import List, Optional
from models import Weapon, Equipment, SpecialRule, GangMember

class WeaponInput(BaseModel):
    name: str
    range: str
    strength: int
    armor_penetration: int
    damage: int
    ammo: str
    traits: List[str] = []

class EquipmentInput(BaseModel):
    name: str
    description: str

class SpecialRuleInput(BaseModel):
    name: str
    description: str
    effect: str

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
        
        weapons = [Weapon(**w.dict()) for w in validated_input.weapons]
        equipment = [Equipment(**e.dict()) for e in validated_input.equipment]
        special_rules = [SpecialRule(**s.dict()) for s in validated_input.special_rules]

        return GangMember(
            **validated_input.dict(exclude={'weapons', 'equipment', 'special_rules'}),
            weapons=weapons,
            equipment=equipment,
            special_rules=special_rules,
            xp=0
        )
    except ValueError as e:
        raise ValueError(f"Invalid gang member data: {str(e)}")
