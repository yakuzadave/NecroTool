import logging
import d20
from models import GameState, Gang, GangMember, Weapon, SpecialRule, Battlefield, Tile, MissionObjective
from database import Database
from typing import List, Dict, Optional, Tuple

class GameLogic:
    """
    Manages the game logic for the Necromunda simulation.
    """

    def __init__(self, db: Database):
        """
        Initialize the GameLogic instance.

        Args:
            db (Database): The database instance for saving and loading game states.
        """
        self.db = db
        self.game_state = self._initialize_game_state()
        self.active_fighter_index = 0
        logging.info("GameLogic initialized")

    def _initialize_game_state(self) -> GameState:
        """
        Initialize or load the game state.

        Returns:
            GameState: The initialized or loaded game state.
        """
        saved_state = self.db.load_game_state()
        if saved_state:
            logging.info("Loaded saved game state")
            return GameState(**saved_state)
        else:
            logging.info("Creating new game state")
            return self._create_new_game_state()

    def _create_new_game_state(self) -> GameState:
        """
        Create a new game state with initial gangs, battlefield, and mission objectives.

        Returns:
            GameState: The newly created game state.
        """
        gang1 = self._create_goliath_gang()
        gang2 = self._create_escher_gang()
        battlefield = self._create_battlefield()
        mission_objectives = self._create_mission_objectives()

        return GameState(gangs=[gang1, gang2], battlefield=battlefield, mission_objectives=mission_objectives)

    def _create_goliath_gang(self) -> Gang:
        """Create and return the Goliath gang."""
        return Gang(name="Goliaths", members=[
            self._create_goliath_champion(),
            self._create_goliath_ganger()
        ])

    def _create_escher_gang(self) -> Gang:
        """Create and return the Escher gang."""
        return Gang(name="Escher", members=[
            self._create_escher_champion(),
            self._create_escher_ganger()
        ])

    def _create_goliath_champion(self) -> GangMember:
        """Create and return a Goliath champion."""
        return GangMember(
            name="Crusher", gang="Goliaths", role="Champion",
            movement=4, weapon_skill=3, ballistic_skill=4, strength=4, toughness=4,
            wounds=2, initiative=2, attacks=1, leadership=7, cool=7, willpower=7, intelligence=6,
            credits_value=120, outlaw=False,
            weapons=[
                Weapon(name="Combat Shotgun", range="S:8\", L:16\"", strength=4, armor_penetration=0, damage=1, ammo="4+", traits=["Blast (3)", "Knockback"])
            ],
            equipment=[],
            skills=["Nerves of Steel"],
            special_rules=[SpecialRule(name="Unstoppable", description="This fighter may ignore Flesh Wounds when making Injury rolls.", effect="Ignore Flesh Wounds on Injury rolls")],
            xp=0
        )

    def _create_goliath_ganger(self) -> GangMember:
        """Create and return a Goliath ganger."""
        return GangMember(
            name="Smasher", gang="Goliaths", role="Ganger",
            movement=4, weapon_skill=3, ballistic_skill=4, strength=4, toughness=4,
            wounds=1, initiative=2, attacks=1, leadership=6, cool=6, willpower=6, intelligence=6,
            credits_value=80, outlaw=False,
            weapons=[
                Weapon(name="Fighting Knife", range="Melee", strength=3, armor_penetration=0, damage=1, ammo="N/A", traits=["Melee"])
            ],
            equipment=[],
            skills=[],
            special_rules=[],
            xp=0
        )

    def _create_escher_champion(self) -> GangMember:
        """Create and return an Escher champion."""
        return GangMember(
            name="Venom", gang="Escher", role="Champion",
            movement=5, weapon_skill=3, ballistic_skill=3, strength=3, toughness=3,
            wounds=1, initiative=4, attacks=1, leadership=7, cool=8, willpower=7, intelligence=7,
            credits_value=100, outlaw=False,
            weapons=[
                Weapon(name="Lasgun", range="S:12\", L:24\"", strength=3, armor_penetration=0, damage=1, ammo="6+", traits=[])
            ],
            equipment=[],
            skills=["Catfall"],
            special_rules=[SpecialRule(name="Agile", description="This fighter is exceptionally agile.", effect="Improve Dodge rolls")],
            xp=0
        )

    def _create_escher_ganger(self) -> GangMember:
        """Create and return an Escher ganger."""
        return GangMember(
            name="Shadow", gang="Escher", role="Ganger",
            movement=5, weapon_skill=3, ballistic_skill=3, strength=3, toughness=3,
            wounds=1, initiative=4, attacks=1, leadership=6, cool=7, willpower=7, intelligence=7,
            credits_value=70, outlaw=False,
            weapons=[
                Weapon(name="Stiletto Knife", range="Melee", strength=3, armor_penetration=-1, damage=1, ammo="N/A", traits=["Melee", "Toxin"])
            ],
            equipment=[],
            skills=[],
            special_rules=[],
            xp=0
        )

    def _create_battlefield(self) -> Battlefield:
        """Create and return the battlefield."""
        battlefield = Battlefield(width=10, height=10, tiles=[
            Tile(x=x, y=y, type="open") for x in range(10) for y in range(10)
        ])

        self._add_cover_to_battlefield(battlefield)
        self._add_elevation_to_battlefield(battlefield)

        return battlefield

    def _add_cover_to_battlefield(self, battlefield: Battlefield) -> None:
        """Add cover tiles to the battlefield."""
        for _ in range(5):
            x, y = d20.roll("1d10-1").total, d20.roll("1d10-1").total
            battlefield.tiles[y * 10 + x].type = "cover"

    def _add_elevation_to_battlefield(self, battlefield: Battlefield) -> None:
        """Add elevation tiles to the battlefield."""
        for _ in range(3):
            x, y = d20.roll("1d10-1").total, d20.roll("1d10-1").total
            battlefield.tiles[y * 10 + x].type = "elevation"
            battlefield.tiles[y * 10 + x].elevation = d20.roll("1d2").total

    def _create_mission_objectives(self) -> List[MissionObjective]:
        """Create and return the list of mission objectives."""
        return [
            MissionObjective(name="Claim Territory", description="Control the most terrain at the end of the game", points=3),
            MissionObjective(name="Assassinate Leader", description="Take out the enemy gang's leader", points=5),
            MissionObjective(name="Scavenge Resources", description="Collect the most resource tokens", points=2)
        ]

    def save_game_state(self) -> None:
        """Save the current game state to the database."""
        self.db.save_game_state(self.game_state.dict())
        logging.info("Game state saved")

    def get_active_gang(self) -> Gang:
        """Get the currently active gang."""
        return self.game_state.gangs[self.game_state.active_gang_index]

    def get_active_fighter(self) -> GangMember:
        """Get the currently active fighter."""
        active_gang = self.get_active_gang()
        return active_gang.members[self.active_fighter_index]

    def next_turn(self) -> None:
        """Advance to the next turn, updating active fighters and gangs."""
        self.active_fighter_index += 1
        if self.active_fighter_index >= len(self.get_active_gang().members):
            self.active_fighter_index = 0
            self.game_state.active_gang_index = (self.game_state.active_gang_index + 1) % len(self.game_state.gangs)
            if self.game_state.active_gang_index == 0:
                self.game_state.current_turn += 1
                self.check_mission_objectives()
        logging.info(f"Next turn: {self.game_state.current_turn}, Active gang: {self.get_active_gang().name}, Active fighter: {self.get_active_fighter().name}")

    def move_fighter(self, fighter_name: str, x: int, y: int) -> bool:
        """
        Move a fighter to a new position.

        Args:
            fighter_name (str): The name of the fighter to move.
            x (int): The x-coordinate to move to.
            y (int): The y-coordinate to move to.

        Returns:
            bool: True if the move was successful, False otherwise.
        """
        active_fighter = self.get_active_fighter()
        if active_fighter.name.lower() != fighter_name.lower():
            logging.warning(f"Attempted to move inactive fighter: {fighter_name}")
            return False

        if abs(x) + abs(y) <= active_fighter.movement:
            logging.info(f"{fighter_name} moved to ({x}, {y})")
            return True
        logging.warning(f"Invalid move for {fighter_name}: distance exceeds movement allowance")
        return False

    def attack(self, attacker_name: str, target_name: str) -> str:
        """
        Perform an attack action.

        Args:
            attacker_name (str): The name of the attacking fighter.
            target_name (str): The name of the target fighter.

        Returns:
            str: A description of the attack result.
        """
        active_fighter = self.get_active_fighter()
        if active_fighter.name.lower() != attacker_name.lower():
            return "It's not this fighter's turn to act"

        target_gang = next((g for g in self.game_state.gangs if g != self.get_active_gang()), None)
        target = next((f for f in target_gang.members if f.name.lower() == target_name.lower()), None)
        if not target:
            logging.warning(f"Target not found: {target_name}")
            return "Target not found"

        weapon = active_fighter.weapons[0]  # Use the first weapon for simplicity
        
        hit_modifier = self.apply_gang_traits(active_fighter, target)
        
        if weapon.range == "Melee":
            return self.resolve_melee_attack(active_fighter, target, weapon, hit_modifier)
        else:
            return self.resolve_ranged_attack(active_fighter, target, weapon, hit_modifier)

    def resolve_melee_attack(self, attacker: GangMember, target: GangMember, weapon: Weapon, hit_modifier: int) -> str:
        """
        Resolve a melee attack.

        Args:
            attacker (GangMember): The attacking fighter.
            target (GangMember): The target fighter.
            weapon (Weapon): The weapon used for the attack.
            hit_modifier (int): The modifier to apply to the hit roll.

        Returns:
            str: A description of the attack result.
        """
        attack_log = f"{attacker.name} attacks {target.name} with {weapon.name}. "
        
        hit_roll = d20.roll(f"1d6 + {hit_modifier}").total
        hit_threshold = 7 - attacker.weapon_skill
        hit_result = "hit" if hit_roll >= hit_threshold else "miss"
        
        attack_log += f"Hit roll: {hit_roll} vs {hit_threshold}+ to hit. {hit_result.capitalize()}! "
        
        if hit_result == "hit":
            wound_roll = d20.roll("1d6").total
            to_wound = self.calculate_to_wound(weapon.strength, target.toughness)
            wound_result = "wounds" if wound_roll >= to_wound else "fails to wound"
            
            attack_log += f"Wound roll: {wound_roll} vs {to_wound}+ to wound. {wound_result.capitalize()}! "
            
            if wound_result == "wounds":
                damage_result = self.resolve_damage(weapon, target)
                attack_log += damage_result + " "
        
        logging.info(attack_log)
        return attack_log

    def resolve_ranged_attack(self, attacker: GangMember, target: GangMember, weapon: Weapon, hit_modifier: int) -> str:
        """
        Resolve a ranged attack.

        Args:
            attacker (GangMember): The attacking fighter.
            target (GangMember): The target fighter.
            weapon (Weapon): The weapon used for the attack.
            hit_modifier (int): The modifier to apply to the hit roll.

        Returns:
            str: A description of the attack result.
        """
        attack_log = f"{attacker.name} shoots at {target.name} with {weapon.name}. "
        
        hit_roll = d20.roll(f"1d6 + {hit_modifier}").total
        hit_threshold = 7 - attacker.ballistic_skill
        hit_result = "hit" if hit_roll >= hit_threshold else "miss"
        
        attack_log += f"Hit roll: {hit_roll} vs {hit_threshold}+ to hit. {hit_result.capitalize()}! "
        
        if hit_result == "hit":
            wound_roll = d20.roll("1d6").total
            to_wound = self.calculate_to_wound(weapon.strength, target.toughness)
            wound_result = "wounds" if wound_roll >= to_wound else "fails to wound"
            
            attack_log += f"Wound roll: {wound_roll} vs {to_wound}+ to wound. {wound_result.capitalize()}! "
            
            if wound_result == "wounds":
                armor_save = self.resolve_armor_save(target, weapon)
                if armor_save:
                    attack_log += f"{target.name} makes their armor save! "
                else:
                    damage_result = self.resolve_damage(weapon, target)
                    attack_log += damage_result + " "
        
        logging.info(attack_log)
        return attack_log

    def calculate_to_wound(self, strength: int, toughness: int) -> int:
        """
        Calculate the 'to wound' roll required based on strength and toughness.

        Args:
            strength (int): The strength of the attacker or weapon.
            toughness (int): The toughness of the target.

        Returns:
            int: The minimum roll required to wound.
        """
        if strength >= toughness * 2:
            return 2
        elif strength > toughness:
            return 3
        elif strength == toughness:
            return 4
        elif strength <= toughness / 2:
            return 6
        else:
            return 5

    def resolve_armor_save(self, target: GangMember, weapon: Weapon) -> bool:
        """
        Resolve an armor save attempt.

        Args:
            target (GangMember): The target of the attack.
            weapon (Weapon): The weapon used in the attack.

        Returns:
            bool: True if the armor save was successful, False otherwise.
        """
        armor_save_threshold = 6 + weapon.armor_penetration
        armor_save_roll = d20.roll("1d6").total
        return armor_save_roll >= armor_save_threshold

    def resolve_damage(self, weapon: Weapon, target: GangMember) -> str:
        """
        Resolve damage dealt to a target.

        Args:
            weapon (Weapon): The weapon used in the attack.
            target (GangMember): The target of the attack.

        Returns:
            str: A description of the damage result.
        """
        damage = weapon.damage
        target.wounds -= damage
        injury_result = ""
        if target.wounds <= 0:
            target.wounds = 0
            injury_result = self.resolve_injury(target)
        return f"Damage dealt: {damage}. {injury_result}"

    def resolve_injury(self, target: GangMember) -> str:
        """
        Resolve an injury for a fighter who has been reduced to 0 wounds.

        Args:
            target (GangMember): The injured fighter.

        Returns:
            str: A description of the injury result.
        """
        injury_roll = d20.roll("1d6").total
        injury_result = ""
        if injury_roll == 1:
            injury_result = "Flesh Wound"
            target.wounds = max(1, target.wounds)  # Ensure the fighter has at least 1 wound
        elif injury_roll in [2, 3, 4]:
            injury_result = "Seriously Injured"
            target.wounds = 0
        else:
            injury_result = "Out of Action"
            target.wounds = 0
        
        target.injuries.append(injury_result)
        logging.info(f"{target.name} suffers {injury_result} (Injury roll: {injury_roll})")
        return f"{target.name} suffers {injury_result} (Injury roll: {injury_roll})"

    def apply_gang_traits(self, attacker: GangMember, target: GangMember) -> int:
        """
        Apply gang-specific traits to modify attack rolls.

        Args:
            attacker (GangMember): The attacking fighter.
            target (GangMember): The target fighter.

        Returns:
            int: The hit modifier to apply to the attack roll.
        """
        hit_modifier = 0
        
        if attacker.gang == "Goliaths" and any(rule.name == "Unstoppable" for rule in attacker.special_rules):
            hit_modifier += 1

        if target.gang == "Escher" and any(rule.name == "Agile" for rule in target.special_rules):
            hit_modifier -= 1

        return hit_modifier

    def apply_special_rules(self, attacker: GangMember, target: GangMember, weapon: Weapon) -> None:
        """
        Apply any special rules for the attack.

        Args:
            attacker (GangMember): The attacking fighter.
            target (GangMember): The target fighter.
            weapon (Weapon): The weapon used in the attack.
        """
        # Implement special rules application logic here
        pass

    def get_battlefield_state(self) -> str:
        """
        Get a string representation of the current battlefield state.

        Returns:
            str: A string representation of the battlefield.
        """
        battlefield = self.game_state.battlefield
        state = ""
        for y in range(battlefield.height):
            for x in range(battlefield.width):
                tile = next(t for t in battlefield.tiles if t.x == x and t.y == y)
                if tile.type == "open":
                    state += "."
                elif tile.type == "cover":
                    state += "#"
                elif tile.type == "elevation":
                    state += str(tile.elevation)
            state += "\n"
        return state

    def end_fighter_activation(self) -> str:
        """
        End the current fighter's activation and move to the next.

        Returns:
            str: A message indicating the new active fighter and gang.
        """
        self.next_turn()
        return f"Activation ended. Active fighter: {self.get_active_fighter().name} ({self.get_active_gang().name})"

    def check_mission_objectives(self) -> None:
        """Check and update the status of all mission objectives."""
        for objective in self.game_state.mission_objectives:
            if objective.name == "Claim Territory":
                self.check_claim_territory_objective()
            elif objective.name == "Assassinate Leader":
                self.check_assassinate_leader_objective()
            elif objective.name == "Scavenge Resources":
                self.check_scavenge_resources_objective()

    def check_claim_territory_objective(self) -> None:
        """Check and update the 'Claim Territory' objective."""
        # Implement territory control logic here
        pass

    def check_assassinate_leader_objective(self) -> None:
        """Check and update the 'Assassinate Leader' objective."""
        for gang in self.game_state.gangs:
            if not any(member.role == "Leader" for member in gang.members):
                opposing_gang = next(g for g in self.game_state.gangs if g != gang)
                opposing_gang.victory_points += 5
                objective = next(obj for obj in self.game_state.mission_objectives if obj.name == "Assassinate Leader")
                objective.completed = True
                logging.info(f"{opposing_gang.name} completed 'Assassinate Leader' objective")

    def check_scavenge_resources_objective(self) -> None:
        """Check and update the 'Scavenge Resources' objective."""
        # Implement resource scavenging logic here
        pass

    def calculate_victory_points(self) -> List[Dict[str, int]]:
        """
        Calculate the current victory points for each gang.

        Returns:
            List[Dict[str, int]]: A list of dictionaries containing gang names and their victory points.
        """
        results = []
        for gang in self.game_state.gangs:
            gang_vp = gang.victory_points
            for objective in self.game_state.mission_objectives:
                if objective.completed:
                    gang_vp += objective.points
            results.append({"gang": gang.name, "victory_points": gang_vp})
        return results

    def is_game_over(self) -> bool:
        """
        Check if the game is over.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return self.game_state.current_turn > self.game_state.max_turns or all(obj.completed for obj in self.game_state.mission_objectives)

    def get_winner(self) -> str:
        """
        Determine the winner of the game.

        Returns:
            str: The name of the winning gang or a message if the game is not over or there's a tie.
        """
        if not self.is_game_over():
            return "Game is not over yet"
        
        results = self.calculate_victory_points()
        max_vp = max(result["victory_points"] for result in results)
        winners = [result["gang"] for result in results if result["victory_points"] == max_vp]
        
        if len(winners) > 1:
            return f"It's a tie between {' and '.join(winners)}!"
        else:
            return f"{winners[0]} wins the game!"

    def create_custom_gang_member(self, gang_name: str, member_data: Dict) -> str:
        """
        Create a custom gang member and add them to the specified gang.

        Args:
            gang_name (str): The name of the gang to add the member to.
            member_data (Dict): The data for the new gang member.

        Returns:
            str: A message indicating the result of the creation attempt.
        """
        gang = next((g for g in self.game_state.gangs if g.name.lower() == gang_name.lower()), None)
        if not gang:
            logging.warning(f"Gang '{gang_name}' not found")
            return f"Gang '{gang_name}' not found."

        try:
            new_member = GangMember(
                name=member_data['name'],
                gang=gang.name,
                role=member_data['role'],
                movement=member_data['movement'],
                weapon_skill=member_data['weapon_skill'],
                ballistic_skill=member_data['ballistic_skill'],
                strength=member_data['strength'],
                toughness=member_data['toughness'],
                wounds=member_data['wounds'],
                initiative=member_data['initiative'],
                attacks=member_data['attacks'],
                leadership=member_data['leadership'],
                cool=member_data['cool'],
                willpower=member_data['willpower'],
                intelligence=member_data['intelligence'],
                credits_value=member_data['credits_value'],
                outlaw=member_data.get('outlaw', False),
                weapons=[Weapon(**w) for w in member_data['weapons']],
                equipment=[],
                skills=member_data.get('skills', []),
                special_rules=[SpecialRule(**sr) for sr in member_data.get('special_rules', [])],
                xp=0
            )
            gang.members.append(new_member)
            logging.info(f"Created new gang member: {new_member.name} for {gang.name} gang")
            return f"Successfully created {new_member.name} for {gang.name} gang."
        except KeyError as e:
            logging.error(f"Error creating gang member: Missing required field {str(e)}")
            return f"Error: Missing required field {str(e)}"
        except ValueError as e:
            logging.error(f"Error creating gang member: Invalid data - {str(e)}")
            return f"Error: Invalid data - {str(e)}"
