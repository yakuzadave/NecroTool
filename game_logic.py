import logging
import d20
from typing import Optional, List, Dict, Any
from models import GameState, Gang, Ganger, CombatRound, CombatPhase, PhaseName, Scenario, Battlefield, Tile
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
        battlefield = Battlefield.generate_default(24, 24)  # Using the generate_default method from Battlefield.

        # Define gangs with improved attributes
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
                    y=0,
                    armor=None  # Placeholder until armor is added
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
                    y=23,
                    armor=None  # Placeholder until armor is added
                )
            ]
        )

        return GameState(
            gangs=[goliaths, eschers],
            battlefield=battlefield,
            current_turn=1,
            active_gang_index=0,
            max_turns=10,
            scenario=None
        )

    def create_new_combat_round(self) -> None:
        new_round = CombatRound(
            round_number=len(self.game_state.combat_rounds) + 1,
            phases=[
                CombatPhase(name=PhaseName.PRIORITY, description="Determine which gang has priority for the round."),
                CombatPhase(name=PhaseName.MOVEMENT, description="Each fighter can move based on their movement characteristic."),
                CombatPhase(name=PhaseName.SHOOTING, description="Fighters can shoot at enemies if eligible."),
                CombatPhase(name=PhaseName.CLOSE_COMBAT, description="Resolve close combat attacks."),
                CombatPhase(name=PhaseName.END, description="Resolve bottle tests and lingering effects.")
            ]
        )
        self.game_state.combat_rounds.append(new_round)
        logging.info(f"Created new combat round: {new_round.round_number}")

    def get_battlefield_state(self) -> str:
        return self.game_state.battlefield.render()

    def move_fighter(self, fighter_name: str, x: int, y: int) -> bool:
        fighter = self._get_fighter_by_name(fighter_name)
        if not fighter:
            logging.error(f"Fighter {fighter_name} not found.")
            return False

        if not (0 <= x < self.game_state.battlefield.width and 0 <= y < self.game_state.battlefield.height):
            logging.error(f"Invalid move for {fighter_name} to ({x}, {y}). Out of bounds.")
            return False

        distance = abs(fighter.x - x) + abs(fighter.y - y)
        if distance > fighter.movement:
            logging.error(f"{fighter_name} cannot move {distance} spaces; maximum movement is {fighter.movement}.")
            return False

        fighter.x = x
        fighter.y = y
        logging.info(f"{fighter_name} moved to ({x}, {y}).")
        return True

    def end_fighter_activation(self) -> str:
        active_gang = self.get_active_gang()
        self.active_fighter_index += 1
        if self.active_fighter_index >= len(active_gang.members):
            self.active_fighter_index = 0
            self.game_state.active_gang_index = (self.game_state.active_gang_index + 1) % len(self.game_state.gangs)

        new_active_gang = self.get_active_gang()
        new_active_fighter = self.get_active_fighter()
        return f"Activation ended. Active gang: {new_active_gang.name}, Active fighter: {new_active_fighter.name}"

    def advance_combat_phase(self) -> None:
        current_round = self.get_current_combat_round()
        if current_round and current_round.phases:
            current_phase = current_round.phases.pop(0)
            logging.info(f"Advanced from phase: {current_phase.name}")
            if not current_round.phases:
                self.create_new_combat_round()
            else:
                next_phase = self.get_current_combat_phase()
                logging.info(f"Next phase: {next_phase.name}" if next_phase else "No more phases.")

    def get_scenario(self) -> Optional[Scenario]:
        return self.game_state.scenario

    def calculate_victory_points(self) -> List[Dict[str, Any]]:
        return [{"gang": gang.name, "victory_points": gang.victory_points} for gang in self.game_state.gangs]

    def _get_fighter_by_name(self, name: str) -> Optional[Ganger]:
        for gang in self.game_state.gangs:
            for fighter in gang.members:
                if fighter.name.lower() == name.lower():
                    return fighter
        return None
