import logging
import d20
import random
from models import GameState, Gang, Ganger, CombatRound, CombatPhase, PhaseName, Scenario, Battlefield, Tile
from typing import Optional, List, Dict, Any
from database import Database

class GameLogic:
    def __init__(self, db: Database):
        self.db = db
        self.d20 = d20
        self.game_state = self._initialize_game_state()
        self.active_fighter_index = 0
        self.create_new_combat_round()
        logging.info("GameLogic initialized")

    def _initialize_game_state(self) -> GameState:
        battlefield = Battlefield(
            width=24,
            height=24,
            tiles=[Tile(x=x, y=y, type='open') for x in range(24) for y in range(24)]
        )
        
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
        
        return GameState(
            gangs=[goliaths, eschers],
            battlefield=battlefield,
            current_turn=1,
            active_gang_index=0,
            max_turns=10
        )

    def create_new_combat_round(self) -> None:
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

    def get_battlefield_state(self) -> str:
        battlefield = self.game_state.battlefield
        state = []
        
        for y in range(battlefield.height):
            row = []
            for x in range(battlefield.width):
                fighter_here = None
                for gang in self.game_state.gangs:
                    for fighter in gang.members:
                        if fighter.x == x and fighter.y == y:
                            fighter_here = fighter
                            break
                    if fighter_here:
                        break
                
                if fighter_here:
                    row.append(fighter_here.name[0])
                else:
                    tile = next((t for t in battlefield.tiles if t.x == x and t.y == y), None)
                    if tile:
                        if tile.type == "open":
                            row.append(".")
                        elif tile.type == "cover":
                            row.append("#")
                        else:
                            row.append(str(tile.elevation))
                    else:
                        row.append(" ")
            state.append("".join(row))
        
        return "\n".join(state)

    def move_fighter(self, fighter_name: str, x: int, y: int) -> bool:
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
        if current_round and current_round.phases:
            current_round.phases.pop(0)
            if not current_round.phases:
                self.create_new_combat_round()
            
            current_phase = self.get_current_combat_phase()
            if current_phase:
                logging.info(f"Advanced to next phase: {current_phase.name}")

    def get_scenario(self) -> Optional[Scenario]:
        return self.game_state.scenario

    def calculate_victory_points(self) -> List[Dict[str, Any]]:
        results = []
        for gang in self.game_state.gangs:
            results.append({
                "gang": gang.name,
                "victory_points": gang.victory_points
            })
        return results

    def check_scenario_objectives(self) -> None:
        scenario = self.get_scenario()
        if not scenario:
            return
            
        for objective in scenario.objectives:
            if not objective.completed:
                if objective.name == "Control Central Zone":
                    gang_counts = {gang.name: 0 for gang in self.game_state.gangs}
                    central_x_range = (self.game_state.battlefield.width // 2 - 2, self.game_state.battlefield.width // 2 + 2)
                    central_y_range = (self.game_state.battlefield.height // 2 - 2, self.game_state.battlefield.height // 2 + 2)
                    
                    for gang in self.game_state.gangs:
                        for fighter in gang.members:
                            if (central_x_range[0] <= fighter.x <= central_x_range[1] and 
                                central_y_range[0] <= fighter.y <= central_y_range[1] and
                                not fighter.is_out_of_action):
                                gang_counts[gang.name] += 1
                    
                    max_count = max(gang_counts.values())
                    winning_gangs = [gang for gang, count in gang_counts.items() if count == max_count]
                    if len(winning_gangs) == 1:
                        objective.completed = True
                        for gang in self.game_state.gangs:
                            if gang.name == winning_gangs[0]:
                                gang.victory_points += objective.points
                
                elif objective.name == "Eliminate Enemy Leader":
                    for gang in self.game_state.gangs:
                        leader = next((f for f in gang.members if f.role == "Leader"), None)
                        if leader and leader.is_out_of_action:
                            objective.completed = True
                            opposing_gang = next((g for g in self.game_state.gangs if g != gang), None)
                            if opposing_gang:
                                opposing_gang.victory_points += objective.points
