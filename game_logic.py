import logging
import d20
from typing import Optional, List, Dict, Any
from models import GameState, Gang, Ganger, CombatRound, CombatPhase, PhaseName, Scenario, Battlefield, Tile, Weapon, WeaponProfile, TileType # Added imports for Weapon and WeaponProfile, TileType
from models.gang_models import GangType, GangerRole
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
            type=GangType.GOLIATH,
            members=[
                Ganger(
                    name="Crusher",
                    gang_affiliation=GangType.GOLIATH,
                    role=GangerRole.LEADER,
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
            type=GangType.ESCHER,
            members=[
                Ganger(
                    name="Venom",
                    gang_affiliation=GangType.ESCHER,
                    role=GangerRole.LEADER,
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
                CombatPhase(name=PhaseName.ACTION, description="Fighters can perform actions like moving, shooting, and combat."),
                CombatPhase(name=PhaseName.END, description="Resolve bottle tests and lingering effects.")
            ]
        )
        self.game_state.combat_rounds.append(new_round)
        logging.info(f"Created new combat round: {new_round.round_number}")

    def get_battlefield_state(self) -> str:
        return self.game_state.battlefield.render()

    def move_fighter(self, fighter_name: str, x: int, y: int) -> bool:
        """Move a fighter to new coordinates with bounds checking."""
        fighter = self._get_fighter_by_name(fighter_name)
        if not fighter:
            logging.error(f"Fighter {fighter_name} not found.")
            return False

        # Check bounds
        if not (0 <= x < self.game_state.battlefield.width and 0 <= y < self.game_state.battlefield.height):
            logging.error(f"Invalid move for {fighter_name} to ({x}, {y}). Out of bounds.")
            return False

        # Check target tile
        target_tile = next((t for t in self.game_state.battlefield.tiles if t.x == x and t.y == y), None)
        if target_tile and target_tile.type == TileType.OBSTRUCTION:
            logging.error(f"Cannot move to obstructed tile at ({x}, {y}).")
            return False

        # Calculate movement cost including terrain
        if target_tile:
            terrain_mods = self.check_terrain_modifiers(target_tile)
            movement_cost = abs(fighter.x - x) + abs(fighter.y - y) + terrain_mods['movement']
            if movement_cost > fighter.movement:
                logging.error(f"{fighter_name} cannot move {movement_cost} spaces (including terrain costs); maximum movement is {fighter.movement}.")
                return False
        else:
            # Basic distance check if no tile info
            distance = abs(fighter.x - x) + abs(fighter.y - y)
            if distance > fighter.movement:
                logging.error(f"{fighter_name} cannot move {distance} spaces; maximum movement is {fighter.movement}.")
                return False

        # Update position
        fighter.x = x
        fighter.y = y
        logging.info(f"{fighter.name} moved to ({x}, {y}).")
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

    def calculate_hit_success(self, attacker: Ganger, defender: Ganger, weapon_profile: Optional[WeaponProfile] = None, weapon: Optional[Weapon] = None) -> tuple[bool, int]:
        """Calculate if an attack hits and any modifiers."""
        if not attacker or not defender:
            logging.error("Invalid attacker or defender")
            return (False, 0)

        base_target = attacker.weapon_skill * 3
        total_modifier = 0

        logging.info(f"Calculating hit success for {attacker.name} vs {defender.name}")
        logging.debug(f"Base target number: {base_target} (WS {attacker.weapon_skill} * 3)")

        # Apply status effect modifiers
        if attacker.is_prone:
            total_modifier -= 2
            logging.debug("Attacker is prone: -2 modifier")
        if defender.is_prone:
            total_modifier += 1
            logging.debug("Defender is prone: +1 modifier")

        # Apply terrain modifiers
        terrain_mod = self.apply_terrain_modifiers(attacker, defender)
        total_modifier += terrain_mod
        logging.debug(f"Terrain modifier: {terrain_mod}")

        # Apply weapon traits
        weapon_trait_mods = self.apply_weapon_traits(attacker, defender, weapon)
        total_modifier += weapon_trait_mods['to_hit']
        logging.debug(f"Weapon trait modifier: {weapon_trait_mods['to_hit']}")

        # Apply combat conditions
        combat_condition_mods = self.check_combat_conditions(attacker, defender)
        total_modifier += combat_condition_mods['to_hit']
        logging.debug(f"Combat condition modifier: {combat_condition_mods['to_hit']}")

        # Roll to hit
        hit_roll = self.d20.roll('1d20')
        modified_roll = hit_roll.total + total_modifier
        logging.debug(f"Hit roll: {hit_roll.total}, Modified roll: {modified_roll}, Target: {base_target}")

        success = modified_roll <= base_target
        logging.info(f"Hit success: {success} with total modifier: {total_modifier}")
        return (success, total_modifier)

    def calculate_wound_success(self, attacker: Ganger, defender: Ganger, weapon: Optional[Weapon] = None) -> tuple[bool, str]:
        """Calculate if a hit causes a wound."""
        # Get effective strength (weapon or natural)
        effective_strength = attacker.strength
        if weapon and weapon.profiles:
            effective_strength = max(profile.strength for profile in weapon.profiles)

        strength_diff = effective_strength - defender.toughness

        # Strength vs Toughness table
        if strength_diff >= 2:  # Much stronger
            wound_target = 2  # 2+
        elif strength_diff == 1:  # Stronger
            wound_target = 3  # 3+
        elif strength_diff == 0:  # Equal
            wound_target = 4  # 4+
        elif strength_diff == -1:  # Weaker
            wound_target = 5  # 5+
        else:  # Much weaker
            wound_target = 6  # 6+

        #Apply weapon traits
        weapon_trait_mods = self.apply_weapon_traits(attacker, defender, weapon)
        wound_target -= weapon_trait_mods['to_wound']

        #Apply combat conditions
        combat_condition_mods = self.check_combat_conditions(attacker, defender)
        wound_target -= combat_condition_mods['to_wound']

        wound_roll = self.d20.roll('1d20')
        success = wound_roll.total <= (wound_target * 3)

        msg = f"Strength {effective_strength} vs Toughness {defender.toughness}"
        return (success, msg)

    def resolve_armor_save(self, defender: Ganger, weapon: Optional[Weapon] = None) -> tuple[bool, str]:
        """Resolve armor save attempt."""
        if not defender.armor:
            return (False, "No armor")

        # Get base save value
        save_value = defender.armor.save_value

        # Apply weapon AP if any
        ap_modifier = 0
        if weapon and weapon.profiles:
            ap_modifier = max(profile.armor_penetration for profile in weapon.profiles)

        #Apply weapon traits
        weapon_trait_mods = self.apply_weapon_traits(defender, defender, weapon)
        ap_modifier += weapon_trait_mods['ap']

        modified_save = save_value + ap_modifier

        # Roll for save
        save_roll = self.d20.roll('1d20')
        success = save_roll.total <= (modified_save * 3)

        msg = f"Armor save {modified_save}+ (AP: {ap_modifier})"
        return (success, msg)

    def resolve_combat(self, attacker: Ganger, defender: Ganger, weapon: Optional[Weapon] = None) -> str:
        """Resolve combat between two gangers."""
        messages = []
        logging.info(f"Resolving combat between {attacker.name} and {defender.name}")

        # Resolve hits
        hit_success, hit_modifier = self.calculate_hit_success(attacker, defender, weapon=weapon)
        if not hit_success:
            return f"{attacker.name} missed {defender.name} (modifier: {hit_modifier})"

        messages.append(f"{attacker.name} hit {defender.name}")

        # Resolve wounds
        wound_success, wound_msg = self.calculate_wound_success(attacker, defender, weapon)
        messages.append(wound_msg)

        if not wound_success:
            return f"{' | '.join(messages)} | Failed to wound"

        # Resolve armor
        save_success, save_msg = self.resolve_armor_save(defender, weapon)
        messages.append(save_msg)

        if save_success:
            return f"{' | '.join(messages)} | Armor saved"

        # Apply damage
        damage = 1
        if weapon and weapon.profiles:
            damage = max(profile.damage for profile in weapon.profiles)

        defender.wounds -= damage
        messages.append(f"Dealt {damage} damage")
        logging.info(f"{attacker.name} dealt {damage} damage to {defender.name}")

        if defender.wounds <= 0:
            defender.is_out_of_action = True
            messages.append("Target is out of action")
            logging.info(f"{defender.name} is out of action")

        return " | ".join(messages)

    def get_active_gang(self) -> Gang:
        """Get the currently active gang."""
        return self.game_state.gangs[self.game_state.active_gang_index]

    def get_active_fighter(self) -> Optional[Ganger]:
        """Get the currently active fighter."""
        active_gang = self.get_active_gang()
        if self.active_fighter_index < len(active_gang.members):
            return active_gang.members[self.active_fighter_index]
        return None

    def get_current_combat_round(self) -> Optional[CombatRound]:
        """Get the current combat round."""
        if self.game_state.combat_rounds:
            return self.game_state.combat_rounds[-1]
        return None

    def get_current_combat_phase(self) -> Optional[CombatPhase]:
        """Get the current phase of combat."""
        current_round = self.get_current_combat_round()
        if current_round and current_round.phases:
            return current_round.phases[0]
        return None

    def calculate_charge_distance(self, attacker: Ganger, target: Ganger) -> int:
        """Calculate the distance needed for a charge move."""
        if attacker.x is None or attacker.y is None or target.x is None or target.y is None:
            return float('inf')

        return abs(attacker.x - target.x) + abs(attacker.y - target.y)

    def can_charge(self, attacker: Ganger, target: Ganger) -> bool:
        """Check if a charge move is possible."""
        if attacker.is_prone or attacker.is_pinned:
            return False

        charge_distance = self.calculate_charge_distance(attacker, target)
        return charge_distance <= attacker.movement * 2  # Charge allows double movement

    def perform_charge(self, attacker: Ganger, target: Ganger) -> str:
        """Execute a charge action."""
        if not self.can_charge(attacker, target):
            return f"{attacker.name} cannot reach {target.name} with a charge"

        # Move the attacker into base contact
        attacker.x = target.x
        attacker.y = target.y

        # Resolve the close combat attack with charge bonus
        return self.handle_multiple_attacks(attacker, target) # Use handle_multiple_attacks for charge


    def calculate_activation_order(self) -> List[Gang]:
        """Calculate the order in which gangs activate based on initiative."""
        gang_rolls = []
        for gang in self.game_state.gangs:
            # Use the leader's initiative if available
            leader = next((m for m in gang.members if m.role == GangerRole.LEADER), None)
            initiative_bonus = leader.initiative if leader else 0

            # Roll initiative
            roll = self.d20.roll('1d20').total + initiative_bonus
            gang_rolls.append((gang, roll))

        # Sort gangs by their initiative rolls (highest first)
        sorted_gangs = [g[0] for g in sorted(gang_rolls, key=lambda x: x[1], reverse=True)]
        return sorted_gangs

    def handle_multiple_attacks(self, attacker: Ganger, defender: Ganger, weapon: Optional[Weapon] = None) -> str:
        """Handle multiple attacks from a single fighter."""
        results = []
        for _ in range(attacker.attacks):
            if defender.is_out_of_action:
                break
            result = self.resolve_combat(attacker, defender, weapon)
            results.append(result)

        return "\n".join(results)

    def check_terrain_modifiers(self, tile: Tile) -> Dict[str, int]:
        """Calculate combat and movement modifiers based on terrain."""
        modifiers = {
            'movement': 0,
            'cover': 0,
            'to_hit': 0
        }

        if tile.type == TileType.COVER:
            modifiers['cover'] = -1  # -1 to hit against targets in cover
            modifiers['movement'] = 1  # +1 movement cost
        elif tile.type == TileType.ELEVATION:
            if tile.elevation > 0:
                modifiers['to_hit'] = 1  # +1 to hit from higher ground
                modifiers['movement'] = tile.elevation  # Additional movement cost per level

        return modifiers

    def apply_terrain_modifiers(self, attacker: Ganger, defender: Ganger) -> int:
        """Calculate total combat modifiers based on terrain for both fighters."""
        # Get attacker and defender tiles
        attacker_tile = next((t for t in self.game_state.battlefield.tiles
                            if t.x == attacker.x and t.y == attacker.y), None)
        defender_tile = next((t for t in self.game_state.battlefield.tiles
                            if t.x == defender.x and t.y == defender.y), None)

        total_modifier = 0
        if attacker_tile:
            attacker_mods = self.check_terrain_modifiers(attacker_tile)
            total_modifier += attacker_mods['to_hit']

        if defender_tile:
            defender_mods = self.check_terrain_modifiers(defender_tile)
            total_modifier += defender_mods['cover']

        return total_modifier

    def apply_weapon_traits(self, attacker: Ganger, defender: Ganger, weapon: Optional[Weapon] = None) -> Dict[str, int]:
        """Apply weapon trait effects to combat.

        Args:
            attacker: The attacking ganger
            defender: The defending ganger
            weapon: Optional weapon being used

        Returns:
            Dict[str, int]: Dictionary of modifiers from weapon traits
        """
        modifiers = {
            'to_hit': 0,
            'to_wound': 0,
            'damage': 0,
            'ap': 0,
            'blast_radius': 0,
            'sustained_hits': 0
        }

        if not weapon or not weapon.traits:
            return modifiers

        logging.debug(f"Applying weapon traits for {weapon.name}")

        for trait in weapon.traits:
            logging.debug(f"Processing trait: {trait.name}")

            match trait.name:
                case "Rapid Fire":
                    modifiers['to_hit'] -= 1  # -1 to hit for rapid fire
                    modifiers['sustained_hits'] += 1  # Additional hit on critical
                case "Unwieldy":
                    modifiers['to_hit'] -= 1  # -1 to hit for unwieldy weapons
                case "Power":
                    modifiers['ap'] += 1  # +1 AP for power weapons
                    modifiers['to_wound'] += 1  # +1 to wound for power weapons
                case "Blast":
                    if trait.description and "radius" in trait.description:
                        try:
                            radius = int(trait.description.split("radius:")[1].strip().split()[0])
                            modifiers['blast_radius'] = radius
                        except (IndexError, ValueError):
                            modifiers['blast_radius'] = 1
                case "Rending":
                    modifiers['ap'] += 2  # +2 AP on critical hits
                case "Accurate":
                    modifiers['to_hit'] += 1  # +1 to hit for accurate weapons
                case "Heavy":
                    if attacker.is_charging or attacker.has_moved:
                        modifiers['to_hit'] -= 1  # -1 to hit if moved

            logging.debug(f"Applied modifiers: {modifiers}")

        return modifiers

    def check_combat_conditions(self, attacker: Ganger, defender: Ganger) -> Dict[str, int]:
        """Check various combat conditions and apply appropriate modifiers.

        Args:
            attacker: The attacking ganger
            defender: The defending ganger

        Returns:
            Dict[str, int]: Dictionary of modifiers from combat conditions
        """
        modifiers = {
            'to_hit': 0,
            'to_wound': 0,
            'leadership_bonus': 0
        }

        # Check if the attacker is in an advantageous position
        if attacker.is_charging:
            modifiers['to_hit'] += 1  # +1 to hit when charging
            logging.debug(f"{attacker.name} gets +1 to hit from charging")

        # Check for gang tactics or special rules
        if attacker.gang_affiliation == GangType.GOLIATH:
            modifiers['to_wound'] += 1  # Goliaths get +1 to wound in close combat
            logging.debug(f"Goliath fighter gets +1 to wound")
        elif attacker.gang_affiliation == GangType.ESCHER:
            if 'toxin' in [t.name.lower() for t in (weapon.traits if weapon else [])]:
                modifiers['to_wound'] += 1  # Eschers get +1 to wound with toxin weapons

        # Check for status effects
        if attacker.is_prone:
            modifiers['to_hit'] -= 2  # -2 to hit when prone
        if defender.is_prone:
            modifiers['to_hit'] += 1  # +1 to hit prone targets

        # Leadership bonuses from nearby leaders
        if attacker.role == GangerRole.LEADER:
            modifiers['leadership_bonus'] += 1
            logging.debug(f"Leader {attacker.name} provides leadership bonus")

        # Check for advantageous height position
        if hasattr(attacker, 'elevation') and hasattr(defender, 'elevation'):
            if attacker.elevation > defender.elevation:
                modifiers['to_hit'] += 1  # +1 to hit from higher ground

        logging.debug(f"Combat conditions modifiers: {modifiers}")
        return modifiers