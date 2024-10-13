import random
from models import GameState, Gang, Fighter, Weapon, Skill, Battlefield, Tile
from database import Database

class GameLogic:
    def __init__(self, db: Database):
        self.db = db
        self.game_state = self._initialize_game_state()

    def _initialize_game_state(self) -> GameState:
        # Load or create initial game state
        saved_state = self.db.load_game_state()
        if saved_state:
            return GameState(**saved_state)
        else:
            return self._create_new_game_state()

    def _create_new_game_state(self) -> GameState:
        # Create a simple game state with two gangs and a small battlefield
        gang1 = Gang(name="Goliaths", fighters=[
            Fighter(name="Crusher", move=4, weapon_skill=3, ballistic_skill=4, strength=4, toughness=4, wounds=2, initiative=2, attacks=1, leadership=7, cool=7, will=7, intelligence=6,
                    weapons=[Weapon(name="Combat Shotgun", range=8, strength=4, ap=0, damage=1, ammo=4, traits=["Blast (3)", "Knockback"])]),
            Fighter(name="Smasher", move=4, weapon_skill=3, ballistic_skill=4, strength=4, toughness=4, wounds=1, initiative=2, attacks=1, leadership=6, cool=6, will=6, intelligence=6,
                    weapons=[Weapon(name="Fighting Knife", range=1, strength=3, ap=0, damage=1, ammo=-1, traits=["Melee"])])
        ])
        gang2 = Gang(name="Escher", fighters=[
            Fighter(name="Venom", move=5, weapon_skill=3, ballistic_skill=3, strength=3, toughness=3, wounds=1, initiative=4, attacks=1, leadership=7, cool=8, will=7, intelligence=7,
                    weapons=[Weapon(name="Lasgun", range=24, strength=3, ap=0, damage=1, ammo=6)]),
            Fighter(name="Shadow", move=5, weapon_skill=3, ballistic_skill=3, strength=3, toughness=3, wounds=1, initiative=4, attacks=1, leadership=6, cool=7, will=7, intelligence=7,
                    weapons=[Weapon(name="Stiletto Knife", range=1, strength=3, ap=-1, damage=1, ammo=-1, traits=["Melee", "Toxin"])])
        ])

        battlefield = Battlefield(width=10, height=10, tiles=[
            Tile(x=x, y=y, type="open") for x in range(10) for y in range(10)
        ])

        # Add some cover and elevation
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
        fighter = next((f for f in active_gang.fighters if f.name.lower() == fighter_name.lower()), None)
        if not fighter:
            return False

        # Simple movement check (no pathfinding)
        if abs(x) + abs(y) <= fighter.move:
            return True
        return False

    def attack(self, attacker_name: str, target_name: str) -> str:
        active_gang = self.get_active_gang()
        attacker = next((f for f in active_gang.fighters if f.name.lower() == attacker_name.lower()), None)
        if not attacker:
            return "Attacker not found"

        target_gang = next((g for g in self.game_state.gangs if g != active_gang), None)
        target = next((f for f in target_gang.fighters if f.name.lower() == target_name.lower()), None)
        if not target:
            return "Target not found"

        weapon = attacker.weapons[0]  # Use the first weapon for simplicity
        hit_roll = random.randint(1, 6)
        
        if weapon.range == 1:  # Melee attack
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
