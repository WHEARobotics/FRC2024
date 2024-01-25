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
        # wpilib.CameraServer.launch()

        self.xbox = wpilib.XboxController(0)
        # self.swerve = CrescendoSwerveModule

        self.frontLeft = CrescendoSwerveModule(2, 3, 0, 0)

          #changes the limit of rate of change in the input value. the smaller the number the longer it takes to reach the destination if slew rate = 1 and input = 1 it would take 1 secnd to accelerate to full speed
        #if input = 0.5 it would take 0.5 seconds to accelerate to desired speed.
        self.xSpeedLimiter = SlewRateLimiter(3)
        self.ySpeedLimiter = SlewRateLimiter(3)
        self.rotLimiter = SlewRateLimiter(3)

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
        self.joystick_x = -self.xbox.getLeftX()
        self.joystick_y = -self.xbox.getLeftY()
        self.joystick_x = applyDeadband(self.joystick_x , 0.1)
        self.joystick_y = applyDeadband(self.joystick_y , 0.1)

        rot = -self.xbox.getRightX()
        rot = applyDeadband(rot, 0.05)
        

        

        if self.xbox.getRightTriggerAxis() > 0.9 and self.xbox.getAButton():
            self.halfSpeed = True
        elif self.xbox.getLeftTriggerAxis() > 0.9 and self.xbox.getAButton():
            self.halfSpeed = False

        #1/22/2024 commented out whats below for more simplification, we dont need joystickscaling maxspeed etc.

        # if self.halfSpeed == True:
        #     joystick_y = self.swerve.joystickscaling(self.joystick_y )
        #     xSpeed = self.xSpeedLimiter.calculate(joystick_y) * self.swerve.getMaxSpeed() / 6

        #     joystick_x = self.swerve.joystickscaling(self.joystick_x )
        #     ySpeed = self.ySpeedLimiter.calculate(joystick_x) * self.swerve.MAX_SPEED / 6

        #     rot = self.swerve.joystickscaling(rot)
        #     rot = self.rotLimiter.calculate(rot) * self.swerve.MAX_ANGULAR_SPEED / 3

        #     # self.swerve.drive(xSpeed, ySpeed, rot, fieldRelativeParam)

        # else:
        #     # Get the x speed. We are inverting this because Xbox controllers return
        #     # negative values when we push forward.
        #     joystick_y = self.swerve.joystickscaling(self.joystick_y )
        #     xSpeed = self.xSpeedLimiter.calculate(joystick_y) * self.swerve.getMaxSpeed()

        #     # Get the y speed. We are inverting this because Xbox controllers return
        #     # negative values when we push to the left.
        #     joystick_x = self.swerve.joystickscaling(self.joystick_x)
        #     ySpeed = self.ySpeedLimiter.calculate(joystick_x) * self.swerve.MAX_SPEED

        #     rot = self.swerve.joystickscaling(rot)
        #     rot = self.rotLimiter.calculate(rot) * self.swerve.MAX_ANGULAR_SPEED

            # self.swerve.drive(xSpeed, ySpeed, rot, fieldRelativeParam)
        self.angle = Rotation2d(self.xbox.getLeftX(), self.xbox.getLeftY())
        self.state = SwerveModuleState(0.1, self.angle)
        self.frontLeft.setDesiredState(self.state, True)
    def teleopExit(self):
        pass
    
    


if __name__ == '__main__':
    wpilib.run(Myrobot)
