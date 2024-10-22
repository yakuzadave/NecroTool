from pydantic import BaseModel, Field
from typing import List, Optional
from .armor_models import Armor
from .weapon_models import Weapon
from .item_models import Equipment, Consumable
from .rules_models import SpecialRule
from .vehicle_models import Vehicle

class Ganger(BaseModel):
    name: str = Field(..., description="Name of the gang member")
    gang_affiliation: str = Field(..., description="Gang to which this member belongs (e.g., Goliath, Escher, Cawdor)")
    role: str = Field(..., description="Role of the gang member (e.g., Leader, Champion, Ganger, Juve)")
    movement: int = Field(..., description="Movement characteristic")
    weapon_skill: int = Field(..., ge=2, le=6, description="Weapon Skill (WS) characteristic, between 2+ and 6+")
    ballistic_skill: int = Field(..., ge=2, le=6, description="Ballistic Skill (BS) characteristic, between 2+ and 6+")
    strength: int = Field(..., description="Strength characteristic")
    toughness: int = Field(..., description="Toughness characteristic")
    wounds: int = Field(..., ge=1, description="Wounds characteristic, minimum 1")
    initiative: int = Field(..., ge=2, le=6, description="Initiative characteristic, between 2+ and 6+")
    attacks: int = Field(..., description="Number of attacks")
    leadership: int = Field(..., ge=2, le=10, description="Leadership characteristic, between 2 and 10")
    cool: int = Field(..., ge=2, le=10, description="Cool characteristic, between 2 and 10")
    willpower: int = Field(..., ge=2, le=10, description="Willpower characteristic, between 2 and 10")
    intelligence: int = Field(..., ge=2, le=10, description="Intelligence characteristic, between 2 and 10")
    equipment: Optional[List[Equipment]] = Field(default_factory=list, description="List of equipment carried by the gang member")
    weapons: Optional[List[Weapon]] = Field(default_factory=list, description="List of weapons carried by the gang member")
    armor: Optional[Armor] = Field(None, description="Armor worn by the gang member")
    consumables: Optional[List[Consumable]] = Field(default_factory=list, description="List of consumables carried by the gang member")
    skills: List[str] = Field(default_factory=list, description="List of skills the gang member possesses")
    special_rules: List[SpecialRule] = Field(default_factory=list, description="List of special rules that apply to the gang member")
    injuries: List[str] = Field(default_factory=list, description="List of permanent injuries sustained by the gang member")
    xp: int = Field(0, description="Experience points earned by the gang member")
    x: Optional[int] = Field(None, description="X-coordinate of the fighter on the battlefield")
    y: Optional[int] = Field(None, description="Y-coordinate of the fighter on the battlefield")
    is_pinned: bool = Field(False, description="Indicates if the fighter is pinned")
    is_out_of_action: bool = Field(False, description="Indicates if the fighter is out of action")
    is_seriously_injured: bool = Field(False, description="Indicates if the fighter is seriously injured")
    is_prone: bool = Field(False, description="Indicates if the fighter is prone")
    status: Optional[str] = Field(None, description="Current status of the fighter (e.g., 'Flesh Wound', 'Seriously Injured', 'Out of Action')")

class Gang(BaseModel):
    name: str
    members: List[Ganger]
    credits: int = 1000
    special_rules: List[SpecialRule] = Field(default_factory=list, description="List of special rules that apply to the entire gang")
    victory_points: int = Field(0, description="Victory points earned by the gang")
    vehicles: Optional[List[Vehicle]] = Field(default_factory=list, description="List of vehicles owned by the gang")
