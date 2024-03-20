from ObjectOrientedStateMachineRobot.robotcommand import RobotCommand


class WristAngleMidCommand(RobotCommand):
    def __init__(self):
        pass

    def execute(self, robot):
        raise NotImplementedError()
