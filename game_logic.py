import logging
import d20
from models import GameState, Gang, GangMember, Weapon, WeaponTrait, WeaponProfile, SpecialRule, Battlefield, Tile, MissionObjective, ArmorModel
from database import Database
from typing import List, Dict, Optional, Tuple
from gang_builder import create_gang_member

class GameLogic:
    def __init__(self, db: Database):
        self.db = db
        self.game_state = self._initialize_game_state()
        self.active_fighter_index = 0
        logging.info("GameLogic initialized")

    def _initialize_game_state(self) -> GameState:
        saved_state = self.db.load_game_state()
        if saved_state:
            logging.info("Loaded saved game state")
            return GameState(**saved_state)
        else:
            logging.info("Creating new game state")
            return self._create_new_game_state()

    def _create_new_game_state(self) -> GameState:
        gang1 = self._create_goliath_gang()
        gang2 = self._create_escher_gang()
        battlefield = self._create_battlefield()
        mission_objectives = self._create_mission_objectives()
        return GameState(gangs=[gang1, gang2], battlefield=battlefield, mission_objectives=mission_objectives)

    def _create_goliath_gang(self) -> Gang:
        return Gang(name="Goliaths", members=[
            self._create_goliath_champion(),
            self._create_goliath_ganger()
        ])

    def _create_escher_gang(self) -> Gang:
        return Gang(name="Escher", members=[
            self._create_escher_champion(),
            self._create_escher_ganger()
        ])

    def _create_goliath_champion(self) -> GangMember:
        return GangMember(
            name="Crusher", gang="Goliaths", role="Champion",
            movement=4, weapon_skill=3, ballistic_skill=4, strength=4, toughness=4,
            wounds=2, initiative=2, attacks=1, leadership=7, cool=7, willpower=7, intelligence=6,
            credits_value=120, outlaw=False,
            weapons=[
                Weapon(
                    name="Combat Shotgun",
                    weapon_type="Basic",
                    cost=60,
                    rarity="Common",
                    traits=[
                        WeaponTrait(name="Blast", description="This weapon uses the Blast (3\") template."),
                        WeaponTrait(name="Knockback", description="If the hit roll exceeds the target's Strength, they are knocked back 1\" distance.")
                    ],
                    profiles=[
                        WeaponProfile(
                            range="Short: 0-8, Long: 8-16",
                            strength=4,
                            armor_penetration=0,
                            damage=1,
                            ammo_roll="4+",
                            special_rules=["Blast (3\")", "Knockback"]
                        )
                    ],
                    description="A powerful shotgun favored by Goliath gangers for its raw stopping power."
                )
            ],
            equipment=[],
            skills=["Nerves of Steel"],
            special_rules=[SpecialRule(name="Unstoppable", description="This fighter may ignore Flesh Wounds when making Injury rolls.", effect="Ignore Flesh Wounds on Injury rolls")],
            armor=ArmorModel(name="Mesh Armor", protection_value=4, locations=["Body", "Arms"], special_rules=["Flexible"]),
            xp=0
        )

    def _create_goliath_ganger(self) -> GangMember:
        return GangMember(
            name="Smasher", gang="Goliaths", role="Ganger",
            movement=4, weapon_skill=3, ballistic_skill=4, strength=4, toughness=4,
            wounds=1, initiative=2, attacks=1, leadership=6, cool=6, willpower=6, intelligence=6,
            credits_value=80, outlaw=False,
            weapons=[
                Weapon(
                    name="Fighting Knife",
                    weapon_type="Melee",
                    cost=15,
                    rarity="Common",
                    traits=[WeaponTrait(name="Melee", description="This weapon can only be used in close combat.")],
                    profiles=[
                        WeaponProfile(
                            range="Melee",
                            strength=3,
                            armor_penetration=0,
                            damage=1,
                            ammo_roll=None,
                            special_rules=["Melee"]
                        )
                    ],
                    description="A sturdy blade favored by Goliath gangers for close-quarters combat."
                )
            ],
            equipment=[],
            skills=[],
            special_rules=[],
            armor=ArmorModel(name="Flak Armor", protection_value=5, locations=["Body"], special_rules=[]),
            xp=0
        )

    def _create_escher_champion(self) -> GangMember:
        return GangMember(
            name="Venom", gang="Escher", role="Champion",
            movement=5, weapon_skill=3, ballistic_skill=3, strength=3, toughness=3,
            wounds=1, initiative=4, attacks=1, leadership=7, cool=8, willpower=7, intelligence=7,
            credits_value=100, outlaw=False,
            weapons=[
                Weapon(
                    name="Lasgun",
                    weapon_type="Basic",
                    cost=40,
                    rarity="Common",
                    traits=[WeaponTrait(name="Plentiful", description="This weapon never runs out of ammo.")],
                    profiles=[
                        WeaponProfile(
                            range="Short: 0-12, Long: 12-24",
                            strength=3,
                            armor_penetration=0,
                            damage=1,
                            ammo_roll="6+",
                            special_rules=["Plentiful"]
                        )
                    ],
                    description="A reliable energy weapon favored by Escher gangs for its accuracy and low maintenance."
                )
            ],
            equipment=[],
            skills=["Catfall"],
            special_rules=[SpecialRule(name="Agile", description="This fighter is exceptionally agile.", effect="Improve Dodge rolls")],
            armor=ArmorModel(name="Mesh Armor", protection_value=4, locations=["Body", "Arms"], special_rules=["Flexible"]),
            xp=0
        )

    def _create_escher_ganger(self) -> GangMember:
        return GangMember(
            name="Shadow", gang="Escher", role="Ganger",
            movement=5, weapon_skill=3, ballistic_skill=3, strength=3, toughness=3,
            wounds=1, initiative=4, attacks=1, leadership=6, cool=7, willpower=7, intelligence=7,
            credits_value=70, outlaw=False,
            weapons=[
                Weapon(
                    name="Stiletto Knife",
                    weapon_type="Melee",
                    cost=20,
                    rarity="Common",
                    traits=[
                        WeaponTrait(name="Melee", description="This weapon can only be used in close combat."),
                        WeaponTrait(name="Toxin", description="This weapon is coated with a dangerous toxin.")
                    ],
                    profiles=[
                        WeaponProfile(
                            range="Melee",
                            strength=3,
                            armor_penetration=-1,
                            damage=1,
                            ammo_roll=None,
                            special_rules=["Melee", "Toxin"]
                        )
                    ],
                    description="A deadly, poisoned blade favored by Escher assassins for silent kills."
                )
            ],
            equipment=[],
            skills=[],
            special_rules=[],
            armor=ArmorModel(name="Flak Armor", protection_value=5, locations=["Body"], special_rules=[]),
            xp=0
        )

    def _create_battlefield(self) -> Battlefield:
        battlefield = Battlefield(width=10, height=10, tiles=[
            Tile(x=x, y=y, type="open") for x in range(10) for y in range(10)
        ])
        self._add_cover_to_battlefield(battlefield)
        self._add_elevation_to_battlefield(battlefield)
        return battlefield

    def _add_cover_to_battlefield(self, battlefield: Battlefield) -> None:
        for _ in range(5):
            x, y = d20.roll("1d10-1").total, d20.roll("1d10-1").total
            battlefield.tiles[y * 10 + x].type = "cover"

    def _add_elevation_to_battlefield(self, battlefield: Battlefield) -> None:
        for _ in range(3):
            x, y = d20.roll("1d10-1").total, d20.roll("1d10-1").total
            battlefield.tiles[y * 10 + x].type = "elevation"
            battlefield.tiles[y * 10 + x].elevation = d20.roll("1d2").total

    def _create_mission_objectives(self) -> List[MissionObjective]:
        return [
            MissionObjective(name="Claim Territory", description="Control the most terrain at the end of the game", points=3),
            MissionObjective(name="Assassinate Leader", description="Take out the enemy gang's leader", points=5),
            MissionObjective(name="Scavenge Resources", description="Collect the most resource tokens", points=2)
        ]

    def save_game_state(self) -> None:
        self.db.save_game_state(self.game_state.dict())
        logging.info("Game state saved")

    def get_active_gang(self) -> Gang:
        return self.game_state.gangs[self.game_state.active_gang_index]

    def get_active_fighter(self) -> GangMember:
        active_gang = self.get_active_gang()
        return active_gang.members[self.active_fighter_index]

    def next_turn(self) -> None:
        self.active_fighter_index += 1
        if self.active_fighter_index >= len(self.get_active_gang().members):
            self.active_fighter_index = 0
            self.game_state.active_gang_index = (self.game_state.active_gang_index + 1) % len(self.game_state.gangs)
            if self.game_state.active_gang_index == 0:
                self.game_state.current_turn += 1
                self.check_mission_objectives()
        logging.info(f"Next turn: {self.game_state.current_turn}, Active gang: {self.get_active_gang().name}, Active fighter: {self.get_active_fighter().name}")

    def move_fighter(self, fighter_name: str, x: int, y: int) -> bool:
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
        active_fighter = self.get_active_fighter()
        if active_fighter.name.lower() != attacker_name.lower():
            return "It's not this fighter's turn to act"

        target_gang = next((g for g in self.game_state.gangs if g != self.get_active_gang()), None)
        target = next((f for f in target_gang.members if f.name.lower() == target_name.lower()), None)
        if not target:
            logging.warning(f"Target not found: {target_name}")
            return "Target not found"

        weapon = active_fighter.weapons[0]
        hit_modifier = self.apply_gang_traits(active_fighter, target)
        
        if weapon.weapon_type == "Melee":
            return self.resolve_melee_attack(active_fighter, target, weapon, hit_modifier)
        else:
            return self.resolve_ranged_attack(active_fighter, target, weapon, hit_modifier)

    def resolve_melee_attack(self, attacker: GangMember, target: GangMember, weapon: Weapon, hit_modifier: int) -> str:
        attack_log = f"{attacker.name} attacks {target.name} with {weapon.name}. "
        hit_roll = d20.roll(f"1d6 + {hit_modifier}").total
        hit_threshold = 7 - attacker.weapon_skill
        hit_result = "hit" if hit_roll >= hit_threshold else "miss"
        attack_log += f"Hit roll: {hit_roll} vs {hit_threshold}+ to hit. {hit_result.capitalize()}! "
        if hit_result == "hit":
            wound_roll = d20.roll("1d6").total
            to_wound = self.calculate_to_wound(weapon.profiles[0].strength, target.toughness)
            wound_result = "wounds" if wound_roll >= to_wound else "fails to wound"
            attack_log += f"Wound roll: {wound_roll} vs {to_wound}+ to wound. {wound_result.capitalize()}! "
            if wound_result == "wounds":
                damage_result = self.resolve_damage(weapon, target)
                attack_log += damage_result + " "
        logging.info(attack_log)
        return attack_log

    def resolve_ranged_attack(self, attacker: GangMember, target: GangMember, weapon: Weapon, hit_modifier: int) -> str:
        attack_log = f"{attacker.name} shoots at {target.name} with {weapon.name}. "
        hit_roll = d20.roll(f"1d6 + {hit_modifier}").total
        hit_threshold = 7 - attacker.ballistic_skill
        hit_result = "hit" if hit_roll >= hit_threshold else "miss"
        attack_log += f"Hit roll: {hit_roll} vs {hit_threshold}+ to hit. {hit_result.capitalize()}! "
        if hit_result == "hit":
            wound_roll = d20.roll("1d6").total
            to_wound = self.calculate_to_wound(weapon.profiles[0].strength, target.toughness)
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
        if target.armor:
            armor_save_threshold = 7 - target.armor.protection_value + weapon.profiles[0].armor_penetration
            armor_save_roll = d20.roll("1d6").total
            return armor_save_roll >= armor_save_threshold
        return False

    def resolve_damage(self, weapon: Weapon, target: GangMember) -> str:
        damage = weapon.profiles[0].damage
        target.wounds -= damage
        injury_result = ""
        if target.wounds <= 0:
            target.wounds = 0
            injury_result = self.resolve_injury(target)
        return f"Damage dealt: {damage}. {injury_result}"

    def resolve_injury(self, target: GangMember) -> str:
        injury_roll = d20.roll("1d6").total
        injury_result = ""
        if injury_roll == 1:
            injury_result = "Flesh Wound"
            target.wounds = max(1, target.wounds)
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
        hit_modifier = 0
        if attacker.gang == "Goliaths" and any(rule.name == "Unstoppable" for rule in attacker.special_rules):
            hit_modifier += 1
        if target.gang == "Escher" and any(rule.name == "Agile" for rule in target.special_rules):
            hit_modifier -= 1
        return hit_modifier

    def apply_special_rules(self, attacker: GangMember, target: GangMember, weapon: Weapon) -> None:
        pass

    def get_battlefield_state(self) -> str:
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
        self.next_turn()
        return f"Activation ended. Active fighter: {self.get_active_fighter().name} ({self.get_active_gang().name})"

    def check_mission_objectives(self) -> None:
        for objective in self.game_state.mission_objectives:
            if objective.name == "Claim Territory":
                self.check_claim_territory_objective()
            elif objective.name == "Assassinate Leader":
                self.check_assassinate_leader_objective()
            elif objective.name == "Scavenge Resources":
                self.check_scavenge_resources_objective()

    def check_claim_territory_objective(self) -> None:
        pass

    def check_assassinate_leader_objective(self) -> None:
        for gang in self.game_state.gangs:
            if not any(member.role == "Leader" for member in gang.members):
                opposing_gang = next(g for g in self.game_state.gangs if g != gang)
                opposing_gang.victory_points += 5
                objective = next(obj for obj in self.game_state.mission_objectives if obj.name == "Assassinate Leader")
                objective.completed = True
                logging.info(f"{opposing_gang.name} completed 'Assassinate Leader' objective")

    def check_scavenge_resources_objective(self) -> None:
        pass

    def calculate_victory_points(self) -> List[Dict[str, int]]:
        results = []
        for gang in self.game_state.gangs:
            gang_vp = gang.victory_points
            for objective in self.game_state.mission_objectives:
                if objective.completed:
                    gang_vp += objective.points
            results.append({"gang": gang.name, "victory_points": gang_vp})
        return results

    def is_game_over(self) -> bool:
        return self.game_state.current_turn > self.game_state.max_turns or all(obj.completed for obj in self.game_state.mission_objectives)

    def get_winner(self) -> str:
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
        gang = next((g for g in self.game_state.gangs if g.name.lower() == gang_name.lower()), None)
        if not gang:
            logging.warning(f"Gang '{gang_name}' not found")
            return f"Gang '{gang_name}' not found."

        try:
            new_member = create_gang_member(member_data)
            gang.members.append(new_member)
            logging.info(f"Created new gang member: {new_member.name} for {gang.name} gang")
            return f"Successfully created {new_member.name} for {gang.name} gang."
        except ValueError as e:
            logging.error(f"Error creating gang member: {str(e)}")
            return f"Error: {str(e)}"