from dataclasses import dataclass
import math

@dataclass
class GameControllerState:
    """
    A dataclass that represents the state of an Xbox controller.
    """#

    a: bool
    b: bool
    x: bool
    y: bool
    dpad_down: bool
    dpad_up: bool
    dpad_left: bool
    dpad_right: bool
    bumper_l: bool
    bumper_r: bool
    stop: bool
    restart: bool
    right_y: float
    right_x: float
    left_y: float
    left_x: float
    trigger_l: float
    trigger_r: float

    def to_xrc_control_strings(self) -> str:
        """
        Converts the game-controller state into the format expected by xRCsim
        """

        # Note: Sensitive to whitespace! No spaces between = and value
        control_string = "// Written by SimBridge\n"
        control_string += f"a={1.0 if self.a else 0.0}\n"
        control_string += f"b={1.0 if self.b else 0.0}\n"
        control_string += f"x={1.0 if self.x else 0.0}\n"
        control_string += f"y={1.0 if self.y else 0.0}\n"
        control_string += f"dpad_down={1 if self.dpad_down else 0}\n"
        control_string += f"dpad_up={1 if self.dpad_up else 0}\n"
        control_string += f"dpad_left={1 if self.dpad_left else 0}\n"
        control_string += f"dpad_right={1 if self.dpad_right else 0}\n"
        control_string += f"bumper_l={1 if self.bumper_l else 0}\n"
        control_string += f"bumper_r={1 if self.bumper_r else 0}\n"
        control_string += f"stop={1 if self.stop else 0}\n"
        control_string += f"restart={1 if self.restart else 0}\n"

        control_string += f"right_y={self.right_y:.3f}\n"
        control_string += f"right_x={self.right_x:.3f}\n"
        control_string += f"left_y={self.left_y:.3f}\n"
        control_string += f"left_x={self.left_x:.3f}\n"
        control_string += f"trigger_l={self.trigger_l:.3f}\n"
        control_string += f"trigger_r={self.trigger_r:.3f}\n"


        return control_string

    def swerve_controls_to_tank_controls(self, robot_rotation_positive_degrees : float) -> 'GameControllerState':
        """
        Convert swerve controls to tank controls. Swerve controls are field-relative, and tank controls are robot-relative.
        """
        # Clone current state
        tank_control = GameControllerState(
            a=self.a,
            b=self.b,
            x=self.x,
            y=self.y,
            dpad_down=self.dpad_down,
            dpad_up=self.dpad_up,
            dpad_left=self.dpad_left,
            dpad_right=self.dpad_right,
            bumper_l=self.bumper_l,
            bumper_r=self.bumper_r,
            stop=self.stop,
            restart=self.restart,
            right_y=self.right_y,
            right_x=self.right_x,
            left_y=self.left_y,
            left_x=self.left_x,
            trigger_l=self.trigger_l,
            trigger_r=self.trigger_r
        )

        # Convert robot rotation to radians
        robot_rotation_rad = (robot_rotation_positive_degrees % 360) * math.pi / 180


        tank_control.left_x, tank_control.left_y = self.calc_tankXY_for_swerve(robot_rotation_rad, tank_control.left_x, tank_control.left_y)

        tank_control.right_x, tank_control.right_y = self.calc_tankRotation_for_swerve(robot_rotation_rad, tank_control.right_x, tank_control.right_y)


        return tank_control

    def calc_tankXY_for_swerve(self, robot_rotation_rad, swerve_x, swerve_y):
        """
        Calculate the tank controls for a swerve drive robot.
        """
        # Calculating the rotated coordinates
        rotated_x = swerve_x * math.cos(robot_rotation_rad) - swerve_x * math.sin(robot_rotation_rad)
        rotated_y = swerve_x * math.sin(robot_rotation_rad) + swerve_y * math.cos(robot_rotation_rad)

        # The field is rotated and inverted relative to gamepad joystick, so we need to swap x and y
        left_x = -rotated_y
        left_y = rotated_x
        return left_x, left_y

    def calc_tankRotation_for_swerve(self, robot_rotation_rad, swerve_x, swerve_y):
        # Right joystick should be field-relative angle desired
        desired_angle_rad = -math.atan2(swerve_y, swerve_x)
        right_magnitude = math.sqrt(swerve_x ** 2 + swerve_y ** 2)

        x = 0
        y = 0
        DEADZONE = 0.1
        if right_magnitude > DEADZONE:
            # Turn the robot towards the desired angle
            delta_rotation = desired_angle_rad - robot_rotation_rad
            if delta_rotation > math.pi:
                delta_rotation -= 2 * math.pi
            if delta_rotation < -math.pi:
                delta_rotation += 2 * math.pi
            # If rotation is to the left, just slam it
            if delta_rotation < 0:
                x = 0.2
                y = 0
            else:
                x = -0.2
                y = 0
        else:
            # If the joystick is not being used, stop the robot
            x = 0
            y = 0

        return x, y