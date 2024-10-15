import logging
import d20
import random
from models import GameState, Gang, GangMember, Weapon, WeaponTrait, WeaponProfile, SpecialRule, Battlefield, Tile, ScenarioObjective, ArmorModel, Consumable, Equipment, Scenario, ScenarioDeploymentZone, ScenarioSpecialRule
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
        scenario = self._create_default_scenario()
        return GameState(gangs=[gang1, gang2], battlefield=battlefield, scenario=scenario)

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
            xp=0,
            consumables=[],
            injuries=[]
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
            xp=0,
            consumables=[],
            injuries=[]
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
            xp=0,
            consumables=[],
            injuries=[]
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
            xp=0,
            consumables=[],
            injuries=[]
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

    def _create_default_scenario(self) -> Scenario:
        return Scenario(
            name="Turf War",
            description="Two gangs clash over control of valuable territory in the underhive.",
            objectives=[
                ScenarioObjective(
                    name="Control Central Zone",
                    description="Control the central 4x4 area of the battlefield at the end of the game.",
                    rewards="5 victory points",
                    points=5
                ),
                ScenarioObjective(
                    name="Eliminate Enemy Leader",
                    description="Take out the enemy gang's leader.",
                    rewards="3 victory points",
                    points=3
                ),
                ScenarioObjective(
                    name="Scavenge Resources",
                    description="Collect resource tokens scattered across the battlefield.",
                    rewards="1 victory point per token, up to 3",
                    points=1
                )
            ],
            deployment_zones=[
                ScenarioDeploymentZone(
                    name="Zone A",
                    description="Deploy within 6\" of the northern table edge."
                ),
                ScenarioDeploymentZone(
                    name="Zone B",
                    description="Deploy within 6\" of the southern table edge."
                )
            ],
            special_rules=[
                ScenarioSpecialRule(
                    name="Unstable Environment",
                    effect="At the end of each round, roll a d6. On a 6, a random piece of terrain collapses, potentially causing damage to nearby fighters."
                )
            ],
            max_gangs=2,
            duration="6 rounds or until one gang is broken",
            rewards="The winning gang gains d3x10 credits and 1 territory."
        )

    def set_scenario(self, scenario: Scenario) -> None:
        self.game_state.scenario = scenario
        logging.info(f"Scenario set: {scenario.name}")

    def get_scenario(self) -> Optional[Scenario]:
        return self.game_state.scenario

    def check_scenario_objectives(self) -> None:
        if not self.game_state.scenario:
            return

        for objective in self.game_state.scenario.objectives:
            if not objective.completed:
                self._check_objective(objective)

    def _check_objective(self, objective: ScenarioObjective) -> None:
        if objective.name == "Control Central Zone":
            self._check_control_central_zone(objective)
        elif objective.name == "Eliminate Enemy Leader":
            self._check_eliminate_enemy_leader(objective)
        elif objective.name == "Scavenge Resources":
            self._check_scavenge_resources(objective)

    def _check_control_central_zone(self, objective: ScenarioObjective) -> None:
        central_zone = [tile for tile in self.game_state.battlefield.tiles
                        if 3 <= tile.x <= 6 and 3 <= tile.y <= 6]
        gang_presence = {gang.name: 0 for gang in self.game_state.gangs}
        
        for tile in central_zone:
            for gang in self.game_state.gangs:
                for member in gang.members:
                    if member.x == tile.x and member.y == tile.y:
                        gang_presence[gang.name] += 1
        
        controlling_gang = max(gang_presence, key=gang_presence.get)
        if gang_presence[controlling_gang] > 0:
            objective.completed = True
            self._award_victory_points(controlling_gang, objective.points)
            logging.info(f"{controlling_gang} completed the 'Control Central Zone' objective")

    def _check_eliminate_enemy_leader(self, objective: ScenarioObjective) -> None:
        for gang in self.game_state.gangs:
            if not any(member.role == "Leader" and member.wounds > 0 for member in gang.members):
                opposing_gang = next(g for g in self.game_state.gangs if g != gang)
                objective.completed = True
                self._award_victory_points(opposing_gang.name, objective.points)
                logging.info(f"{opposing_gang.name} completed the 'Eliminate Enemy Leader' objective")

    def _check_scavenge_resources(self, objective: ScenarioObjective) -> None:
        pass

    def _award_victory_points(self, gang_name: str, points: int) -> None:
        gang = next(gang for gang in self.game_state.gangs if gang.name == gang_name)
        gang.victory_points += points
        logging.info(f"{gang_name} awarded {points} victory points")

    def apply_scenario_special_rules(self) -> None:
        if not self.game_state.scenario or not self.game_state.scenario.special_rules:
            return

        for rule in self.game_state.scenario.special_rules:
            if rule.name == "Unstable Environment":
                self._apply_unstable_environment()

    def _apply_unstable_environment(self) -> None:
        if d20.roll("1d6").total == 6:
            collapsible_terrain = [tile for tile in self.game_state.battlefield.tiles if tile.type == "cover" or tile.elevation > 0]
            if collapsible_terrain:
                collapsed_terrain = random.choice(collapsible_terrain)
                self._collapse_terrain(collapsed_terrain)

    def _collapse_terrain(self, tile: Tile) -> None:
        if tile.type == "cover":
            tile.type = "open"
        elif tile.elevation > 0:
            tile.elevation -= 1
        
        affected_fighters = self._get_affected_fighters(tile)
        for fighter in affected_fighters:
            damage = d20.roll("1d3").total
            fighter.wounds = max(0, fighter.wounds - damage)
            logging.info(f"{fighter.name} took {damage} damage from collapsing terrain")

    def _get_affected_fighters(self, tile: Tile) -> List[GangMember]:
        affected_fighters = []
        for gang in self.game_state.gangs:
            for member in gang.members:
                if abs(member.x - tile.x) <= 1 and abs(member.y - tile.y) <= 1:
                    affected_fighters.append(member)
        return affected_fighters

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
                self.check_scenario_objectives()
                self.apply_scenario_special_rules()
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
        
        self.apply_equipment_effects(active_fighter)
        self.apply_equipment_effects(target)

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

    def is_game_over(self) -> bool:
        return self.game_state.current_turn > self.game_state.scenario.duration or all(obj.completed for obj in self.game_state.scenario.objectives)

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

    def use_consumable(self, fighter_name: str, consumable_name: str) -> str:
        fighter = self._get_fighter_by_name(fighter_name)
        if not fighter:
            return f"Fighter {fighter_name} not found."

        consumable = next((c for c in fighter.consumables if c.name.lower() == consumable_name.lower()), None)
        if not consumable:
            return f"{fighter_name} doesn't have a {consumable_name}."

        if consumable.uses <= 0:
            return f"{consumable_name} has no uses left."

        effect_result = self._apply_consumable_effect(fighter, consumable)
        consumable.uses -= 1
        if consumable.uses <= 0:
            fighter.consumables.remove(consumable)

        return effect_result

    def _apply_consumable_effect(self, fighter: GangMember, consumable: Consumable) -> str:
        effect_description = f"{fighter.name} uses {consumable.name}. {consumable.effect}"
        
        if "Stimm-Slug" in consumable.name:
            fighter.strength += 1
            fighter.toughness += 1
            effect_description += f" {fighter.name}'s Strength and Toughness increased by 1 for one round."
        elif "Medipack" in consumable.name:
            healed_wounds = min(d20.roll("1d3").total, fighter.wounds)
            fighter.wounds += healed_wounds
            effect_description += f" {fighter.name} regains {healed_wounds} wound(s)."

        if consumable.side_effects:
            effect_description += f" Side effect: {consumable.side_effects}"

        return effect_description

    def apply_equipment_effects(self, fighter: GangMember) -> None:
        for equipment in fighter.equipment:
            if equipment.modifiers:
                for modifier in equipment.modifiers:
                    self._apply_equipment_modifier(fighter, modifier)

    def _apply_equipment_modifier(self, fighter: GangMember, modifier: str) -> None:
        stat, value = modifier.split()
        value = int(value)
        if stat in fighter.__dict__:
            setattr(fighter, stat, getattr(fighter, stat) + value)

    def _get_fighter_by_name(self, name: str) -> Optional[GangMember]:
        for gang in self.game_state.gangs:
            for member in gang.members:
                if member.name.lower() == name.lower():
                    return member
        return None

    def calculate_victory_points(self) -> List[Dict[str, int]]:
        results = []
        for gang in self.game_state.gangs:
            gang_vp = gang.victory_points
            for objective in self.game_state.scenario.objectives:
                if objective.completed:
                    gang_vp += objective.points
            results.append({"gang": gang.name, "victory_points": gang_vp})
        return results