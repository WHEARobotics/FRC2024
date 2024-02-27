import rev
from rev import CANSparkLowLevel
import wpilib
from wpilib import DutyCycleEncoder

class Shooter:
    def __init__(self) -> None:
        
        SHOOTER_SUB_ANGLE = 180
        SHOOTER_START_ANGLE = 0
        SHOOTER_MAX_ANGLE = 90
        self.WRIST_GEAR_RATIO = 1

        kP = 0.1
        kI = 0.0
        kD = 0.0
        kIz = 0.0
        kFF = 0.0
        kMaxOutput = 0.2
        kMinOutput = -0.2
        maxRPM = 5700

        maxVel = 10
        minVel = 0
        maxAcc = 5

        allowedErr = 0

        self.shooter_pivot = rev.CANSparkMax(15, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.shooter_pivot_2 = rev.CANSparkMax(13, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.shooter_wheel = rev.CANSparkMax(12, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.shooter_wheel_2 = rev.CANSparkMax(14, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.kicker = rev.CANSparkMax(16, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        
        self.shooter_wheel_2.follow(self.shooter_wheel, True)
        self.shooter_pivot_2.follow(self.shooter_pivot, True)

        self.shooter_pivot.setInverted(True)  
        #self.motor2.setInverted(True)
        self.shooter_wheel.setInverted(True)
        self.shooter_wheel_2.setInverted(False)
        self.kicker.setInverted(False)

       
        self.shooter_pivot.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)
        self.shooter_pivot.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)
        self.shooter_wheel.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.shooter_wheel.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.kicker.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)

        self.shooter_pivot_encoder = self.shooter_pivot.getEncoder()
        self.shooter_pivot_encoder.setPosition(0.0)

        
        self.PIDController = self.shooter_pivot.getPIDController()
        self.PIDController.setP(kP)
        self.PIDController.setI(kI)
        self.PIDController.setD(kD)
        self.PIDController.setIZone(kIz)
        self.PIDController.setFF(kFF)
        self.PIDController.setOutputRange(kMinOutput, kMaxOutput)

        smartmotionslot = 0
        self.PIDController.setSmartMotionMaxAccel(maxAcc, smartmotionslot)
        self.PIDController.setSmartMotionMaxVelocity(maxVel, smartmotionslot)
        self.PIDController.setSmartMotionMinOutputVelocity(minVel, smartmotionslot)
        self.PIDController.setSmartMotionAllowedClosedLoopError(allowedErr, smartmotionslot)

        

        self.abs_encoder = DutyCycleEncoder(1)     
        self.abs_enc_offset = 0.0

        self.shooter_pivot_encoder.setPosition(self.correctedEncoderPosition() * self.WRIST_GEAR_RATIO)   

        self.shooter_in = SHOOTER_START_ANGLE
        self.shooter_out = SHOOTER_MAX_ANGLE
        self.shooter_sub = SHOOTER_SUB_ANGLE

    def periodic(self, shooter_pivot_pos, shooter_control):
            
        if shooter_pivot_pos < 0 or shooter_pivot_pos > 3:
            self.shooter_pivot.set(0.0)
        else:

            desired_angle = self.shooter_in

            if shooter_pivot_pos == 1:
                desired_angle = self.shooter_in
            elif shooter_pivot_pos == 2:
                desired_angle = self.shooter_out
            elif shooter_pivot_pos == 3:
                desired_angle = self.shooter_sub
            elif shooter_pivot_pos == 4:
                self.shooter_pivot.set(0.3)
            elif shooter_pivot_pos == 5:
                self.shooter_pivot.set(-0.3)
            # simple state machine for all the shooter pivot motors actions. 4 and 5 will be to manually move for the chain climb
                
            if shooter_control == 1:
                self.shooter_wheel.set(-0.1)
                self.kicker.set(-0.15)
            if shooter_control == 2:
                self.shooter_wheel.set(0.5)
                self.kicker.set(0.15)
            if shooter_control == 3:
                self.shooter_wheel.set(1.0)
            else:
                self.shooter_wheel.set(0.0)
            
            desired_turn_count = self.DegToTurnCount(desired_angle)
            self.PIDController.setReference(desired_turn_count, CANSparkLowLevel.ControlType.kPosition)

    def DegToTurnCount(self, deg):

        return deg * (1.0/360.0) * self.WRIST_GEAR_RATIO #150/7 : 1
    #deg to count 

    def TurnCountToDeg(self, count):
        return count * 360.0 / self.WRIST_GEAR_RATIO
    #count to deg

    def correctedEncoderPosition(self):
        AbsEncValue =  self.abs_encoder.getAbsolutePosition() - self.abs_enc_offset
        if AbsEncValue < 0.0:
            AbsEncValue += 1.0 # we add 1.0 to the encoder value if it returns negative to be able to keep it on the 0-1 range.
        return AbsEncValue