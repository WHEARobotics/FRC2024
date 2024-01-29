import wpilib
import wpilib.drive
import wpimath
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from wpimath.geometry import Rotation2d, Translation2d
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
import time
import math

class XrcBridgeBot(wpilib.TimedRobot):

    def robotInit(self):
        self.xbox = wpilib.XboxController(0)

    def disabledInit(self):
        pass

    def disabledPeriodic(self):
        pass

    def disabledExit(self):
        pass

    def autonomousInit(self):
        pass

    def autonomousPeriodic(self):
        pass

    def autonomousExit(self):
        pass

    def teleopInit(self):
        pass
    def teleopPeriodic(self):
         self.driveWithJoystick(True)


    def driveWithJoystick(self, fieldRelativeParam: bool) -> None:
        # allow joystick to be off from center without giving input

        self.joystick_x = -self.xbox.getLeftX()
        self.joystick_y = -self.xbox.getLeftY()
        self.joystick_x = applyDeadband(self.joystick_x , 0.1)
        self.joystick_y = applyDeadband(self.joystick_y , 0.1)

        rot = -self.xbox.getRightX()
        rot = applyDeadband(rot, 0.05) 
        
        self.magnitude = math.sqrt(self.joystick_x*self.joystick_x + self.joystick_y*self.joystick_y)/3

        self.angle = Rotation2d(self.joystick_x, self.joystick_y)
        wpilib.SmartDashboard.putString('DB/String 1',"Rot2D {:4.3f}".format(self.angle.degrees()))
        wpilib.SmartDashboard.putString('DB/String 0',"Enc {:4.3f}".format(self.frontLeft.present_degrees))

    def teleopExit(self):
        pass

if __name__ == '__main__':
    wpilib.run(XrcBridgeBot)
