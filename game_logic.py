import logging
import d20
import random
from models import GameState, Gang, Ganger, Weapon, WeaponProfile, CombatRound, CombatPhase, PhaseName, Scenario, ScenarioObjective, Battlefield, Tile
from typing import List, Optional, Dict, Union
from database import Database

class GameLogic:
    def __init__(self, db: Database):
        self.db = db
        self.game_state = self._initialize_game_state()
        self.active_fighter_index = 0
        self.create_new_combat_round()  # Initialize the first combat round
        logging.info("GameLogic initialized")

    def _initialize_game_state(self) -> GameState:
        gangs = [
            Gang(name="Goliaths", members=[
                Ganger(name="Crusher", gang_affiliation="Goliaths", role="Leader", movement=4, weapon_skill=3, ballistic_skill=4, strength=4, toughness=4, wounds=2, initiative=3, attacks=2, leadership=7, cool=7, will=7, intelligence=6,
                       weapons=[Weapon(name="Power Hammer", weapon_type="Melee", profiles=[WeaponProfile(range="Melee", strength=5, armor_penetration=-2, damage=2, ammo_roll=None)])])
            ]),
            Gang(name="Eschers", members=[
                Ganger(name="Venom", gang_affiliation="Eschers", role="Leader", movement=5, weapon_skill=3, ballistic_skill=3, strength=3, toughness=3, wounds=1, initiative=4, attacks=1, leadership=7, cool=8, will=8, intelligence=7,
                       weapons=[Weapon(name="Stiletto Knife", weapon_type="Melee", profiles=[WeaponProfile(range="Melee", strength=3, armor_penetration=-1, damage=1, ammo_roll=None)])])
            ])
        ]
        battlefield = Battlefield(width=20, height=20, tiles=[Tile(x=x, y=y, type='open') for x in range(20) for y in range(20)])
        scenario = Scenario(
            name="Test Scenario",
            description="A test scenario for the Necromunda simulation",
            objectives=[
                ScenarioObjective(name="Capture Territory", description="Capture and hold the central territory", points=3),
                ScenarioObjective(name="Eliminate Enemy Leader", description="Take out the enemy gang's leader", points=5)
            ],
            deployment_zones=[],
            duration="6 rounds",
            rewards="100 credits"
        )
        return GameState(gangs=gangs, battlefield=battlefield, scenario=scenario)

    def create_new_combat_round(self) -> None:
        round_number = len(self.game_state.combat_rounds) + 1
        phases = [
            CombatPhase(
                name=PhaseName.PRIORITY.value,
                description="Determine which gang has priority for the round.",
                actions=["Roll-off", "Assign Priority"]
            ),
            CombatPhase(
                name=PhaseName.MOVEMENT.value,
                description="Each fighter can move based on their movement characteristic.",
                actions=["Move", "Charge", "Retreat"]
            ),
            CombatPhase(
                name=PhaseName.SHOOTING.value,
                description="Fighters with ready markers can shoot at enemies.",
                actions=["Shoot", "Aim"]
            ),
            CombatPhase(
                name=PhaseName.CLOSE_COMBAT.value,
                description="Resolve close combat attacks for engaged fighters.",
                actions=["Melee Attack", "Fight Back"]
            ),
            CombatPhase(
                name=PhaseName.END.value,
                description="Resolve any lingering effects and check for bottle tests.",
                actions=["Bottle Test", "Recovery Test", "Remove Ready Markers"]
            )
        ]
        new_round = CombatRound(round_number=round_number, phases=phases)
        self.game_state.combat_rounds.append(new_round)
        logging.info(f"Created new combat round: {round_number}")

    def get_current_combat_round(self) -> Optional[CombatRound]:
        if self.game_state.combat_rounds:
            return self.game_state.combat_rounds[-1]
        return None

    def get_current_combat_phase(self) -> Optional[CombatPhase]:
        current_round = self.get_current_combat_round()
        if current_round and current_round.phases:
            return current_round.phases[0]
        return None

    def advance_combat_phase(self) -> None:
        current_round = self.get_current_combat_round()
        if current_round:
            if len(current_round.phases) > 1:
                current_round.phases.pop(0)
                logging.info(f"Advanced to next phase: {current_round.phases[0].name}")
            else:
                self.create_new_combat_round()
                logging.info("Advanced to new combat round")
        else:
            self.create_new_combat_round()
            logging.info("Created first combat round")

    def attack(self, attacker_name: str, target_name: str) -> str:
        attacker = self._get_fighter_by_name(attacker_name)
        target = self._get_fighter_by_name(target_name)
        
        if not attacker or not target:
            return "Invalid attacker or target name."
        
        if not attacker.weapons:
            return f"{attacker.name} has no weapons to attack with."
        
        weapon = attacker.weapons[0]
        
        hit_roll = d20.roll("1d6").total
        if hit_roll >= attacker.ballistic_skill:
            damage = self.apply_damage(target, weapon.profiles[0].damage)
            return f"{attacker.name} hit {target.name} with {weapon.name} for {damage} damage."
        else:
            return f"{attacker.name} missed {target.name} with {weapon.name}."

    def _get_fighter_by_name(self, name: str) -> Optional[Ganger]:
        for gang in self.game_state.gangs:
            for fighter in gang.members:
                if fighter.name == name:
                    return fighter
        return None

    def apply_damage(self, fighter: Ganger, damage: int) -> int:
        actual_damage = min(damage, fighter.wounds)
        fighter.wounds -= actual_damage
        if fighter.wounds <= 0:
            fighter.is_out_of_action = True
            fighter.status = "Out of Action"
        return actual_damage

    def get_active_gang(self) -> Gang:
        return self.game_state.gangs[self.game_state.active_gang_index]

    def get_active_fighter(self) -> Ganger:
        active_gang = self.get_active_gang()
        return active_gang.members[self.active_fighter_index]

    def end_fighter_activation(self) -> str:
        active_gang = self.get_active_gang()
        self.active_fighter_index = (self.active_fighter_index + 1) % len(active_gang.members)
        
        if self.active_fighter_index == 0:
            self.game_state.active_gang_index = (self.game_state.active_gang_index + 1) % len(self.game_state.gangs)
        
        new_active_gang = self.get_active_gang()
        new_active_fighter = self.get_active_fighter()
        
        return f"Activation ended. Active gang: {new_active_gang.name}, Active fighter: {new_active_fighter.name}"