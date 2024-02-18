import wpilib
import wpilib.drive
import wpimath
from rev import CANSparkLowLevel
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
        INTAKE_WRIST_ANGLE = 0
        OUTPUT_WRIST_ANGLE = 90
        self.WRIST_GEAR_RATIO = 1

        self.wrist_motor = rev.CANSparkMax(15, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.intake_motor = rev.CANSparkMax(14, rev._rev.CANSparkLowLevel.MotorType.kBrushless)

        self.xbox = wpilib.XboxController(0)

        self.wrist_in = INTAKE_WRIST_ANGLE
        self.wrist_out = OUTPUT_WRIST_ANGLE
        

        self.PIDController = self.wrist_motor.getPIDController()
        self.wrist_encoder = self.wrist_motor.getEncoder()


    def teleopInit(self):
        self.halfSpeed = True
        
        self.wrist_encoder.setPosition(self.wrist_in)

        self.percent_output = 0.1

    def teleopPeriodic(self):
        # Just set it to a defaul value for now
        desired_angle = self.wrist_in

        self.Bbutton = self.xbox.getBButton()

        if self.Bbutton:
            desired_angle = self.wrist_out
           # self.intake_motor.set(self.percent_output * 2)
            
        else:
            desired_angle = self.wrist_in

        desired_turn_count = self.DegToTurnCount(desired_angle)

        self.PIDController.setReference(desired_turn_count, CANSparkLowLevel.ControlType.kPosition)
        self.PIDController.setP(0.5)

        current_angle = self.TurnCountToDeg(self.wrist_encoder.getPosition())
        wpilib.SmartDashboard.putString('DB/String 1',f"Desired angle: {desired_angle:.1f}")
        wpilib.SmartDashboard.putString('DB/String 2', f"Current angle: {current_angle:.1f}")
        wpilib.SmartDashboard.putString('DB/String 3', f"Desired Turn Count: {desired_turn_count:.1f}")

    def DegToTurnCount(self, deg):
        return deg * (1.0/360.0) * self.WRIST_GEAR_RATIO #150/7 : 1
    #deg to count 

    def TurnCountToDeg(self, count):
        return count * 360.0 / self.WRIST_GEAR_RATIO
    #count to deg


            