import wpilib
import wpilib.drive
import wpimath
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from wpimath.geometry import Rotation2d, Translation2d
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
import time
import math
import rev

from vision import Vision #Vision file import
# from CrescendoSwerveDrivetrain import CrescendoSwerveDrivetrain
from CrescendoSwerveModule import CrescendoSwerveModule

class Myrobot(wpilib.TimedRobot):

 

    def robotInit(self):

        self.xbox = wpilib.XboxController(0)

        self.frontLeft = CrescendoSwerveModule(3, 2, 0, 0)

   

        

        self.motor = rev.CANSparkMax(10, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.motor2 = rev.CANSparkMax(11, rev._rev.CANSparkLowLevel.MotorType.kBrushless)

        #self.motor.setInverted(True)
        self.motor.setInverted(False)
        #self.motor2.setInverted(True)  
        self.motor2.setInverted(True)

        self.motor2.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)
        self.motor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)


    


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
        self.halfSpeed = True
        self.xbox = wpilib.XboxController(0)
        
        self.percent_output = 0.1

    def teleopPeriodic(self):
        self.driveWithJoystick(False)
        self.Abutton = self.xbox.getAButton()
        self.Bbutton = self.xbox.getBButton()
        self.Xbutton = self.xbox.getXButton()
        self.Ybutton = self.xbox.getYButton()
        self.RightBumper = self.xbox.getRightBumper()
        self.LeftBumper = self.xbox.getLeftBumper()

        if self.Abutton:
            self.motor2.set(-self.percent_output * -1)
            self.motor.set(-self.percent_output * -1)
    
        elif self.Bbutton:
            self.motor.set(-self.percent_output * 5)
            self.motor2.set(-self.percent_output * 5) 
        
        # elif self.Xbutton:
        #     self.motor2.set(self.percent_output * 5)
        #     self.motor.set(self.percent_output * 5)
        
        # elif self.Ybutton:
        #     self.motor2.set(self.percent_output * 2.5)
        #     self.motor.set(self.percent_output * 2.5)
        
        # elif self.RightBumper:
        #     self.motor2.set(self.percent_output * 7.5)
        #     self.motor.set(self.percent_output * 7.5)

        # if self.LeftBumper:
        #      self.motor2.set(self.percent_output * 20)
        #      self.motor.set(self.percent_output * 20)
        else:
            self.motor2.set(0)
            self.motor.set(0)

        wpilib.SmartDashboard.putString('DB/String 1',"Motor 1 {:4.3f}".format(self.motor.get()))
        wpilib.SmartDashboard.putString('DB/String 2',"Motor 2 {:4.3f}".format(self.motor2.get()))


             
    
    def driveWithJoystick(self, fieldRelativeParam: bool) -> None:
        
        # allow joystick to be off from center without giving input

        self.joystick_x = -self.xbox.getLeftX()
        self.joystick_y = -self.xbox.getLeftY()
        self.joystick_x = applyDeadband(self.joystick_x , 0.1)
        self.joystick_y = applyDeadband(self.joystick_y , 0.1)

        rot = -self.xbox.getRightX()
        rot = applyDeadband(rot, 0.05) 
        
        self.magnitude = math.sqrt(self.joystick_x*self.joystick_x + self.joystick_y*self.joystick_y)/3

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

        self.angle = Rotation2d(self.joystick_x, self.joystick_y)
        self.state = SwerveModuleState(self.magnitude, self.angle)
        self.frontLeft.setDesiredState(self.state, True)
        wpilib.SmartDashboard.putString('DB/String 1',"Rot2D {:4.3f}".format(self.angle.degrees()))
        wpilib.SmartDashboard.putString('DB/String 0',"Enc {:4.3f}".format(self.frontLeft.present_degrees))
        

         
            

    def teleopExit(self):
        pass
    
    


if __name__ == '__main__':
    wpilib.run(Myrobot)

	
