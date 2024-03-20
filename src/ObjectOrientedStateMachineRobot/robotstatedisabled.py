import rev

from robotstate import RobotState
import logging


class RobotStateDisabled(RobotState):
    def __init__(self, robot):
        logging.debug("RobotStateDisabled.__init__")
        self.robot = robot
        # Set the motors to brake on disable
        self.robot.intake.set_brake_mode(rev.CANSparkMax.IdleMode.kBrake)
        self.robot.swerve.set_brake_mode(rev.CANSparkMax.IdleMode.kBrake)

    def periodic(self):
        logging.debug("RobotStateDisabled.periodic")
        self.robot.readAbsoluteEncodersAndOutputToSmartDashboard()
        return self

    def finalize(self):
        logging.debug("RobotStateDisabled.finalize")
        pass

