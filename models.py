from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Weapon(BaseModel):
    name: str
    range: str
    strength: int
    armor_penetration: int
    damage: int
    ammo: str
    traits: List[str]

class Equipment(BaseModel):
    name: str
    description: str

class SpecialRule(BaseModel):
    name: str
    description: str
    effect: str

class GangMember(BaseModel):
    name: str = Field(..., description="Name of the gang member")
    gang: str = Field(..., description="Gang to which this member belongs (e.g., Goliath, Escher, Cawdor)")
    role: str = Field(..., description="Role in the gang (e.g., Leader, Champion, Ganger, Juve)")
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
    credits_value: int = Field(..., description="Credits value assigned to this gang member for balancing purposes")
    outlaw: bool = Field(False, description="Indicates if the gang member belongs to an outlaw gang")
    weapons: List[Weapon] = Field(..., description="List of weapons carried by the gang member")
    equipment: List[Equipment] = Field(default_factory=list, description="List of equipment carried by the gang member")
    skills: List[str] = Field(default_factory=list, description="List of skills the gang member possesses (e.g., Nerves of Steel, Combat Master)")
    special_rules: List[SpecialRule] = Field(default_factory=list, description="List of special rules that apply to the gang member")
    injuries: List[str] = Field(default_factory=list, description="List of permanent injuries sustained by the gang member")
    xp: int = Field(0, description="Experience points earned by the gang member")

class Gang(BaseModel):
    name: str
    members: List[GangMember]
    credits: int = 1000
    special_rules: List[SpecialRule] = Field(default_factory=list, description="List of special rules that apply to the entire gang")
    victory_points: int = Field(0, description="Victory points earned by the gang")

class Tile(BaseModel):
    x: int
    y: int
    type: str  # 'open', 'cover', 'elevation'
    elevation: int = 0

class Battlefield(BaseModel):
    width: int
    height: int
    tiles: List[Tile]

class MissionObjective(BaseModel):
    name: str
    description: str
    points: int
    completed: bool = False

class GameState(BaseModel):
    gangs: List[Gang]
    battlefield: Battlefield
    current_turn: int = 1
    active_gang_index: int = 0
    mission_objectives: List[MissionObjective] = Field(default_factory=list, description="List of mission objectives for the current game")
    max_turns: int = Field(10, description="Maximum number of turns for the game")
