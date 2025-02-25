from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt, model_validator, ValidationError
from typing import List, Optional, Dict, Annotated
from enum import Enum
from .armor_models import Armor
from .weapon_models import Weapon
from .item_models import Equipment, Consumable
from .rules_models import SpecialRule
from .vehicle_models import Vehicle


class GangType(str, Enum):
    GOLIATH = "Goliath"
    ESCHER = "Escher"
    CAWDOR = "Cawdor"
    DELAQUE = "Delaque"
    VAN_SAAR = "Van Saar"
    ORLOCK = "Orlock"
    OUTCAST = "Outcast"
    ENFORCERS = "Enforcers"


class GangerRole(str, Enum):
    LEADER = "Leader"
    CHAMPION = "Champion"
    GANGER = "Ganger"
    JUVENILE = "Juve"
    SPECIALIST = "Specialist"
    
    
class InjuryResult(str, Enum):
    """Represents the result of an injury dice roll."""
    FLESH_WOUND = "Flesh Wound"
    SERIOUS_INJURY = "Serious Injury"
    OUT_OF_ACTION = "Out of Action"
    RECOVERED = "Recovered"
    DOWN = "Down"
    
    
class InjurySeverity(str, Enum):
    """Represents the severity of an injury."""
    MINOR = "Minor"
    MAJOR = "Major"
    CRITICAL = "Critical"
    MEMORABLE = "Memorable"


class Injury(BaseModel):
    """Represents an injury sustained by a ganger."""
    type: Annotated[str, Field(description="Type of injury (e.g., 'Flesh Wound', 'Missing Eye').")]
    severity: Annotated[str, Field(description="Severity of the injury (e.g., 'Minor', 'Major').")]
    effect: Annotated[Optional[str], Field(description="Effect of the injury on gameplay.")]
    attribute_modifiers: Annotated[Dict[str, int], Field(
        default_factory=dict, description="Attribute changes caused by the injury (e.g., {'Toughness': -1})."
    )]


class Ganger(BaseModel):
    """Represents a ganger in Necromunda."""
    name: Annotated[str, Field(description="Name of the gang member.")]
    gang_affiliation: Annotated[GangType, Field(description="Gang to which this member belongs.")]
    role: Annotated[GangerRole, Field(description="Role of the gang member.")]
    movement: Annotated[int, Field(description="Movement characteristic.")]
    weapon_skill: Annotated[int, Field(ge=2, le=6, description="Weapon Skill (WS) characteristic, between 2+ and 6+.")]
    ballistic_skill: Annotated[int, Field(ge=2, le=6, description="Ballistic Skill (BS) characteristic, between 2+ and 6+.")]
    strength: Annotated[int, Field(description="Strength characteristic.")]
    toughness: Annotated[int, Field(description="Toughness characteristic.")]
    wounds: Annotated[PositiveInt, Field(description="Wounds characteristic, minimum 1.")]
    initiative: Annotated[int, Field(ge=2, le=6, description="Initiative characteristic, between 2+ and 6+.")]
    attacks: Annotated[PositiveInt, Field(description="Number of attacks.")]
    leadership: Annotated[int, Field(ge=2, le=10, description="Leadership characteristic, between 2 and 10.")]
    cool: Annotated[int, Field(ge=2, le=10, description="Cool characteristic, between 2 and 10.")]
    will: Annotated[int, Field(ge=2, le=10, description="Will characteristic, between 2 and 10.")]
    intelligence: Annotated[int, Field(ge=2, le=10, description="Intelligence characteristic, between 2 and 10.")]
    equipment: Annotated[List[Equipment], Field(default_factory=list, description="List of equipment carried.")]
    weapons: Annotated[List[Weapon], Field(default_factory=list, description="List of weapons carried.")]
    armor: Annotated[Optional[Armor], Field(default=None, description="Armor worn by the ganger.")]
    consumables: Annotated[List[Consumable], Field(default_factory=list, description="Consumables carried.")]
    skills: Annotated[List[str], Field(default_factory=list, description="List of skills the ganger possesses.")]
    special_rules: Annotated[List[SpecialRule], Field(default_factory=list, description="Special rules that apply to the ganger.")]
    injuries: Annotated[List[Injury], Field(default_factory=list, description="Permanent injuries sustained.")]
    xp: Annotated[NonNegativeInt, Field(default=0, description="Experience points earned.")]
    x: Annotated[Optional[int], Field(default=None, description="X-coordinate on the battlefield.")]
    y: Annotated[Optional[int], Field(default=None, description="Y-coordinate on the battlefield.")]
    is_pinned: Annotated[bool, Field(default=False, description="Indicates if the fighter is pinned.")]
    is_out_of_action: Annotated[bool, Field(default=False, description="Indicates if the fighter is out of action.")]
    is_seriously_injured: Annotated[bool, Field(default=False, description="Indicates if the fighter is seriously injured.")]
    is_prone: Annotated[bool, Field(default=False, description="Indicates if the fighter is prone.")]
    status: Annotated[Optional[str], Field(default=None, description="Current status (e.g., 'Flesh Wound').")]
    # Added new attributes for combat system
    is_charging: Annotated[bool, Field(default=False, description="Indicates if the fighter is charging.")]
    has_moved: Annotated[bool, Field(default=False, description="Indicates if the fighter has moved this activation.")]
    elevation: Annotated[Optional[int], Field(default=0, description="Current elevation of the fighter.")]

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Crusher",
                    "gang_affiliation": "Goliath",
                    "role": "Leader",
                    "movement": 4,
                    "weapon_skill": 3,
                    "ballistic_skill": 4,
                    "strength": 4,
                    "toughness": 4,
                    "wounds": 2,
                    "initiative": 3,
                    "attacks": 2,
                    "leadership": 7,
                    "cool": 7,
                    "will": 7,
                    "intelligence": 6
                }
            ]
        }
    }


