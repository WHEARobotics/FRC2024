import wpilib
import wpilib.drive
import wpimath
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from wpimath.geometry import Rotation2d, Translation2d
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
import time

from vision import Vision #Vision file import
# from CrescendoSwerveDrivetrain import CrescendoSwerveDrivetrain
from CrescendoSwerveModule import CrescendoSwerveModule

class Myrobot(wpilib.TimedRobot):

 

    def robotInit(self):

        self.xbox = wpilib.XboxController(0)

        self.frontLeft = CrescendoSwerveModule(3, 2, 0, 0)

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
        self.halfSpeed = False

    def teleopPeriodic(self):
         self.driveWithJoystick(True)


    def driveWithJoystick(self, fieldRelativeParam: bool) -> None:
        
        # allow joystick to be off from center without giving input

        # self.joystick_x = -self.xbox.getLeftX()
        # self.joystick_y = -self.xbox.getLeftY()
        # self.joystick_x = applyDeadband(self.joystick_x , 0.1)
        # self.joystick_y = applyDeadband(self.joystick_y , 0.1)

        # rot = -self.xbox.getRightX()
        # rot = applyDeadband(rot, 0.05) 
        


        #1/22/2024 commented out whats below for more simplification, we dont need joystickscaling maxspeed etc.

        # # Get the x speed. We are inverting this because Xbox controllers return
        # # negative values when we push forward.
        # joystick_y = self.swerve.joystickscaling(self.joystick_y )
        # xSpeed = self.xSpeedLimiter.calculate(joystick_y) * self.swerve.getMaxSpeed()

        # # Get the y speed. We are inverting this because Xbox controllers return
        # # negative values when we push to the left.
        # joystick_x = self.swerve.joystickscaling(self.joystick_x)
        # ySpeed = self.ySpeedLimiter.calculate(joystick_x) * self.swerve.MAX_SPEED

        # rot = self.swerve.joystickscaling(rot)
        # rot = self.rotLimiter.calculate(rot) * self.swerve.MAX_ANGULAR_SPEED

        # self.swerve.drive(xSpeed, ySpeed, rot, fieldRelativeParam)

        self.angle = Rotation2d(self.xbox.getLeftX(), self.xbox.getLeftY())
        self.state = SwerveModuleState(0.1, self.angle)
        self.frontLeft.setDesiredState(self.state, True)
    def teleopExit(self):
        pass
    
    


if __name__ == '__main__':
    wpilib.run(Myrobot)
