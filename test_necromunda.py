import unittest
from game_logic import GameLogic
from database import Database
from models.gang_models import Ganger, Gang, GangerRole, GangType
from models.weapon_models import Weapon, WeaponProfile, WeaponType, WeaponTrait, Rarity # Added Rarity import
from models.armor_models import Armor, ArmorType
from models import TileType, Tile

class TestNecromundaSimulation(unittest.TestCase):

    def setUp(self):
        self.db = Database()
        self.game_logic = GameLogic(self.db)

        # Create test weapon with all required fields
        self.test_weapon = Weapon(
            name="Power Hammer",
            weapon_type=WeaponType.MELEE,
            cost=25,  # Added required field
            rarity=Rarity.COMMON,  # Added required field
            description="A massive hammer crackling with power field energy",  # Added required field
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

        # Create test armor with all required fields
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

        # Create a counter to sequence different dice roll results for the various roll types
        self.roll_counter = 0
        
        def mock_roll(_):
            self.roll_counter += 1
            if self.roll_counter == 1:  # Hit roll
                return type('MockRoll', (), {'total': 6})()  # Natural 6 for critical hit
            elif self.roll_counter == 2:  # Wound roll
                return type('MockRoll', (), {'total': 5})()  # Successful wound roll
            elif self.roll_counter == 3:  # Save roll
                return type('MockRoll', (), {'total': 1})()  # Natural 1 always fails
            elif self.roll_counter == 4:  # Injury roll
                return type('MockRoll', (), {'total': 6})()  # 6 is OUT_OF_ACTION in the updated rules
            return type('MockRoll', (), {'total': 6})()
            
        self.game_logic.d20.roll = mock_roll
        
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

        # Override the cover status check to return "none"
        original_cover_status = self.game_logic._get_target_cover_status
        self.game_logic._get_target_cover_status = lambda attacker, defender: "none"
        
        # Create a custom weapon with low AP that won't negate the save
        weapon = Weapon(
            name="Stub Gun",
            weapon_type=WeaponType.PISTOL,
            cost=10,
            rarity=Rarity.COMMON,
            profiles=[
                WeaponProfile(
                    range="Short: 0-8, Long: 8-16",
                    strength=3,
                    armor_penetration=0,  # No AP
                    damage=1,
                    short_range_modifier=0,
                    long_range_modifier=0,
                    ammo_roll=None,
                    blast_radius=None,
                    traits=[]
                )
            ],
            description="A simple pistol"
        )
        
        # Mock a successful armor save - roll of 6 should pass a 6+ save
        self.game_logic.d20.roll = lambda _: type('MockRoll', (), {'total': 6})()
        save_success, msg, roll = self.game_logic.resolve_armor_save(defender, weapon)
        
        # Restore original method
        self.game_logic._get_target_cover_status = original_cover_status
        
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
            y=0,
            is_charging=True  # Added required attribute
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

        # Create a counter to sequentially return different roll results
        self.roll_counter = 0
        
        def mock_roll(_):
            self.roll_counter += 1
            if self.roll_counter % 4 == 1:  # Hit roll
                return type('MockRoll', (), {'total': 6})()  # Natural 6 for critical hit
            elif self.roll_counter % 4 == 2:  # Wound roll
                return type('MockRoll', (), {'total': 5})()  # Successful wound roll
            elif self.roll_counter % 4 == 3:  # Save roll
                return type('MockRoll', (), {'total': 1})()  # Natural 1 always fails save
            elif self.roll_counter % 4 == 0:  # Injury roll
                return type('MockRoll', (), {'total': 6})()  # 6 is OUT_OF_ACTION in updated rules
            return type('MockRoll', (), {'total': 6})()
            
        # Override the cover status check to return "none"
        original_cover_status = self.game_logic._get_target_cover_status
        self.game_logic._get_target_cover_status = lambda attacker, defender: "none"
        
        self.game_logic.d20.roll = mock_roll

        result = self.game_logic.handle_multiple_attacks(attacker, defender, self.test_weapon)
        
        # Restore original method
        self.game_logic._get_target_cover_status = original_cover_status

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
            cost=40,
            rarity=Rarity.RARE,
            description="An energized blade that cuts through armor with ease",
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
        condition_mods = self.game_logic.check_combat_conditions(attacker, defender, None)
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

        # Create a counter to sequentially return different roll results
        self.roll_counter = 0
        
        def mock_roll(_):
            self.roll_counter += 1
            if self.roll_counter == 1:  # Hit roll
                return type('MockRoll', (), {'total': 6})()  # Critical hit with natural 6
            elif self.roll_counter == 2:  # Wound roll
                return type('MockRoll', (), {'total': 6})()  # Always wounds
            elif self.roll_counter == 3:  # Save roll
                return type('MockRoll', (), {'total': 1})()  # Failed save
            elif self.roll_counter == 4:  # Injury dice
                return type('MockRoll', (), {'total': 6})()  # Out of Action result (6)
            return type('MockRoll', (), {'total': 6})()
            
        # Override the cover status check to return "none"
        original_cover_status = self.game_logic._get_target_cover_status
        self.game_logic._get_target_cover_status = lambda attacker, defender: "none"
        
        self.game_logic.d20.roll = mock_roll

        # Test combat with extreme conditions
        result = self.game_logic.resolve_combat(attacker, defender, self.test_weapon)
        
        # Restore original method
        self.game_logic._get_target_cover_status = original_cover_status
        
        self.assertIn("ExtremeAttacker hit ExtremeDefender", result, "Critical hit should definitely land")
        
        # Now test a natural 1 miss case
        self.game_logic.d20.roll = lambda _: type('MockRoll', (), {'total': 1})()
        result = self.game_logic.resolve_combat(attacker, defender, self.test_weapon)
        
        # In Necromunda, natural 1s always miss, regardless of modifiers
        self.assertIn("missed", result, "Natural 1 should always miss in melee per Necromunda rules")

    def test_weapon_traits_comprehensive(self):
        """Test comprehensive weapon trait effects."""
        # Create test fighters for weapon trait testing
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
            has_moved=True, # For testing Heavy weapons
            armor=self.test_armor #Added armor for consistency
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
            intelligence=6,
            armor=self.test_armor #Added armor for consistency
        )

        # Test various weapon types
        power_weapon = Weapon(
            name="Power Sword",
            weapon_type=WeaponType.MELEE,
            cost=40,
            rarity=Rarity.RARE,
            description="An energized blade that cuts through armor with ease",
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
            cost=160,
            rarity=Rarity.RARE,
            description="A heavy automatic weapon that fires explosive rounds",
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
            cost=85,
            rarity=Rarity.COMMON,
            description="A launcher that fires explosive grenades",
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
        power_mods = self.game_logic.apply_weapon_traits(attacker, defender, power_weapon)
        self.assertEqual(power_mods['ap'], 1)
        self.assertEqual(power_mods['to_wound'], 1)

        # Test Heavy weapon traits for moved shooter
        heavy_mods = self.game_logic.apply_weapon_traits(attacker, defender, heavy_weapon)
        self.assertEqual(heavy_mods['to_hit'], -1)

        # Test Blast weapon radius parsing
        blast_mods = self.game_logic.apply_weapon_traits(attacker, defender, blast_weapon)
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
        condition_mods = self.game_logic.check_combat_conditions(leader, defender, None)
        self.assertEqual(condition_mods['leadership_bonus'], 1)
        self.assertEqual(condition_mods['to_hit'], 2)  # +1 from height, +1 from prone target


if __name__ == '__main__':
    unittest.main(verbosity=2)