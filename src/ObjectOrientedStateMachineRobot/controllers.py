from dataclasses import dataclass

from wpilib import XboxController


@dataclass(frozen=True)
class ControllersState:
    joystick_x: float
    joystick_y: float
    joystick_rot: float
    a_button : bool
    b_button : bool
    x_button : bool
    y_button : bool
    right_bumper : bool
    left_bumper : bool
    left_stick_button : bool
    right_stick_button : bool
    left_trigger : float
    right_trigger : float
    start_button : bool

@dataclass(frozen=True)
class DriveSpeeds:
    x_speed: float
    y_speed: float
    rot: float

def applyDeadband(val, deadband):
    if abs(val) < deadband:
        return 0
    return val

class Controllers:
    def __init__(self):
        self.JOYSTICK_DRIVE_SLOWDOWN_FACTOR = 3

        self.xbox = XboxController(0)
        self.xbox_operator = XboxController(1)

    def getJoystickDriveValues(self) -> (float, float, float):
        # allow joystick to be off from center without giving input

        self.joystick_x = -self.xbox.getLeftX()
        self.joystick_x = applyDeadband(self.joystick_x, 0.1)
        self.joystick_y = -self.xbox.getLeftY()
        self.joystick_y = applyDeadband(self.joystick_y, 0.1)
        joystick_rot = -self.xbox.getRightX()
        joystick_rot = applyDeadband(joystick_rot, 0.15)

        return self.joystick_x, self.joystick_y, joystick_rot

    def speeds_for_joystick_values(self, joystick_x, joystick_y, joystick_rot) -> DriveSpeeds:
        x_speed = self.joystickscaling(joystick_y) / self.JOYSTICK_DRIVE_SLOWDOWN_FACTOR
        y_speed = self.joystickscaling(joystick_x) / self.JOYSTICK_DRIVE_SLOWDOWN_FACTOR
        rot = joystick_rot  # TODO: Could add a joystickscaling here
        return DriveSpeeds(x_speed, y_speed, rot)

    def joystickscaling(self,
                        input):  # this function helps bring an exponential curve in the joystick value and near the zero value it uses less value and is more flat
        a = 1
        output = a * input * input * input + (1 - a) * input
        return output


    def get_state(self) -> ControllersState:
        joystick_x, joystick_y, joystick_rot = self.getJoystickDriveValues()
        a_button = self.xbox_operator.getAButton()
        Bbutton = self.xbox_operator.getBButton()
        Xbutton = self.xbox_operator.getXButton()
        Ybutton = self.xbox_operator.getYButton()
        RightBumper = self.xbox_operator.getRightBumper()
        LeftBumper = self.xbox_operator.getLeftBumper()
        leftStickButton = self.xbox_operator.getLeftStickButton()
        rightStickButton = self.xbox_operator.getRightStickButton()
        leftTrigger = self.xbox_operator.getLeftTriggerAxis()
        rightTrigger = self.xbox_operator.getRightTriggerAxis()
        startButton = self.xbox_operator.getStartButton()
        return ControllersState(joystick_x, joystick_y, joystick_rot, \
                                a_button, Bbutton, Xbutton, Ybutton, \
                                RightBumper, LeftBumper, leftStickButton, rightStickButton, \
                                leftTrigger, rightTrigger, startButton)