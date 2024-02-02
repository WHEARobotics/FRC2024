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
        robot_rotation = -(robot_rotation_positive_degrees % 360) * math.pi / 180


        # Calculating the rotated coordinates
        rotated_x = tank_control.left_x * math.cos(robot_rotation) - tank_control.left_y * math.sin(robot_rotation)
        rotated_y = tank_control.left_x * math.sin(robot_rotation) + tank_control.left_y * math.cos(robot_rotation)

        # The field is rotated and inverted relative to gamepad joystick, so we need to swap x and y and invert
        tank_control.left_x = rotated_y
        tank_control.left_y = -rotated_x

        return tank_control
