from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from robot import ObjectOrientedRobot

class RobotCommand:
    """
    Abstract base class for robot commands. A robot command is a logical action that the robot can perform.
    Typically, a command will be executed by a `RobotState` in its `periodic` function, and will be used to
    control the robot's subsystems.

    Because commands are typically called in periodic functions, they should not block for long periods of time.
    """

    def __init__(self):
        pass

    def execute(self, robot : "ObjectOrientedRobot") -> None:
        raise NotImplementedError("Implement this method in the RobotCommand subclass")
