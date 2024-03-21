from controllers import DriveSpeeds
from robotcommand import RobotCommand


class SwerveDriveSpeedCommand(RobotCommand):
    def __init__(self, speeds: DriveSpeeds):
        self.speeds = speeds

    def execute(self, robot):
        robot.swerve.drive(self.speeds.x_speed, self.speeds.y_speed, self.speeds.rot, field_relative=True)


class SwerveDriveStopCommand(RobotCommand):
    def __init__(self):
        pass

    def execute(self, robot):
        # ? Something else. Like set brakes?
        robot.swerve.drive(0, 0, 0, field_relative=True)


class GyroSetYawCommand(RobotCommand):
    def __init__(self, yaw):
        self.desired_yaw = yaw

    def execute(self, robot):
        raise NotImplementedError()


class PivotControlCommand(RobotCommand):
    def __init__(self, shooter_pivot_control):
        self.shooter_pivot_control = shooter_pivot_control

    def execute(self, robot):
        # TODO Do something with shooter_pivot_control
        pass
