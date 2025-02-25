import unittest
from game_logic import GameLogic
from database import Database
from models.gang_models import Ganger, Gang, GangerRole, GangType
from models.weapon_models import Weapon, WeaponProfile, WeaponType, WeaponTrait # Added import for WeaponTrait
from models.armor_models import Armor, ArmorType
from models import TileType, Tile

class TestNecromundaSimulation(unittest.TestCase):

    def setUp(self):
        self.db = Database()
        self.game_logic = GameLogic(self.db)

        # Create test weapon with correct range format
        self.test_weapon = Weapon(
            name="Power Hammer",
            weapon_type=WeaponType.MELEE,
            profiles=[
                WeaponProfile(
                    range="Short: 0-1, Long: 1-2",
                    strength=5,
                    armor_penetration=2,
                    damage=2,
                    short_range_modifier=0,
                    long_range_modifier=-1,
                    ammo_roll=None,
                    blast_radius=None,
                    traits=[]
                )
            ]
        )

        # Create test armor with correct attributes
        self.test_armor = Armor(
            name="Flak Armor",
            armor_type=ArmorType.FLACK,
            save_value=6,
            save_modifier=None,
            conditional_saves=[],
            special_rules=[],
            modifiers=[],
            is_bulk=False
        )

    def test_resolve_combat(self):
        """Test basic combat resolution."""
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
            intelligence=6,
            armor=self.test_armor
        )

        # Mock the dice rolls to ensure a hit (WS * 3 = 9, so roll under)
        self.game_logic.d20.roll = lambda _: type('MockRoll', (), {'total': 8})()

        result = self.game_logic.resolve_combat(attacker, defender, self.test_weapon)

        self.assertIn("TestAttacker hit TestDefender", result)
        self.assertEqual(defender.wounds, 0)
        self.assertTrue(defender.is_out_of_action)

    def test_armor_save(self):
        defender = Ganger(
            name="ArmoredDefender",
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
            intelligence=5,
            armor=self.test_armor
        )

        # Mock a successful armor save
        self.game_logic.d20.roll = lambda _: type('MockRoll', (), {'total': 15})()
        save_success, msg = self.game_logic.resolve_armor_save(defender, self.test_weapon)
        self.assertTrue(save_success)

    def test_charge_mechanics(self):
        """Test charge movement and combat mechanics."""
        attacker = Ganger(
            name="Charger",
            gang_affiliation=GangType.GOLIATH,
            role=GangerRole.GANGER,
            movement=4,
            weapon_skill=3,
            ballistic_skill=4,
            strength=4,
            toughness=4,
            wounds=2,
            initiative=3,
            attacks=1,
            leadership=7,
            cool=6,
            will=6,
            intelligence=5,
            x=0,
            y=0
        )

        defender = Ganger(
            name="Target",
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
            intelligence=6,
            x=6,
            y=0,
            armor=self.test_armor
        )

        # Test charge distance calculation
        charge_distance = self.game_logic.calculate_charge_distance(attacker, defender)
        self.assertEqual(charge_distance, 6)

        # Test charge possibility (should be possible with movement 4 since charge doubles movement)
        can_charge = self.game_logic.can_charge(attacker, defender)
        self.assertTrue(can_charge)

        # Mock the dice rolls to ensure a hit and wound
        self.game_logic.d20.roll = lambda _: type('MockRoll', (), {'total': 6})()

        # Test charge execution
        result = self.game_logic.perform_charge(attacker, defender)

        # Verify attacker moved to target's position
        self.assertEqual(attacker.x, defender.x)
        self.assertEqual(attacker.y, defender.y)

        # Verify combat was resolved
        self.assertIn("Charger hit Target", result)

    def test_multiple_attacks(self):
        """Test handling of multiple attacks from a single fighter."""
        attacker = Ganger(
            name="BrutalFighter",
            gang_affiliation=GangType.GOLIATH,
            role=GangerRole.CHAMPION,
            movement=4,
            weapon_skill=3,
            ballistic_skill=4,
            strength=4,
            toughness=4,
            wounds=2,
            initiative=3,
            attacks=2,  # Fighter has 2 attacks
            leadership=7,
            cool=6,
            will=6,
            intelligence=5
        )

        defender = Ganger(
            name="Victim",
            gang_affiliation=GangType.ESCHER,
            role=GangerRole.GANGER,
            movement=4,
            weapon_skill=3,
            ballistic_skill=4,
            strength=3,
            toughness=3,
            wounds=2,
            initiative=4,
            attacks=1,
            leadership=7,
            cool=7,
            will=7,
            intelligence=6,
            armor=self.test_armor
        )

        # Mock dice rolls to ensure hits
        self.game_logic.d20.roll = lambda _: type('MockRoll', (), {'total': 6})()

        result = self.game_logic.handle_multiple_attacks(attacker, defender, self.test_weapon)

        # Verify that multiple attacks occurred
        self.assertEqual(len(result.split('\n')), 2)
        self.assertTrue(defender.is_out_of_action)

    def test_terrain_modifiers(self):
        """Test terrain effects on combat."""
        # Create tiles with different terrain types
        cover_tile = Tile(x=0, y=0, type=TileType.COVER, elevation=0)
        elevation_tile = Tile(x=1, y=0, type=TileType.ELEVATION, elevation=2)

        # Test cover modifiers
        cover_mods = self.game_logic.check_terrain_modifiers(cover_tile)
        self.assertEqual(cover_mods['cover'], -1)
        self.assertEqual(cover_mods['movement'], 1)

        # Test elevation modifiers
        elevation_mods = self.game_logic.check_terrain_modifiers(elevation_tile)
        self.assertEqual(elevation_mods['to_hit'], 1)
        self.assertEqual(elevation_mods['movement'], 2)

    def test_weapon_traits(self):
        """Test the effects of weapon traits on combat."""
        attacker = Ganger(
            name="PowerFighter",
            gang_affiliation=GangType.GOLIATH,
            role=GangerRole.CHAMPION,
            movement=4,
            weapon_skill=3,
            ballistic_skill=4,
            strength=4,
            toughness=4,
            wounds=2,
            initiative=3,
            attacks=1,
            leadership=7,
            cool=6,
            will=6,
            intelligence=5
        )

        defender = Ganger(
            name="Target",
            gang_affiliation=GangType.ESCHER,
            role=GangerRole.GANGER,
            movement=4,
            weapon_skill=3,
            ballistic_skill=4,
            strength=3,
            toughness=3,
            wounds=2,
            initiative=4,
            attacks=1,
            leadership=7,
            cool=7,
            will=7,
            intelligence=6
        )

        # Create a weapon with traits
        power_weapon = Weapon(
            name="Power Sword",
            weapon_type=WeaponType.MELEE,
            profiles=[
                WeaponProfile(
                    range="Short: 0-1, Long: 1-2",
                    strength=4,
                    armor_penetration=2,
                    damage=1,
                    short_range_modifier=0,
                    long_range_modifier=-1,
                    ammo_roll=None,
                    blast_radius=None,
                    traits=[]
                )
            ],
            traits=[WeaponTrait(name="Power", description="Increases armor penetration")]
        )

        # Test weapon trait modifiers
        trait_mods = self.game_logic.apply_weapon_traits(attacker, defender, power_weapon)
        self.assertEqual(trait_mods['ap'], 1, "Power weapon should give +1 AP")

        # Test combat with weapon traits
        result = self.game_logic.resolve_combat(attacker, defender, power_weapon)
        self.assertIn("PowerFighter hit Target", result)

    def test_combat_conditions(self):
        """Test various combat condition modifiers."""
        attacker = Ganger(
            name="ChargingGoliath",
            gang_affiliation=GangType.GOLIATH,
            role=GangerRole.GANGER,
            movement=4,
            weapon_skill=3,
            ballistic_skill=4,
            strength=4,
            toughness=4,
            wounds=2,
            initiative=3,
            attacks=1,
            leadership=7,
            cool=6,
            will=6,
            intelligence=5,
            is_charging=True
        )

        defender = Ganger(
            name="ProneFighter",
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
            intelligence=6,
            is_prone=True
        )

        # Test combat condition modifiers
        condition_mods = self.game_logic.check_combat_conditions(attacker, defender)
        self.assertEqual(condition_mods['to_hit'], 2, "Should get +1 for charging and +1 for prone target")
        self.assertEqual(condition_mods['to_wound'], 1, "Goliath should get +1 to wound")

    def test_complex_combat_scenario(self):
        """Test a complex combat scenario with multiple modifiers."""
        attacker = Ganger(
            name="EliteWarrior",
            gang_affiliation=GangType.GOLIATH,
            role=GangerRole.CHAMPION,
            movement=4,
            weapon_skill=4,  # Better WS
            ballistic_skill=4,
            strength=4,
            toughness=4,
            wounds=2,
            initiative=3,
            attacks=2,  # Multiple attacks
            leadership=7,
            cool=6,
            will=6,
            intelligence=5,
            is_charging=True  # Charging bonus
        )

        defender = Ganger(
            name="DefensiveTarget",
            gang_affiliation=GangType.ESCHER,
            role=GangerRole.GANGER,
            movement=4,
            weapon_skill=3,
            ballistic_skill=4,
            strength=3,
            toughness=3,
            wounds=2,
            initiative=4,
            attacks=1,
            leadership=7,
            cool=7,
            will=7,
            intelligence=6,
            armor=self.test_armor,
            x=1,
            y=0
        )

        # Place defender in cover
        cover_tile = Tile(x=1, y=0, type=TileType.COVER, elevation=0)
        self.game_logic.game_state.battlefield.tiles.append(cover_tile)

        # Mock dice rolls to ensure hits
        self.game_logic.d20.roll = lambda _: type('MockRoll', (), {'total': 6})()

        # Test combat with all modifiers
        result = self.game_logic.handle_multiple_attacks(attacker, defender, self.test_weapon)

        # Verify results
        self.assertIn("EliteWarrior hit DefensiveTarget", result)
        self.assertTrue(len(result.split('\n')) > 1, "Should have multiple attack results")

    def test_edge_case_movement(self):
        """Test edge cases for fighter movement."""
        # Setup test fighter
        fighter = Ganger(
            name="TestMover",
            gang_affiliation=GangType.GOLIATH,
            role=GangerRole.GANGER,
            movement=4,
            weapon_skill=3,
            ballistic_skill=4,
            strength=4,
            toughness=4,
            wounds=2,
            initiative=3,
            attacks=1,
            leadership=7,
            cool=6,
            will=6,
            intelligence=5,
            x=0,
            y=0
        )

        self.game_logic.game_state.gangs[0].members.append(fighter)

        # Test out of bounds movement
        result = self.game_logic.move_fighter("TestMover", -1, 0)
        self.assertFalse(result, "Should not allow movement outside battlefield bounds")

        result = self.game_logic.move_fighter("TestMover", self.game_logic.game_state.battlefield.width + 1, 0)
        self.assertFalse(result, "Should not allow movement beyond battlefield width")

        # Test movement through terrain
        obstacle_tile = Tile(x=2, y=0, type=TileType.OBSTRUCTION, elevation=0)
        self.game_logic.game_state.battlefield.tiles.append(obstacle_tile)

        result = self.game_logic.move_fighter("TestMover", 2, 0)
        self.assertFalse(result, "Should not allow movement into obstructed tile")

        # Test movement cost with terrain
        elevation_tile = Tile(x=1, y=0, type=TileType.ELEVATION, elevation=2)
        self.game_logic.game_state.battlefield.tiles.append(elevation_tile)

        result = self.game_logic.move_fighter("TestMover", 1, 0)
        self.assertTrue(result, "Should allow movement to elevated tile within movement range")

        # Test excessive movement distance
        result = self.game_logic.move_fighter("TestMover", 5, 5)
        self.assertFalse(result, "Should not allow movement beyond fighter's movement characteristic")

    def test_extreme_combat_modifiers(self):
        """Test combat resolution with extreme modifier values."""
        attacker = Ganger(
            name="ExtremeAttacker",
            gang_affiliation=GangType.GOLIATH,
            role=GangerRole.CHAMPION,
            movement=4,
            weapon_skill=4,
            ballistic_skill=4,
            strength=5,
            toughness=4,
            wounds=2,
            initiative=3,
            attacks=1,
            leadership=7,
            cool=6,
            will=6,
            intelligence=5,
            is_charging=True,
            x=1,
            y=1
        )

        defender = Ganger(
            name="ExtremeDefender",
            gang_affiliation=GangType.ESCHER,
            role=GangerRole.GANGER,
            movement=4,
            weapon_skill=3,
            ballistic_skill=4,
            strength=3,
            toughness=3,
            wounds=2,
            initiative=4,
            attacks=1,
            leadership=7,
            cool=7,
            will=7,
            intelligence=6,
            is_prone=True,
            armor=self.test_armor,
            x=1,
            y=2
        )

        # Create extreme terrain conditions
        elevation_tile = Tile(x=1, y=1, type=TileType.ELEVATION, elevation=3)
        cover_tile = Tile(x=1, y=2, type=TileType.COVER, elevation=0)
        self.game_logic.game_state.battlefield.tiles.extend([elevation_tile, cover_tile])

        # Mock minimum roll
        self.game_logic.d20.roll = lambda _: type('MockRoll', (), {'total': 1})()

        # Test combat with extreme conditions
        result = self.game_logic.resolve_combat(attacker, defender, self.test_weapon)
        self.assertIn("ExtremeAttacker hit ExtremeDefender", result,
                     "Even with extreme modifiers, a roll of 1 should always hit")

        # Mock maximum roll
        self.game_logic.d20.roll = lambda _: type('MockRoll', (), {'total': 20})()
        result = self.game_logic.resolve_combat(attacker, defender, self.test_weapon)
        self.assertIn("missed", result,
                     "A roll of 20 should miss regardless of modifiers")

    def test_weapon_traits_comprehensive(self):
        """Test comprehensive weapon trait effects."""
        # Create a test fighter
        attacker = Ganger(
            name="Specialist",
            gang_affiliation=GangType.GOLIATH,
            role=GangerRole.CHAMPION,
            movement=4,
            weapon_skill=4,
            ballistic_skill=4,
            strength=4,
            toughness=4,
            wounds=2,
            initiative=3,
            attacks=1,
            leadership=7,
            cool=6,
            will=6,
            intelligence=5,
            has_moved=True  # For testing Heavy weapons
        )

        # Test various weapon types
        power_weapon = Weapon(
            name="Power Sword",
            weapon_type=WeaponType.MELEE,
            traits=[WeaponTrait(name="Power", description="Power field adds devastating energy")],
            profiles=[WeaponProfile(
                range="Short: 0-1, Long: 1-2",
                strength=4,
                armor_penetration=2,
                damage=1,
                short_range_modifier=0,
                long_range_modifier=-1,
                ammo_roll=None,
                blast_radius=None,
                traits=[]
            )]
        )

        heavy_weapon = Weapon(
            name="Heavy Bolter",
            weapon_type=WeaponType.RANGED,
            traits=[
                WeaponTrait(name="Heavy", description="Difficult to fire on the move"),
                WeaponTrait(name="Sustained Fire", description="Multiple hits")
            ],
            profiles=[WeaponProfile(
                range="Short: 0-12, Long: 12-24",
                strength=5,
                armor_penetration=2,
                damage=2,
                short_range_modifier=0,
                long_range_modifier=-1,
                ammo_roll=None,
                blast_radius=None,
                traits=[]
            )]
        )

        blast_weapon = Weapon(
            name="Grenade Launcher",
            weapon_type=WeaponType.RANGED,
            traits=[WeaponTrait(name="Blast", description="radius: 3")],
            profiles=[WeaponProfile(
                range="Short: 0-12, Long: 12-24",
                strength=4,
                armor_penetration=0,
                damage=1,
                short_range_modifier=0,
                long_range_modifier=-1,
                ammo_roll=None,
                blast_radius=None,
                traits=[]
            )]
        )

        # Test Power weapon traits
        power_mods = self.game_logic.apply_weapon_traits(attacker, None, power_weapon)
        self.assertEqual(power_mods['ap'], 1)
        self.assertEqual(power_mods['to_wound'], 1)

        # Test Heavy weapon traits for moved shooter
        heavy_mods = self.game_logic.apply_weapon_traits(attacker, None, heavy_weapon)
        self.assertEqual(heavy_mods['to_hit'], -1)

        # Test Blast weapon radius parsing
        blast_mods = self.game_logic.apply_weapon_traits(attacker, None, blast_weapon)
        self.assertEqual(blast_mods['blast_radius'], 3)

    def test_special_combat_conditions(self):
        """Test special combat conditions and gang-specific rules."""
        # Create a test leader
        leader = Ganger(
            name="Boss",
            gang_affiliation=GangType.GOLIATH,
            role=GangerRole.LEADER,
            movement=4,
            weapon_skill=4,
            ballistic_skill=4,
            strength=4,
            toughness=4,
            wounds=2,
            initiative=3,
            attacks=1,
            leadership=8,
            cool=7,
            will=7,
            intelligence=6,
            elevation=2  # Higher ground
        )

        # Create a test defender
        defender = Ganger(
            name="Target",
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
            intelligence=6,
            elevation=0,  # Lower ground
            is_prone=True
        )

        # Test leadership and elevation bonuses
        condition_mods = self.game_logic.check_combat_conditions(leader, defender)
        self.assertEqual(condition_mods['leadership_bonus'], 1)
        self.assertEqual(condition_mods['to_hit'], 2)  # +1 from height, +1 from prone target


if __name__ == '__main__':
    unittest.main(verbosity=2)