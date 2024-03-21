import rev

from robotstate import RobotState
import logging
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from robot import ObjectOrientedRobot


class RobotStateDisabled(RobotState):
    def __init__(self, robot : "ObjectOrientedRobot"):
        super().__init__(robot)
        logging.debug("RobotStateDisabled.__init__")
        self.robot = robot
        # Set the motors to brake on disable
        self.robot.intake.set_idle_mode(rev.CANSparkMax.IdleMode.kBrake)
        self.robot.swerve.set_idle_mode(rev.CANSparkMax.IdleMode.kBrake)

    def periodic(self, robot) -> RobotState:
        logging.debug("RobotStateDisabled.periodic")
        self.robot.read_absolute_encoders_and_output_to_smart_dashboard()
        return self
