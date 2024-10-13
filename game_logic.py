import random
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
                special_rules=[SpecialRule(name="Unstoppable", description="This fighter may ignore Flesh Wounds when making Injury rolls.")],
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
                special_rules=[],
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
            x, y = random.randint(0, 9), random.randint(0, 9)
            battlefield.tiles[y * 10 + x].type = "cover"

        for _ in range(3):
            x, y = random.randint(0, 9), random.randint(0, 9)
            battlefield.tiles[y * 10 + x].type = "elevation"
            battlefield.tiles[y * 10 + x].elevation = random.randint(1, 2)

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
        hit_roll = random.randint(1, 6)
        
        if weapon.range == "Melee":  # Melee attack
            if hit_roll >= attacker.weapon_skill:
                wound_roll = random.randint(1, 6)
                if wound_roll >= 4:  # Simplified wounding
                    armor_save = random.randint(1, 6)
                    if armor_save < 4:  # Simplified armor save
                        target.wounds -= 1
                        return f"{attacker.name} hit and wounded {target.name}! Remaining wounds: {target.wounds}"
                    else:
                        return f"{attacker.name} hit {target.name}, but the armor saved them!"
                else:
                    return f"{attacker.name} hit {target.name}, but failed to wound"
            else:
                return f"{attacker.name} missed {target.name}"
        else:  # Ranged attack
            if hit_roll >= attacker.ballistic_skill:
                wound_roll = random.randint(1, 6)
                if wound_roll >= 4:  # Simplified wounding
                    armor_save = random.randint(1, 6)
                    if armor_save < 4:  # Simplified armor save
                        target.wounds -= 1
                        return f"{attacker.name} shot and wounded {target.name}! Remaining wounds: {target.wounds}"
                    else:
                        return f"{attacker.name} shot {target.name}, but the armor saved them!"
                else:
                    return f"{attacker.name} hit {target.name}, but failed to wound"
            else:
                return f"{attacker.name} missed {target.name}"

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
