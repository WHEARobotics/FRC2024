import wpilib
import wpilib.drive
import wpimath
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from wpimath.geometry import Rotation2d, Translation2d
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
import time
import math

from vision import Vision #Vision file import
from CrescendoSwerveDrivetrain import CrescendoSwerveDrivetrain
# from CrescendoSwerveModule import CrescendoSwerveModule

class Myrobot(wpilib.TimedRobot):

 

    def robotInit(self):

        self.xbox = wpilib.XboxController(0)
        self.swerve = CrescendoSwerveDrivetrain()

        self.absEnc1 = self.swerve.backLeft.absEnc.getAbsolutePosition()
        self.absEnc2 = self.swerve.frontRight.absEnc.getAbsolutePosition()
        self.absEnc3 = self.swerve.frontLeft.absEnc.getAbsolutePosition()
        self.absEnc4 = self.swerve.backRight.absEnc.getAbsolutePosition()
    

        
    def disabledInit(self):
        pass

    def disabledPeriodic(self):

        
        wpilib.SmartDashboard.putString('DB/String 0',"Enc Back Left {:4.3f}".format( self.absEnc1 ))
        wpilib.SmartDashboard.putString('DB/String 1',"Enc Front Right {:4.3f}".format( self.absEnc2 ))
        wpilib.SmartDashboard.putString('DB/String 2',"Enc Front Left {:4.3f}".format( self.absEnc3 ))
        wpilib.SmartDashboard.putString('DB/String 3',"Enc Back Right {:4.3f}".format( self.absEnc4 ))

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

        self.joystick_x = -self.xbox.getLeftX()
        self.joystick_y = -self.xbox.getLeftY()
        self.joystick_x = applyDeadband(self.joystick_x , 0.1)
        self.joystick_y = applyDeadband(self.joystick_y , 0.1)
        rot = -self.xbox.getRightX()
        rot = applyDeadband(rot, 0.05)
        
        

        #1/22/2024 commented out whats below for more simplification, we dont need joystickscaling maxspeed etc.




        self.magnitude = math.sqrt(self.joystick_x*self.joystick_x + self.joystick_y*self.joystick_y)/3
        self.angle = Rotation2d(self.joystick_x, self.joystick_y)

        # self.state = SwerveModuleState(self.magnitude, self.angle)
        self.swerve.drive(self.joystick_x/3, self.joystick_y/3, rot, fieldRelativeParam)
        
        wpilib.SmartDashboard.putString('DB/String 1',"Rot2D {:4.3f}".format(self.angle.degrees()))
        # wpilib.SmartDashboard.putString('DB/String 0',"Enc {:4.3f}".format(self.frontLeft.present_degrees))
        wpilib.SmartDashboard.putString('DB/String 5',"Enc Back Left {:4.3f}".format( self.absEnc1 ))
        wpilib.SmartDashboard.putString('DB/String 6',"Enc Front Right {:4.3f}".format( self.absEnc2 ))
        wpilib.SmartDashboard.putString('DB/String 7',"Enc Front Left {:4.3f}".format( self.absEnc3 ))
        wpilib.SmartDashboard.putString('DB/String 8',"Enc Back Right {:4.3f}".format( self.absEnc4 ))

    def teleopExit(self):
        pass
    
    


if __name__ == '__main__':
    wpilib.run(Myrobot)