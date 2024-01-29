import wpilib
import wpilib.drive
import wpimath
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from wpimath.geometry import Rotation2d, Translation2d
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
import time
import math

# I DO need a robot.py file that is just a placeholder so that `robotpy sim` will work

class XrcBridgeBot(wpilib.TimedRobot):

    def robotInit(self):
        pass


if __name__ == '__main__':
    wpilib.run(XrcBridgeBot)