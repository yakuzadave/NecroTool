import unittest
from game_logic import GameLogic
from database import Database
from models.gang_models import Ganger, Gang, GangerRole, GangType
from models.weapon_models import Weapon, WeaponProfile
from models.armor_models import Armor
from models.item_models import Consumable, Equipment
from models.scenario_models import ScenarioObjective
from models.vehicle_models import Vehicle

class TestNecromundaSimulation(unittest.TestCase):

    def setUp(self):
        self.db = Database()
        self.game_logic = GameLogic(self.db)

    def test_resolve_combat(self):
        print("Testing resolve_combat")
        attacker = Ganger(
            name="TestAttacker",
            gang_affiliation=GangType.GOLIATH,
            role=GangerRole.GANGER,
            movement=4,
            weapon_skill=3,
            ballistic_skill=4,
            strength=4,
            toughness=4,
            wounds=1,
            initiative=3,
            attacks=1,
            leadership=7,
            cool=6,
            will=6,
            intelligence=5
        )
        defender = Ganger(
            name="TestDefender",
            gang_affiliation=GangType.ESCHER,
            role=GangerRole.GANGER,
            movement=4,
            weapon_skill=3,
            ballistic_skill=4,
            strength=3,
            toughness=3,
            wounds=1,
            initiative=4,
            attacks=1,
            leadership=7,
            cool=7,
            will=7,
            intelligence=6
        )
        
        # Mock the dice rolls to ensure a hit and wound
        self.game_logic.d20.roll = lambda _: type('MockRoll', (), {'total': 6})()

        result = self.game_logic.resolve_combat(attacker, defender)
        self.assertIn("TestAttacker hit and wounded TestDefender", result)
        self.assertEqual(defender.wounds, 0)
        self.assertTrue(defender.is_out_of_action)
        print("Resolve combat test passed")

if __name__ == '__main__':
    unittest.main(verbosity=2)
