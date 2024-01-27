
import wpilib
import wpimath
import rev
from rev import CANSparkLowLevel
from wpimath.kinematics import SwerveDrive4Kinematics, SwerveDrive4Odometry, SwerveModulePosition, SwerveModuleState, ChassisSpeeds
from wpimath.controller import PIDController, ProfiledPIDController
from wpimath.controller import SimpleMotorFeedforwardMeters
from wpimath.geometry import Rotation2d, Translation2d

from wpimath.kinematics import SwerveModulePosition, SwerveModuleState
from wpimath.trajectory import TrapezoidProfile

from wpilib import Encoder
from wpilib.interfaces import MotorController
from wpilib import PWMSparkMax

import math
import time # Temporary for diagnostics

class CrescendoSwerveModule:      #This is the 'constructor' which we refer to in the Drivtrain file i.e. CrescendoSwerveModule(3,4,5,ABSOLUTEPOS_4)                            #UPDATE: 2/3/2023

    
    WHEELDIAMETER = 4 * 0.0254 #4 inch diameter for the wheel times the conversion to meters
    TURNING_GEAR_RATIO = 150.0/7.0 # Docs call it a 150/7:1
    DRIVE_GEAR_RATIO = 6.75

    #turn angle invert: yes
    #drive invert: no

    
    def __init__(self,driveMotorChannel : int, turningMotorChannel : int, absoluteEncoderChannel : int, absEncOffset : float) -> None:        #The first three parameters refer to which motor controller 
        self.turningMotor = rev.CANSparkMax(turningMotorChannel, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.driveMotor = rev.CANSparkMax(driveMotorChannel, rev._rev.CANSparkLowLevel.MotorType.kBrushless)                 #"Channel" is ID of CANSparkMax Motorcontroller on CAN bus
        
        self.PIDController = self.turningMotor.getPIDController()
        self.InternalEncoder = self.turningMotor.getEncoder()

        self.absEnc = wpilib.AnalogEncoder(absoluteEncoderChannel)
       

        self.driveMotor.setInverted(False) #set inverted to true
        self.turningMotor.setInverted(True)

        self.driveMotor.setIdleMode(rev.CANSparkMax.IdleMode.kCoast)
        self.turningMotor.setIdleMode(rev.CANSparkMax.IdleMode.kCoast)


        # #THIS WAS USED TO REPLACE THE ABOVE CTRE CODE FROM THE REV LIBRARY ON REV MIGRATING (NOT FORM READ THE DOCS)
        # self.PIDController.setP(0.3)
        # self.PIDController.setI(0)
        # self.PIDController.setD(0)
        # self.PIDController.setFF(0)
        # self.PIDController.setOutputRange(-1, 1)
        # #self.PIDController.setIZone(0)                                           #Maybe add later
         
        # absolutePos = self.absEnc.getAbsolutePosition()
        # print(absolutePos) # Print the value as a diagnostic.

        # UPDATE CODE FUCTION IS FROM CTRE
        # self.turningMotor.setSelectedSensorPosition(self.initPos)                                                  #'''SWAP BACK TUES AM'''
        # #print(self.turningMotor.setSelectedSensorPosition(initPos))   
        
        tempPos = self.InternalEncoder.getPosition()                                          #SWAP BACK TUES AM'''

        print(self.TurnCountToDeg(tempPos))

        self.MAX_SPEED = 1    #6380 rpm * (4in * 0.0254 * 3.14) / 6.75 / 60 = 5.02 METERS PER SECOND unweighted
        
        # UPDATE CODE FUCTION FROM CTRE
        # Get CANCoder position
        # absolutePos = self.absEnc.getAbsolutePosition()
        # print(f'absolute {absoluteEncoderChannel}: {absolutePos:.1f}') # The ":.1f" tells it to print only one digit after the decimal.

        # Try to set the Falcon, either to zero or to the absolute position.
        # initPos = 0                                                 
        # initPos = self.DegToTurnCount(absolutePos)


        
    def getState(self) -> SwerveModuleState:
        return SwerveModuleState(self.driveVelocitytToMPS(self.driveMotor.getSelectedSensorVelocity()), Rotation2d.fromDegrees(self.TurnCountToDeg(self.InternalEncoder.getPosition())))           # Rod: needs a rate in meters/sec and turning angle in radians.

    
    def getPosition(self) -> SwerveModulePosition:
        drivePos = self.driveCountToMeters(self.driveMotor.getSelectedSensorPosition())
        wpilib.SmartDashboard.putString('DB/String 4',"Pos_Degrees: {:4.2f}".format(drivePos))
        return SwerveModulePosition(drivePos, Rotation2d.fromDegrees(self.TurnCountToDeg(self.InternalEncoder.getPosition())))           # Rod: needs the distance the wheel has driven (meters), and the turning angle in radians


    def setDesiredState(self, desiredState: SwerveModuleState, open_loop: bool) -> None:
        '''This method is does all the work.  Pass it a desired SwerveModuleState (that is, wheel rim velocity and
        turning direction), and it sets the feedback loops to achieve that.'''

        present_degrees = self.InternalEncoder.getPosition() / (150.0/7.0)
        # present_degrees = self.TurnCountToDeg(self.InternalEncoder.getPosition()) #Soren here, I think instead of tuning motor selected sensor, we might have to use absolute encoder
        present_rotation = Rotation2d.fromDegrees(present_degrees)
        state = self.optimize(desiredState, present_rotation)

        percent_output = state.speed / self.MAX_SPEED
        self.driveMotor.set(0.0)
        percent_output = state.speed / self.MAX_SPEED
        self.turningMotor.set(0.0)

        wpilib.SmartDashboard.putString('DB/String 0',"Enc {:4.3f}".format(present_degrees))
        
    #     if open_loop:
    #          percent_output = state.speed / self.MAX_SPEED
    #          self.driveMotor.set(percent_output)
    #     # else:
    #     #      velocity = self.MPSToDriveVelocity(state.speed)
    #     #      self.driveMotor.setVelocity(velocity, DemandType.ArbitraryFeedForward, self.driveFeedForward.calculate(state.speed))

    #     angle = self.DegToTurnCount(state.angle.degrees())
    #    # self.turningMotor.setPosition(angle)
    #     self.PIDController.setReference(angle, CANSparkLowLevel.ControlType.kPosition)

        # if open_loop:
        #     percent_output = state.speed / self.MAX_SPEED  # TODO: define the max speed in meters/second #DONE
        #     self.driveMotor.set(ControlMode.PercentOutput, percent_output)
        # else:
        #     velocity = self.MPSToDriveVelocity(state.speed)
        #     self.driveMotor.set(ControlMode.Velocity, velocity, DemandType.ArbitraryFeedForward, self.driveFeedForward.calculate(state.speed))

        # angle = self.DegToTurnCount(state.angle.degrees())
        # self.turningMotor.set(ControlMode.Position, angle)

    # Rod: I don't think that this method is ever called, so we may not need to implement it.
    # Also, I'm not sure we want to reset the absolute encoder used for turning control.
    def resetEncoders(self) -> None:
        self.driveEncoder.reset()
        self.turningEncoder.reset()
    
    def DegToTurnCount(self, deg):
        return deg * (2048/360) * self.TURNING_GEAR_RATIO #150/7 : 1
    
    def TurnCountToDeg(self, count):
        return count * (360/2048) / self.TURNING_GEAR_RATIO
    
    def driveCountToMeters(self, x):
        output = (x / 2048) * (self.WHEELDIAMETER * math.pi) / self.DRIVE_GEAR_RATIO #6.75 : 1
        return output
    
    def metersToDriveCount(self, x):
        return (2048/x) / (self.WHEELDIAMETER * math.pi) * self.DRIVE_GEAR_RATIO
    
    def driveVelocitytToMPS(self, x):
        return self.driveCountToMeters(x * 10)     #.getSelectedSensorVelocity measures counts per 1/10 of a second, rather than per second

    def MPSToDriveVelocity(self, x):
        pass

        #Added Jan 26 2024, Line 266 to 269 from utilities
    def joystickscaling(input): #this function helps bring an exponential curve in the joystick value and near the zero value it uses less value and is more flat
        a = 1
        output = a * input * input * input + (1 - a) * input
        return output


    def optimize(self, desired_state: SwerveModuleState, current_angle: Rotation2d) -> SwerveModuleState:
        '''Our own optimize method (instead of SwerveModuleState.optimize())
            There are two ways for a swerve module to reach its goal:
            1) Rotate to its intended steering angle and drive at its intended speed.
            2) Rotate to the mirrored steering angle (subtract 180) and drive at the opposite of its intended speed.
            Optimizing finds the option that requires the smallest rotation by the module.
        '''
        # This method is customized from WPILib's version to include placing in appropriate scope for 
        # CTRE Falcon's onobard control.
        target_angle = self.placeInAppropriate0To360Scope(current_angle.degrees(), desired_state.angle.degrees())
        target_speed = desired_state.speed
        delta = target_angle - current_angle.degrees()

        if abs(delta) > 90:
            target_speed *= -1
            if delta > 90:
                # delta positive
                target_angle -= 180
            else:
                target_angle += 180

        return SwerveModuleState(target_speed, Rotation2d.fromDegrees(target_angle))


    def placeInAppropriate0To360Scope(self, scope_reference: float, new_angle: float) -> float:
        '''Place the new_angle in the range that is a multiple of [0,360] that is closest
           to the scope_reference.
        '''
        lower_offset = scope_reference % 360         # Modulo (remainder) is always positive when divisor (360) is positive.
        lower_bound = scope_reference - lower_offset
        upper_bound = lower_bound + 360

        # Adjust the new_angle to fit between the bounds.
        while new_angle < lower_bound:
            new_angle += 360
        while new_angle > upper_bound:
            new_angle -= 360

        # Adjust new_angle more to make sure it is within 180 degrees of the reference.
        if new_angle - scope_reference > 180:
            new_angle -= 360
        elif new_angle - scope_reference < -180:
            new_angle += 360

        return new_angle
    
    def resetSteering(self):
        """Call this when the steering arrow is pointed straight forward, aligned with the others."""
        self.turningMotor.setSelectedSensorPosition(0.0)

    def toggleDriveMotorInverted(self):
        self.driveMotor.setInverted(not self.driveMotor.getInverted())

