import rev
import wpilib
from wpilib import DutyCycleEncoder
from rev import CANSparkMax, CANSparkLowLevel

class Intake:

    def __init__(self) -> None:

        INTAKE_WRIST_ANGLE = 0
        OUTPUT_WRIST_ANGLE = 90
        AMP_WRIST_ANGLE = 45 # not figured out yet
        self.WRIST_GEAR_RATIO = 5

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
        
        self.wrist_motor = rev.CANSparkMax(10, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.intake_motor = rev.CANSparkMax(11, rev._rev.CANSparkLowLevel.MotorType.kBrushless)


        #This function slows dow can states frames to not over load the canbuss
        self.wrist_motor.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus3, 500)
        self.wrist_motor.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus4, 500)
        self.wrist_motor.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus5, 500)
        self.wrist_motor.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus6, 500)

        self.intake_motor.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus0, 100)
        self.intake_motor.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus1, 500)
        self.intake_motor.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus2, 500)
        self.intake_motor.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus3, 500)
        self.intake_motor.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus4, 500)
        self.intake_motor.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus5, 500)
        self.intake_motor.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus6, 500)

        self.PIDController = self.wrist_motor.getPIDController()
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



        self.wrist_in = INTAKE_WRIST_ANGLE
        self.wrist_out = OUTPUT_WRIST_ANGLE
        self.wrist_amp = AMP_WRIST_ANGLE
        

      
        self.wrist_encoder = self.wrist_motor.getEncoder()

        self.abs_encoder = DutyCycleEncoder(0)     
        self.abs_enc_offset = 0.0

        self.wrist_encoder.setPosition(self.correctedEncoderPosition() * self.WRIST_GEAR_RATIO)   

    def periodic(self, wrist_pos):
        if wrist_pos < 0 or wrist_pos > 3:
            self.wrist_motor.set(0.0)
        else:

            desired_angle = self.wrist_in

            if wrist_pos == 1:
                desired_angle = self.wrist_in
            elif wrist_pos == 2:
                desired_angle = self.wrist_out
            elif wrist_pos == 3:
                desired_angle = self.wrist_amp
            
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