class Gang(BaseModel):
    """Represents a gang in Necromunda."""
    name: Annotated[str, Field(description="Name of the gang.")]
    type: Annotated[GangType, Field(description="The type of the gang.")]
    members: Annotated[List[Ganger], Field(description="List of gang members.")]
    credits: Annotated[NonNegativeInt, Field(default=1000, description="Amount of credits available.")]
    reputation: Annotated[NonNegativeInt, Field(default=0, description="Reputation score.")]
    territories: Annotated[List[str], Field(default_factory=list, description="Territories controlled by the gang.")]
    special_rules: Annotated[List[SpecialRule], Field(default_factory=list, description="Special rules for the gang.")]
    victory_points: Annotated[NonNegativeInt, Field(default=0, description="Victory points earned.")]
    vehicles: Annotated[List[Vehicle], Field(default_factory=list, description="Vehicles owned by the gang.")]

    @model_validator(mode='after')
    def validate_gang_composition(self) -> 'Gang':
        """Validate gang composition rules."""
        leaders = [m for m in self.members if m.role == GangerRole.LEADER]
        champions = [m for m in self.members if m.role == GangerRole.CHAMPION]

        if len(leaders) != 1:
            raise ValueError("Each gang must have exactly one Leader.")
        if len(champions) > 2:
            raise ValueError("A gang can have a maximum of two Champions.")
        return self

    model_config = {
        "arbitrary_types_allowed": True,
        "validate_assignment": True,
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Goliaths",
                    "type": GangType.GOLIATH,
                    "members": [],
                    "credits": 1000,
                    "reputation": 0,
                    "territories": [],
                    "special_rules": [],
                    "victory_points": 0,
                    "vehicles": []
                }
            ]
        }
    }

    def total_xp(self) -> int:
        """Calculate total experience points across all members."""
        return sum(member.xp for member in self.members)

    def add_member(self, ganger: Ganger):
        """Add a new ganger to the gang."""
        self.members.append(ganger)

    def remove_member(self, name: str):
        """Remove a ganger by name."""
        self.members = [member for member in self.members if member.name != name]