import logging
import d20
import random
from models import GameState, Gang, GangMember, Weapon, WeaponTrait, WeaponProfile, SpecialRule, Battlefield, Tile, ScenarioObjective, ArmorModel, Consumable, Equipment, Scenario, ScenarioDeploymentZone, ScenarioSpecialRule, CombatPhase, CombatRound
from database import Database
from typing import List, Dict, Optional, Tuple
from gang_builder import create_gang_member

class GameLogic:
    def __init__(self, db: Database):
        self.db = db
        self.game_state = self._initialize_game_state()
        self.active_fighter_index = 0
        logging.info("GameLogic initialized")

    def create_new_combat_round(self) -> None:
        """Create a new combat round and add it to the game state."""
        round_number = len(self.game_state.combat_rounds) + 1
        new_round = CombatRound(
            round_number=round_number,
            phases=[],
            special_rules=[],
            summary=""
        )
        self.game_state.combat_rounds.append(new_round)
        self._add_combat_phases(new_round)
        logging.info(f"Created new combat round: {round_number}")

    def _add_combat_phases(self, combat_round: CombatRound) -> None:
        """Add the standard combat phases to a combat round."""
        phases = [
            CombatPhase(
                name="Priority Phase",
                description="Determine which gang has priority for the round.",
                actions=["Roll-off", "Assign Priority"]
            ),
            CombatPhase(
                name="Movement Phase",
                description="Each fighter can move based on their movement characteristic.",
                actions=["Move", "Charge", "Retreat"]
            ),
            CombatPhase(
                name="Shooting Phase",
                description="Fighters with ready markers can shoot at enemies.",
                actions=["Shoot", "Aim"]
            ),
            CombatPhase(
                name="Close Combat Phase",
                description="Resolve close combat attacks for engaged fighters.",
                actions=["Melee Attack", "Fight Back"]
            ),
            CombatPhase(
                name="End Phase",
                description="Resolve any lingering effects and check for bottle tests.",
                actions=["Bottle Test", "Recovery Test", "Remove Ready Markers"]
            )
        ]
        combat_round.phases.extend(phases)

    def get_current_combat_round(self) -> Optional[CombatRound]:
        """Get the current combat round."""
        if self.game_state.combat_rounds:
            return self.game_state.combat_rounds[-1]
        return None

    def get_current_combat_phase(self) -> Optional[CombatPhase]:
        """Get the current combat phase."""
        current_round = self.get_current_combat_round()
        if current_round and current_round.phases:
            return current_round.phases[0]  # Assume the first phase is the current one
        return None

    def advance_combat_phase(self) -> None:
        """Advance to the next combat phase or create a new round if necessary."""
        current_round = self.get_current_combat_round()
        if current_round and current_round.phases:
            current_round.phases.pop(0)
            if not current_round.phases:
                self.create_new_combat_round()
        else:
            self.create_new_combat_round()

    def update_combat_round_summary(self, summary: str) -> None:
        """Update the summary of the current combat round."""
        current_round = self.get_current_combat_round()
        if current_round:
            current_round.summary = summary
            logging.info(f"Updated combat round {current_round.round_number} summary: {summary}")

    def add_special_rule_to_current_round(self, rule: str) -> None:
        """Add a special rule to the current combat round."""
        current_round = self.get_current_combat_round()
        if current_round:
            current_round.special_rules.append(rule)
            logging.info(f"Added special rule to combat round {current_round.round_number}: {rule}")

    def next_turn(self) -> None:
        self.active_fighter_index += 1
        if self.active_fighter_index >= len(self.get_active_gang().members):
            self.active_fighter_index = 0
            self.game_state.active_gang_index = (self.game_state.active_gang_index + 1) % len(self.game_state.gangs)
            if self.game_state.active_gang_index == 0:
                self.game_state.current_turn += 1
                self.check_scenario_objectives()
                self.apply_scenario_special_rules()
                self.advance_combat_phase()
        logging.info(f"Next turn: {self.game_state.current_turn}, Active gang: {self.get_active_gang().name}, Active fighter: {self.get_active_fighter().name}")

    def attack(self, attacker_name: str, target_name: str) -> str:
        result = super().attack(attacker_name, target_name)
        current_phase = self.get_current_combat_phase()
        if current_phase and current_phase.name in ["Shooting Phase", "Close Combat Phase"]:
            self.update_combat_round_summary(f"{result}")
        return result

    def move_fighter(self, fighter_name: str, x: int, y: int) -> bool:
        result = super().move_fighter(fighter_name, x, y)
        current_phase = self.get_current_combat_phase()
        if current_phase and current_phase.name == "Movement Phase":
            self.update_combat_round_summary(f"{fighter_name} moved to ({x}, {y})")
        return result

    def use_skill(self, fighter_name: str, skill_name: str) -> str:
        fighter = self._get_fighter_by_name(fighter_name)
        if not fighter:
            return f"Fighter {fighter_name} not found."
        
        if skill_name not in fighter.skills:
            return f"{fighter_name} does not have the skill {skill_name}."
        
        # Implement skill effects here. This is a placeholder implementation.
        effect = f"{fighter_name} used the skill {skill_name}."
        
        # Add specific skill effects based on the skill name
        if skill_name == "Nerves of Steel":
            effect += " They ignore the next Pinning test they would be required to take."
        elif skill_name == "Gunfighter":
            effect += " They can fire two pistol weapons in their next Shooting action without penalty."
        # Add more skill effects as needed
        
        current_phase = self.get_current_combat_phase()
        if current_phase:
            self.update_combat_round_summary(effect)
        
        return effect