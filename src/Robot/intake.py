import rev
import wpilib
from wpilib import DutyCycleEncoder
from rev import CANSparkMax, CANSparkLowLevel

class Intake:

    def __init__(self) -> None:

        INTAKE_WRIST_ANGLE = 90
        OUTPUT_WRIST_ANGLE = 0
        AMP_WRIST_ANGLE = 45 # not figured out yet
        self.WRIST_GEAR_RATIO = 1

        kP = 5e-5
        kI = 1e-6
        kD = 0.0
        kIz = 0.0
        kFF = 0.0
        kMaxOutput = 1.0
        kMinOutput = -1.0
        maxRPM = 5700

        maxVel = 2000
        minVel = 0
        maxAcc = 1500

        allowedErr = 0
        
        self.wrist_motor = rev.CANSparkMax(10, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.intake_motor = rev.CANSparkMax(11, rev._rev.CANSparkLowLevel.MotorType.kBrushless)

        self.intake_motor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.wrist_motor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)

        self.intake_motor.setInverted(True)
        self.wrist_motor.setInverted(True) 



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


        self.desired_angle = self.wrist_in
        

      
        self.wrist_encoder = self.wrist_motor.getEncoder()

        self.abs_encoder = DutyCycleEncoder(0)     
        self.abs_enc_offset = 0.0

        self.wrist_encoder.setPosition(self.correctedEncoderPosition() * self.WRIST_GEAR_RATIO)   

    def periodic(self, wrist_pos, intake_control):
        if wrist_pos < 0 or wrist_pos > 3:
            self.wrist_motor.set(0.0)
        else:

            

            # if wrist_pos == 1:
            #     desired_angle = self.wrist_out
            # elif wrist_pos == 2:
            #     desired_angle = self.wrist_amp
            if wrist_pos == 3:
                self.wrist_motor.set(0.2)
            elif wrist_pos == 4:
                self.wrist_motor.set(-0.2)
            #these are temporary movements for the wrist to be able to do tests i=on the robot using motor power not position control 
            else:
                self.wrist_motor.set(0.0) # desired_angle = self.wrist_in

            if intake_control == 1:
                self.intake_motor.set(-0.15)
            elif intake_control == 2:
                self.intake_motor.set(0.6)
            else: 
                self.intake_motor.set(0.0)

            
            desired_turn_count = self.DegToTurnCount(self.desired_angle)
            self.PIDController.setReference(desired_turn_count, CANSparkLowLevel.ControlType.kSmartMotion)

            self.motor_pos_degrees = self.TurnCountToDeg(self.wrist_encoder.getPosition())
    
            wpilib.SmartDashboard.putString('DB/String 6',"desired angle {:4.3f}".format(self.desired_angle))
            wpilib.SmartDashboard.putString('DB/String 7',"motor_pos {:4.3f}".format(self.motor_pos_degrees))


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

