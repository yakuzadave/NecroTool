from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class WeaponTrait(BaseModel):
    name: str = Field(..., description="The name of the weapon trait (e.g., Rapid Fire, Knockback, Unwieldy).")
    description: Optional[str] = Field(None, description="A description of the trait and its effect on the weapon or ganger.")

class WeaponProfile(BaseModel):
    range: str = Field(..., description="The range of the weapon, e.g., 'Short: 0-8', 'Long: 8-24'.")
    strength: int = Field(..., description="The strength value of the weapon.")
    armor_penetration: int = Field(..., description="The armor penetration value of the weapon.")
    damage: int = Field(..., description="The damage dealt by the weapon when it successfully wounds.")
    ammo_roll: Optional[str] = Field(None, description="The ammo roll required to avoid running out of ammo, e.g., '4+'.")
    special_rules: Optional[List[str]] = Field(None, description="Any special rules associated with this profile.")

class Weapon(BaseModel):
    name: str = Field(..., description="The name of the weapon, e.g., Lasgun, Bolt Pistol.")
    weapon_type: str = Field(..., description="The type of the weapon, e.g., Basic, Pistol, Heavy, Melee.")
    cost: Optional[int] = Field(None, description="The credit cost of the weapon, used for gang management purposes.")
    rarity: Optional[str] = Field(None, description="The rarity level of the weapon, used to determine availability in trading post.")
    traits: Optional[List[WeaponTrait]] = Field(None, description="Traits or special abilities associated with the weapon.")
    profiles: List[WeaponProfile] = Field(..., description="List of weapon profiles representing different firing modes or melee stats.")
    is_unwieldy: Optional[bool] = Field(False, description="Indicates whether the weapon is unwieldy, adding penalties to movement or attack.")
    description: Optional[str] = Field(None, description="A detailed description of the weapon, including lore or fluff.")

class Consumable(BaseModel):
    name: str = Field(..., description="The name of the consumable item, e.g., Stimm-Slug Stash, Medipack.")
    cost: Optional[int] = Field(None, description="The credit cost of the consumable item.")
    rarity: Optional[str] = Field(None, description="The rarity level of the consumable, used to determine availability in trading post.")
    uses: int = Field(..., ge=1, description="The number of uses the consumable item has.")
    effect: str = Field(..., description="The effect or benefit provided by the consumable item.")
    side_effects: Optional[str] = Field(None, description="Any negative side effects of using the consumable item.")
    description: Optional[str] = Field(None, description="A detailed description of the consumable, including lore or fluff.")

class Equipment(BaseModel):
    name: str = Field(..., description="The name of the equipment, e.g., Grapnel Launcher, Photo-Visor.")
    cost: Optional[int] = Field(None, description="The credit cost of the equipment item.")
    rarity: Optional[str] = Field(None, description="The rarity level of the equipment, used to determine availability in trading post.")
    weight: Optional[str] = Field(None, description="The weight category of the equipment, e.g., Light, Medium, Heavy.")
    special_rules: Optional[List[str]] = Field(None, description="Special rules or abilities provided by the equipment.")
    modifiers: Optional[List[str]] = Field(None, description="Stat modifiers provided by the equipment, e.g., +1 to Strength.")
    is_restricted: Optional[bool] = Field(False, description="Indicates whether the equipment is restricted and requires special permission to use.")
    description: Optional[str] = Field(None, description="A detailed description of the equipment, including lore or fluff.")

class SpecialRule(BaseModel):
    name: str
    description: str
    effect: str

class ArmorModel(BaseModel):
    name: str = Field(..., description="Name of the armor")
    protection_value: int = Field(..., ge=0, le=6, description="Protection value of the armor, between 0 and 6")
    locations: List[str] = Field(..., description="Body locations covered by the armor")
    special_rules: List[str] = Field(default_factory=list, description="Special rules associated with the armor")

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
    consumables: List[Consumable] = Field(default_factory=list, description="List of consumables carried by the gang member")
    skills: List[str] = Field(default_factory=list, description="List of skills the gang member possesses (e.g., Nerves of Steel, Combat Master)")
    special_rules: List[SpecialRule] = Field(default_factory=list, description="List of special rules that apply to the gang member")
    injuries: List[str] = Field(default_factory=list, description="List of permanent injuries sustained by the gang member")
    xp: int = Field(0, description="Experience points earned by the gang member")
    armor: Optional[ArmorModel] = Field(None, description="Armor worn by the gang member")

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

class ScenarioObjective(BaseModel):
    name: str = Field(..., description="The name of the objective, e.g., Capture the Flag, Defend the Territory.")
    description: Optional[str] = Field(None, description="A detailed description of the objective and how it impacts gameplay.")
    rewards: Optional[str] = Field(None, description="Rewards for completing the objective, such as credits or reputation.")
    completed: bool = Field(False, description="Indicates whether the objective has been completed.")
    points: int = Field(0, description="Victory points awarded for completing this objective.")

class ScenarioDeploymentZone(BaseModel):
    name: str = Field(..., description="The name of the deployment zone, e.g., Zone A, Northern Sector.")
    description: Optional[str] = Field(None, description="A detailed description of the deployment zone.")
    starting_positions: Optional[str] = Field(None, description="Information about starting positions for each gang.")

class ScenarioSpecialRule(BaseModel):
    name: str = Field(..., description="The name of the special rule, e.g., Toxic Fog, Reinforcements.")
    effect: Optional[str] = Field(None, description="A description of the effect the special rule has on the scenario.")

class Scenario(BaseModel):
    name: str = Field(..., description="The name of the scenario, e.g., Ambush, Turf War.")
    description: Optional[str] = Field(None, description="A detailed description of the scenario, including lore or fluff.")
    objectives: List[ScenarioObjective] = Field(..., description="List of objectives that gangs must accomplish during the scenario.")
    deployment_zones: List[ScenarioDeploymentZone] = Field(..., description="List of deployment zones available in the scenario.")
    special_rules: Optional[List[ScenarioSpecialRule]] = Field(None, description="List of special rules that modify how the scenario is played.")
    max_gangs: Optional[int] = Field(2, description="The maximum number of gangs that can participate in the scenario.")
    duration: Optional[str] = Field(None, description="The expected duration of the scenario, e.g., '3-5 turns' or 'Until all objectives are completed'.")
    rewards: Optional[str] = Field(None, description="General rewards for winning the scenario, e.g., credits, territory, reputation.")

class CombatPhase(BaseModel):
    name: str = Field(..., description="The name of the phase, e.g., Priority Phase, Movement Phase, Shooting Phase.")
    description: Optional[str] = Field(None, description="A detailed description of what happens during this phase.")
    actions: Optional[List[str]] = Field(None, description="List of actions that can be taken during this phase, e.g., Move, Shoot, Charge.")

class CombatRound(BaseModel):
    round_number: int = Field(..., ge=1, description="The number of the combat round, starting from 1.")
    phases: List[CombatPhase] = Field(..., description="List of phases that occur in this round of combat.")
    special_rules: Optional[List[str]] = Field(None, description="Special rules or events that are specific to this round.")
    summary: Optional[str] = Field(None, description="A summary of key events that took place during this round.")

class GameState(BaseModel):
    gangs: List[Gang]
    battlefield: Battlefield
    current_turn: int = 1
    active_gang_index: int = 0
    scenario: Optional[Scenario] = Field(None, description="The current scenario being played")
    max_turns: int = Field(10, description="Maximum number of turns for the game")
    combat_rounds: List[CombatRound] = Field(default_factory=list, description="List of combat rounds in the game")