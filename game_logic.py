import logging
import d20
import random
from models import GameState, Gang, Ganger, Weapon, WeaponProfile, CombatRound, CombatPhase, PhaseName, Scenario, ScenarioObjective, Battlefield, Tile, Consumable, Equipment
from typing import List, Optional, Dict, Union, Any
from database import Database
from rich.table import Table
import contextlib

class GameLogic:
    def __init__(self, db: Database):
        self.db = db
        self.d20 = d20  # Initialize d20 as an attribute
        self.game_state = self._initialize_game_state()
        self.active_fighter_index = 0
        self.create_new_combat_round()  # Initialize the first combat round
        logging.info("GameLogic initialized")

    def _initialize_game_state(self) -> GameState:
        # Create initial battlefield
        battlefield = Battlefield(
            width=24,
            height=24,
            tiles=[Tile(x=x, y=y, type='open') for x in range(24) for y in range(24)]
        )
        
        # Create initial gangs
        goliaths = Gang(
            name="Goliaths",
            members=[
                Ganger(
                    name="Crusher",
                    gang_affiliation="Goliaths",
                    role="Leader",
                    movement=4,
                    weapon_skill=3,
                    ballistic_skill=4,
                    strength=4,
                    toughness=4,
                    wounds=2,
                    initiative=3,
                    attacks=2,
                    leadership=7,
                    cool=7,
                    will=7,
                    intelligence=6,
                    x=0,
                    y=0
                )
            ]
        )
        
        eschers = Gang(
            name="Eschers",
            members=[
                Ganger(
                    name="Venom",
                    gang_affiliation="Eschers",
                    role="Leader",
                    movement=5,
                    weapon_skill=3,
                    ballistic_skill=3,
                    strength=3,
                    toughness=3,
                    wounds=2,
                    initiative=4,
                    attacks=2,
                    leadership=7,
                    cool=7,
                    will=8,
                    intelligence=7,
                    x=23,
                    y=23
                )
            ]
        )
        
        # Return initialized game state
        return GameState(
            gangs=[goliaths, eschers],
            battlefield=battlefield,
            current_turn=1,
            active_gang_index=0,
            max_turns=10
        )

    def create_new_combat_round(self) -> None:
        """Create a new combat round and add it to the game state."""
        new_round = CombatRound(
            round_number=len(self.game_state.combat_rounds) + 1,
            phases=[
                CombatPhase(name=str(PhaseName.PRIORITY), description="Determine which gang has priority for the round.", actions=["Roll-off", "Assign Priority"]),
                CombatPhase(name=str(PhaseName.MOVEMENT), description="Each fighter can move based on their movement characteristic.", actions=["Move", "Charge", "Retreat"]),
                CombatPhase(name=str(PhaseName.SHOOTING), description="Fighters with ready markers can shoot at enemies.", actions=["Shoot", "Aim"]),
                CombatPhase(name=str(PhaseName.CLOSE_COMBAT), description="Resolve close combat attacks for engaged fighters.", actions=["Melee Attack", "Fight Back"]),
                CombatPhase(name=str(PhaseName.END), description="Resolve any lingering effects and check for bottle tests.", actions=["Bottle Test", "Recovery Test", "Remove Ready Markers"])
            ],
            special_rules=[],
            summary=""
        )
        self.game_state.combat_rounds.append(new_round)
        logging.info(f"Created new combat round: {new_round.round_number}")

    def resolve_combat(self, attacker: Ganger, defender: Ganger) -> str:
        """Resolve combat between two fighters."""
        attack_roll = self.d20.roll("1d6").total
        if attack_roll >= attacker.weapon_skill:
            # Hit successful
            weapon = attacker.weapons[0] if attacker.weapons else None
            if weapon:
                strength = weapon.profiles[0].strength if weapon.profiles else attacker.strength
                damage = weapon.profiles[0].damage if weapon.profiles else 1
            else:
                strength = attacker.strength
                damage = 1

            wound_roll = self.d20.roll("1d6").total
            if wound_roll >= defender.toughness:
                # Wound successful
                actual_damage = self._apply_damage(defender, damage)
                return f"{attacker.name} hit and wounded {defender.name} for {actual_damage} damage!"
            else:
                return f"{attacker.name} hit but failed to wound {defender.name}."
        else:
            return f"{attacker.name} missed {defender.name}."

    def _apply_damage(self, target: Ganger, damage: int) -> int:
        if target.armor:
            armor_save = self.d20.roll("1d6").total
            if armor_save >= target.armor.armor_rating:
                damage = max(0, damage - 1)
        
        target.wounds -= damage
        if target.wounds <= 0:
            target.is_out_of_action = True
            target.status = "Out of Action"
        elif target.wounds <= 1:
            target.is_seriously_injured = True
            target.status = "Seriously Injured"
        
        return damage

    def get_active_gang(self) -> Gang:
        return self.game_state.gangs[self.game_state.active_gang_index]

    def get_active_fighter(self) -> Ganger:
        active_gang = self.get_active_gang()
        return active_gang.members[self.active_fighter_index]

    def end_fighter_activation(self) -> str:
        active_gang = self.get_active_gang()
        self.active_fighter_index += 1
        if self.active_fighter_index >= len(active_gang.members):
            self.active_fighter_index = 0
            self.game_state.active_gang_index = (self.game_state.active_gang_index + 1) % len(self.game_state.gangs)
        
        new_active_gang = self.get_active_gang()
        new_active_fighter = self.get_active_fighter()
        return f"Activation ended. Active gang: {new_active_gang.name}, Active fighter: {new_active_fighter.name}"

    def _get_fighter_by_name(self, name: str) -> Optional[Ganger]:
        for gang in self.game_state.gangs:
            for fighter in gang.members:
                if fighter.name.lower() == name.lower():
                    return fighter
        return None

    def attack(self, attacker_name: str, target_name: str) -> str:
        attacker = self._get_fighter_by_name(attacker_name)
        target = self._get_fighter_by_name(target_name)
        
        if not attacker or not target:
            return "Invalid attacker or target name."
        
        return self.resolve_combat(attacker, target)

    def get_current_combat_round(self) -> Optional[CombatRound]:
        if self.game_state.combat_rounds:
            return self.game_state.combat_rounds[-1]
        return None

    def get_current_combat_phase(self) -> Optional[CombatPhase]:
        current_round = self.get_current_combat_round()
        if current_round and current_round.phases:
            return current_round.phases[0]  # Assume the first phase is the current one
        return None

    def advance_combat_phase(self) -> None:
        current_round = self.get_current_combat_round()
        if current_round and current_round.phases:
            current_round.phases.pop(0)
            if not current_round.phases:
                self.create_new_combat_round()
                
            current_phase = self.get_current_combat_phase()
            if current_phase:
                logging.info(f"Advanced to next phase: {current_phase.name}")

    def move_fighter(self, fighter_name: str, x: int, y: int) -> bool:
        """Move a fighter to new coordinates."""
        fighter = self._get_fighter_by_name(fighter_name)
        if not fighter:
            return False
        
        if not (0 <= x < self.game_state.battlefield.width and 0 <= y < self.game_state.battlefield.height):
            return False
        
        if abs(fighter.x - x) + abs(fighter.y - y) > fighter.movement:
            return False
        
        fighter.x = x
        fighter.y = y
        return True

    def get_battlefield_state(self) -> str:
        """Get a string representation of the current battlefield state."""
        battlefield = self.game_state.battlefield
        state = ""
        for y in range(battlefield.height):
            for x in range(battlefield.width):
                # Check if there's a fighter at this position
                fighter_here = None
                for gang in self.game_state.gangs:
                    for fighter in gang.members:
                        if fighter.x == x and fighter.y == y:
                            fighter_here = fighter
                            break
                    if fighter_here:
                        break
                
                if fighter_here:
                    state += fighter_here.name[0]  # First letter of fighter's name
                else:
                    tile = next((t for t in battlefield.tiles if t.x == x and t.y == y), None)
                    if tile:
                        if tile.type == "open":
                            state += "."
                        elif tile.type == "cover":
                            state += "#"
                        else:
                            state += str(tile.elevation)
                    else:
                        state += " "
            state += "\n"
        return state

    def calculate_victory_points(self) -> List[Dict[str, Union[str, int]]]:
        """Calculate and return victory points for each gang."""
        results = []
        for gang in self.game_state.gangs:
            points = gang.victory_points
            
            # Add points for surviving fighters
            for fighter in gang.members:
                if not fighter.is_out_of_action:
                    points += 1
                    if fighter.role == "Leader":
                        points += 2
            
            results.append({
                "gang": gang.name,
                "victory_points": points
            })
        return results

    def get_scenario(self) -> Optional[Scenario]:
        """Get the current scenario."""
        return self.game_state.scenario

    def check_scenario_objectives(self) -> None:
        """Check and update scenario objectives."""
        if not self.game_state.scenario:
            return
        
        for objective in self.game_state.scenario.objectives:
            if not objective.completed:
                # Check each objective condition
                if objective.name == "Control Central Zone":
                    # Count fighters in central zone for each gang
                    gang_counts = {gang.name: 0 for gang in self.game_state.gangs}
                    central_x_range = (self.game_state.battlefield.width // 2 - 2, self.game_state.battlefield.width // 2 + 2)
                    central_y_range = (self.game_state.battlefield.height // 2 - 2, self.game_state.battlefield.height // 2 + 2)
                    
                    for gang in self.game_state.gangs:
                        for fighter in gang.members:
                            if (central_x_range[0] <= fighter.x <= central_x_range[1] and 
                                central_y_range[0] <= fighter.y <= central_y_range[1] and
                                not fighter.is_out_of_action):
                                gang_counts[gang.name] += 1
                    
                    # Find gang with most fighters in zone
                    max_count = max(gang_counts.values())
                    winning_gangs = [gang for gang, count in gang_counts.items() if count == max_count]
                    if len(winning_gangs) == 1:  # Clear winner
                        objective.completed = True
                        # Award points to winning gang
                        for gang in self.game_state.gangs:
                            if gang.name == winning_gangs[0]:
                                gang.victory_points += objective.points
                
                elif objective.name == "Eliminate Enemy Leader":
                    # Check if any gang's leader is out of action
                    for gang in self.game_state.gangs:
                        leader = next((f for f in gang.members if f.role == "Leader"), None)
                        if leader and leader.is_out_of_action:
                            objective.completed = True
                            # Award points to the gang that eliminated the leader
                            opposing_gang = next((g for g in self.game_state.gangs if g != gang), None)
                            if opposing_gang:
                                opposing_gang.victory_points += objective.points
