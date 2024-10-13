import d20
from models import GameState, Gang, GangMember, Weapon, Equipment, SpecialRule, Battlefield, Tile
from database import Database

class GameLogic:
    def __init__(self, db: Database):
        self.db = db
        self.game_state = self._initialize_game_state()

    def _initialize_game_state(self) -> GameState:
        saved_state = self.db.load_game_state()
        if saved_state:
            return GameState(**saved_state)
        else:
            return self._create_new_game_state()

    def _create_new_game_state(self) -> GameState:
        gang1 = Gang(name="Goliaths", members=[
            GangMember(
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
            ),
            GangMember(
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
        ])

        gang2 = Gang(name="Escher", members=[
            GangMember(
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
            ),
            GangMember(
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
        ])

        battlefield = Battlefield(width=10, height=10, tiles=[
            Tile(x=x, y=y, type="open") for x in range(10) for y in range(10)
        ])

        for _ in range(5):
            x, y = d20.roll("1d10-1").total, d20.roll("1d10-1").total
            battlefield.tiles[y * 10 + x].type = "cover"

        for _ in range(3):
            x, y = d20.roll("1d10-1").total, d20.roll("1d10-1").total
            battlefield.tiles[y * 10 + x].type = "elevation"
            battlefield.tiles[y * 10 + x].elevation = d20.roll("1d2").total

        return GameState(gangs=[gang1, gang2], battlefield=battlefield)

    def save_game_state(self):
        self.db.save_game_state(self.game_state.dict())

    def get_active_gang(self) -> Gang:
        return self.game_state.gangs[self.game_state.active_gang_index]

    def next_turn(self):
        self.game_state.active_gang_index = (self.game_state.active_gang_index + 1) % len(self.game_state.gangs)
        if self.game_state.active_gang_index == 0:
            self.game_state.current_turn += 1

    def move_fighter(self, fighter_name: str, x: int, y: int) -> bool:
        active_gang = self.get_active_gang()
        fighter = next((f for f in active_gang.members if f.name.lower() == fighter_name.lower()), None)
        if not fighter:
            return False

        if abs(x) + abs(y) <= fighter.movement:
            return True
        return False

    def attack(self, attacker_name: str, target_name: str) -> str:
        active_gang = self.get_active_gang()
        attacker = next((f for f in active_gang.members if f.name.lower() == attacker_name.lower()), None)
        if not attacker:
            return "Attacker not found"

        target_gang = next((g for g in self.game_state.gangs if g != active_gang), None)
        target = next((f for f in target_gang.members if f.name.lower() == target_name.lower()), None)
        if not target:
            return "Target not found"

        weapon = attacker.weapons[0]  # Use the first weapon for simplicity
        
        hit_modifier = self.apply_gang_traits(attacker, target)
        
        if weapon.range == "Melee":
            return self.resolve_melee_attack(attacker, target, weapon, hit_modifier)
        else:
            return self.resolve_ranged_attack(attacker, target, weapon, hit_modifier)

    def resolve_melee_attack(self, attacker, target, weapon, hit_modifier):
        hit_roll = d20.roll(f"1d6 + {hit_modifier}").total
        if hit_roll >= attacker.weapon_skill:
            wound_roll = d20.roll("1d6").total
            to_wound = self.calculate_to_wound(weapon.strength, target.toughness)
            if wound_roll >= to_wound:
                damage = self.resolve_damage(weapon, target)
                return f"{attacker.name} hit and wounded {target.name} with {weapon.name}! Damage dealt: {damage}"
            else:
                return f"{attacker.name} hit {target.name}, but failed to wound"
        else:
            return f"{attacker.name} missed {target.name}"

    def resolve_ranged_attack(self, attacker, target, weapon, hit_modifier):
        hit_roll = d20.roll(f"1d6 + {hit_modifier}").total
        if hit_roll >= attacker.ballistic_skill:
            wound_roll = d20.roll("1d6").total
            to_wound = self.calculate_to_wound(weapon.strength, target.toughness)
            if wound_roll >= to_wound:
                damage = self.resolve_damage(weapon, target)
                return f"{attacker.name} shot and wounded {target.name} with {weapon.name}! Damage dealt: {damage}"
            else:
                return f"{attacker.name} hit {target.name}, but failed to wound"
        else:
            return f"{attacker.name} missed {target.name}"

    def calculate_to_wound(self, strength, toughness):
        if strength >= toughness * 2:
            return 2
        elif strength > toughness:
            return 3
        elif strength == toughness:
            return 4
        elif strength < toughness:
            return 5
        else:
            return 6

    def resolve_damage(self, weapon, target):
        damage = weapon.damage
        armor_save = d20.roll("1d6").total
        if armor_save + weapon.armor_penetration >= 4:  # Simplified armor save
            damage = 0
        
        if damage > 0:
            target.wounds -= damage
            if target.wounds <= 0:
                target.wounds = 0
                # Implement injury roll here
        
        return damage

    def apply_gang_traits(self, attacker, target):
        hit_modifier = 0
        
        # Goliath trait: Unstoppable
        if attacker.gang == "Goliaths" and any(rule.name == "Unstoppable" for rule in attacker.special_rules):
            hit_modifier += 1

        # Escher trait: Agile
        if target.gang == "Escher" and any(rule.name == "Agile" for rule in target.special_rules):
            hit_modifier -= 1

        return hit_modifier

    def apply_special_rules(self, attacker, target, weapon):
        # Implement special rules here
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