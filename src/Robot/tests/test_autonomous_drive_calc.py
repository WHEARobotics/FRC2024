from robot import Myrobot
import unittest

class AutonomousDriveCalcTest(unittest.TestCase):
    def test_arrived_at_target(self):
        # Given
        target_x, target_y, target_rotation = 0, 0, 0
        botpose = [0, 0, -1, -1, -1, 0, -1]
        # When
        x_pct, y_pct, rot_pct, arrived = Myrobot.drive_values_for_field_position(botpose, target_x, target_y, target_rotation)
        # Then
        assert arrived == True
        assert x_pct == 0
        assert y_pct == 0
        assert rot_pct == 0

    def test_drive_fast_to_target(self):
        # Given
        target_x, target_y, target_rotation = 10, 10, 0
        botpose = [0, 0, -1, -1, -1, 0, -1]
        # When
        x_pct, y_pct, rot_pct, arrived = Myrobot.drive_values_for_field_position(botpose, target_x, target_y, target_rotation)
        # Then
        assert arrived == False
        self.assertAlmostEqual(x_pct, 1.0)
        self.assertAlmostEqual(y_pct, 1.0)
        self.assertAlmostEqual(rot_pct, 0.0)

    def test_drive_slow_to_target(self):
        # Given
        target_x, target_y, target_rotation = 1, 1, 0
        botpose = [0, 0, -1, -1, -1, 0, -1]
        # When
        x_pct, y_pct, rot_pct, arrived = Myrobot.drive_values_for_field_position(botpose, target_x, target_y, target_rotation)
        # Then
        assert arrived == False
        self.assertAlmostEqual(x_pct, 0.3535534)
        self.assertAlmostEqual(y_pct, 0.3535534)
        self.assertAlmostEqual(rot_pct, 0.0)

    def test_yaws_quickly(self):
        # Given
        target_x, target_y, target_rotation = 0, 0, 45
        botpose = [0, 0, -1, -1, -1, 0, -1]
        # When
        x_pct, y_pct, rot_pct, arrived = Myrobot.drive_values_for_field_position(botpose, target_x, target_y, target_rotation)
        # Then
        assert arrived == False
        self.assertAlmostEqual(x_pct, 0.0)
        self.assertAlmostEqual(y_pct, 0.0)
        self.assertAlmostEqual(rot_pct, -1.0)

        # Given
        target_x, target_y, target_rotation = 0, 0, 45
        botpose = [0, 0, -1, -1, -1, 0, -1]
        # When
        x_pct, y_pct, rot_pct, arrived = Myrobot.drive_values_for_field_position(botpose, target_x, target_y, target_rotation)
        # Then
        assert arrived == False
        self.assertAlmostEqual(x_pct, 0.0)
        self.assertAlmostEqual(y_pct, 0.0)
        self.assertAlmostEqual(rot_pct, -1.0)