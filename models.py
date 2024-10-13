from pydantic import BaseModel, Field
from typing import List, Optional

class Weapon(BaseModel):
    name: str
    range: int
    strength: int
    ap: int
    damage: int
    ammo: int
    traits: List[str] = Field(default_factory=list)

class Skill(BaseModel):
    name: str
    description: str

class Fighter(BaseModel):
    name: str
    move: int
    weapon_skill: int
    ballistic_skill: int
    strength: int
    toughness: int
    wounds: int
    initiative: int
    attacks: int
    leadership: int
    cool: int
    will: int
    intelligence: int
    weapons: List[Weapon]
    skills: List[Skill] = Field(default_factory=list)
    xp: int = 0
    credits: int = 0

class Gang(BaseModel):
    name: str
    fighters: List[Fighter]
    credits: int = 1000

class Tile(BaseModel):
    x: int
    y: int
    type: str  # 'open', 'cover', 'elevation'
    elevation: int = 0

class Battlefield(BaseModel):
    width: int
    height: int
    tiles: List[Tile]

class GameState(BaseModel):
    gangs: List[Gang]
    battlefield: Battlefield
    current_turn: int = 1
    active_gang_index: int = 0
