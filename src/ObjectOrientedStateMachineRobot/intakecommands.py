from ObjectOrientedStateMachineRobot.intake import IntakeCommandEnum, WristAngleCommandEnum
from ObjectOrientedStateMachineRobot.robotcommand import RobotCommand


class IntakeCommand(RobotCommand):
    def __init__(self, intake_control, wrist_position):
        self.intake_control = intake_control
        self.wrist_position = wrist_position

    def execute(self, robot):
        # ? robot.intake.periodic(self.wrist_position, self.intake_control)
        raise NotImplementedError()


class OuttakeCommand(RobotCommand):
    def __init__(self, wrist_position, intake_control, kicker_action, shooter_pivot_control):
        self.wrist_position = wrist_position
        self.intake_control = intake_control
        self.kicker_action = kicker_action
        self.shooter_pivot_control = shooter_pivot_control

    def execute(self, robot):
        raise NotImplementedError()


class IntakeIdleCommand(RobotCommand):
    def __init__(self):
        self.intake_control = IntakeCommandEnum.idle

    def execute(self, robot):
        raise NotImplementedError()


class WristStowCommand(RobotCommand):
    def __init__(self):
        self.wrist_position = WristAngleCommandEnum.wrist_stow_action

    def execute(self, robot):
        raise NotImplementedError()


class WristAngleMidCommand(RobotCommand):
    def __init__(self):
        self.wrist_position = WristAngleCommandEnum.wrist_mid_action

    def execute(self, robot):
        raise NotImplementedError()