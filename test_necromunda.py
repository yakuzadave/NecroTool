import unittest
from game_logic import GameLogic
from database import Database
from models.gang_models import Ganger, Gang
from models.weapon_models import Weapon, WeaponProfile
from models.armor_models import Armor
from models.item_models import Consumable, Equipment
from models.scenario_models import ScenarioObjective
from models.vehicle_models import Vehicle

class TestNecromundaSimulation(unittest.TestCase):

    def setUp(self):
        self.db = Database()
        self.game_logic = GameLogic(self.db)

    def test_fighter_activation_and_gang_alternation(self):
        print("Testing fighter activation and gang alternation")
        initial_active_gang = self.game_logic.get_active_gang()
        initial_active_fighter = self.game_logic.get_active_fighter()
        
        self.game_logic.end_fighter_activation()
        new_active_gang = self.game_logic.get_active_gang()
        new_active_fighter = self.game_logic.get_active_fighter()
        
        self.assertNotEqual(initial_active_gang.name, new_active_gang.name)
        self.assertNotEqual(initial_active_fighter.name, new_active_fighter.name)
        print("Fighter activation and gang alternation test passed")

    def test_weapon_profiles(self):
        print("Testing use of weapons with different profiles")
        attacker = self.game_logic.get_active_fighter()
        weapon = Weapon(
            name="Test Weapon",
            weapon_type="Ranged",
            profiles=[
                WeaponProfile(range="Short", strength=4, armor_penetration=0, damage=1, ammo_roll=None, special_rules=None),
                WeaponProfile(range="Long", strength=3, armor_penetration=-1, damage=2, ammo_roll=None, special_rules=None)
            ],
            cost=10,
            rarity="Common",
            traits=[],
            is_unwieldy=False,
            description="A test weapon"
        )
        attacker.weapons = [weapon]
        
        # Move to the next gang to ensure we're not attacking our own gang member
        self.game_logic.end_fighter_activation()
        target = self.game_logic.get_active_fighter()
        
        attack_result = self.game_logic.attack(attacker.name, target.name)
        self.assertIn(attacker.name, attack_result)
        self.assertIn(target.name, attack_result)
        self.assertIn("Test Weapon", attack_result)
        print("Weapon profiles test passed")

    def test_armor_application(self):
        print("Testing application of armor and armor saves")
        fighter = self.game_logic.get_active_fighter()
        armor = Armor(name="Test Armor", armor_rating=4, armor_type="Light")
        fighter.armor = armor
        
        initial_wounds = fighter.wounds
        damage = self.game_logic.apply_damage(fighter, 1)
        
        self.assertLessEqual(damage, 1)  # Damage should be 0 or 1 depending on the armor save
        self.assertLessEqual(fighter.wounds, initial_wounds)
        print("Armor application test passed")

    def test_attack_resolution(self):
        print("Testing attack resolution")
        attacker = self.game_logic.get_active_fighter()
        
        # Move to the next gang to ensure we're not attacking our own gang member
        self.game_logic.end_fighter_activation()
        target = self.game_logic.get_active_fighter()
        
        initial_target_wounds = target.wounds
        attack_result = self.game_logic.attack(attacker.name, target.name)
        
        self.assertIn(attacker.name, attack_result)
        self.assertIn(target.name, attack_result)
        updated_target = self.game_logic._get_fighter_by_name(target.name)
        self.assertLessEqual(updated_target.wounds, initial_target_wounds)
        print("Attack resolution test passed")

    # ... [rest of the test methods remain unchanged]

if __name__ == '__main__':
    unittest.main(verbosity=2)
