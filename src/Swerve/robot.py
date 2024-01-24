import wpilib
import wpilib.drive
import wpimath
from wpilib import AnalogEncoder
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from wpimath.geometry import Rotation2d, Translation2d
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
import time

class Myrobot(wpilib.TimedRobot):

 

    def robotInit(self):

        self.timer = wpilib.Timer()

        #self.AbsEncFL = wpilib.AnalogInput(0)

        self.AbsEncFL = AnalogEncoder(0)
        #self.AbsEncFR = AnalogEncoder(1)
        #self.AbsEncBL = AnalogEncoder(2)
        #self.AbsEncBR = AnalogEncoder(3)

        wpilib.SmartDashboard.putString('DB/String 0'," ")
        wpilib.SmartDashboard.putString('DB/String 1'," ")
        wpilib.SmartDashboard.putString('DB/String 2'," ")
        wpilib.SmartDashboard.putString('DB/String 3'," ")
        wpilib.SmartDashboard.putString('DB/String 4'," ")
        wpilib.SmartDashboard.putString('DB/String 5'," ")
        wpilib.SmartDashboard.putString('DB/String 6'," ")
        wpilib.SmartDashboard.putString('DB/String 7'," ")
        wpilib.SmartDashboard.putString('DB/String 8'," ")
        wpilib.SmartDashboard.putString('DB/String 9'," ")

    def disabledInit(self):
        
        self.timer.reset()

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
        
        self.timer.start()

        #self.AbsEncFL.reset()
        #self.AbsEncFR.reset()
        #self.AbsEncBL.reset()
        #self.AbsEncBR.reset()

    def teleopPeriodic(self):

        wpilib.SmartDashboard.putString('DB/String 0',"Time: {:4.2f}".format(self.timer.get()))

        wpilib.SmartDashboard.putString('DB/String 1',"FL Abs: {:4.2f}".format(self.AbsEncFL.getAbsolutePosition()))
        wpilib.SmartDashboard.putString('DB/String 6',"FL Offset: {:4.2f}".format(self.AbsEncFL.getPositionOffset()))
        #wpilib.SmartDashboard.putString('DB/String 2',"FR Abs: {:4.2f}".format(self.AbsEncFR.getAbsolutePosition()))
        #wpilib.SmartDashboard.putString('DB/String 7',"FR Offset: {:4.2f}".format(self.AbsEncFL.getPositionOffset()))
        #wpilib.SmartDashboard.putString('DB/String 3',"BL Abs: {:4.2f}".format(self.AbsEncBL.getAbsolutePosition()))
        #wpilib.SmartDashboard.putString('DB/String 8',"BL Offset: {:4.2f}".format(self.AbsEncFL.getPositionOffset()))
        #wpilib.SmartDashboard.putString('DB/String 4',"BR Abs: {:4.2f}".format(self.AbsEncBR.getAbsolutePosition()))
        #wpilib.SmartDashboard.putString('DB/String 9',"BR Offset: {:4.2f}".format(self.AbsEncFL.getPositionOffset()))

    def teleopExit(self):
        pass



if __name__ == '__main__':
    wpilib.run(Myrobot)