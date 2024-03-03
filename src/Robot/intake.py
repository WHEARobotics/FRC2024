import rev
import wpilib
from wpilib import DutyCycleEncoder
from rev import CANSparkMax, CANSparkLowLevel

class Intake:

    def __init__(self) -> None:

        WRIST_RESTING_ANGLE = 0
        INTAKE_WRIST_ANGLE = 90
        AMP_WRIST_ANGLE = 45 # not figured out yet
        self.WRIST_GEAR_RATIO = 80

        kP = 5e-5
        kP_2 = 0.01
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
        
        self.wrist_motor = rev.CANSparkMax(11, rev._rev.CANSparkLowLevel.MotorType.kBrushless)
        self.intake_motor = rev.CANSparkMax(10, rev._rev.CANSparkLowLevel.MotorType.kBrushless)

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

        self.PIDController_intake = self.intake_motor.getPIDController()
        self.PIDController_intake.setP(kP_2)
        self.PIDController_intake.setI(kI)
        self.PIDController_intake.setD(kD)
        self.PIDController_intake.setIZone(kIz)
        self.PIDController_intake.setFF(kFF)
        self.PIDController_intake.setOutputRange(kMinOutput, kMaxOutput)

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
        self.wrist_out = WRIST_RESTING_ANGLE
        self.wrist_amp = AMP_WRIST_ANGLE

        self.set_speed = 0.0


        self.desired_angle = self.wrist_in
        

      
        self.wrist_encoder = self.wrist_motor.getEncoder()

        self.abs_encoder = DutyCycleEncoder(1)     
        self.abs_enc_offset = 0.0

        self.wrist_encoder.setPosition(self.correctedEncoderPosition() * self.WRIST_GEAR_RATIO)   

    def periodic(self, wrist_pos, intake_control):
        wpilib.SmartDashboard.putString("DB/String 1", f'wrist pos {wrist_pos}')
        if wrist_pos < 0 or wrist_pos > 4:
            self.wrist_motor.set(0.0)
        else:

            

            # if wrist_pos == 1:
            #     desired_angle = self.wrist_out
            # elif wrist_pos == 2:
            #     desired_angle = self.wrist_amp
            if wrist_pos == 3:
                self.wrist_motor.set(0.3)
            elif wrist_pos == 4:
                wpilib.SmartDashboard.putString("DB/String 1", 'wrist down')
                self.wrist_motor.set(-0.3)
            #these are temporary movements for the wrist to be able to do tests i=on the robot using motor power not position control 
            else:
                self.wrist_motor.set(0.0) # desired_angle = self.wrist_in

        
            if intake_control == 1:
                self.set_speed =  0.7
            elif intake_control == 2:
                self.set_speed = -0.3
                 #intake action
            else:
                self.set_speed = 0.0

            self.intake_motor.set(self.set_speed)

            
            # desired_turn_count = self.DegToTurnCount(self.desired_angle)
            # self.PIDController.setReference(desired_turn_count, CANSparkLowLevel.ControlType.kSmartMotion)

            self.motor_pos_degrees = self.TurnCountToDeg(self.wrist_encoder.getPosition())

            self.motor_pos_to_degrees = self.DegToTurnCount(self.wrist_encoder.getPosition())
    
            # wpilib.SmartDashboard.putString('DB/String 6',"desired angle {:4.3f}".format(self.desired_angle))
            # wpilib.SmartDashboard.putString('DB/String 7',"motor_pos {:4.3f}".format(self.motor_pos_degrees))
            # wpilib.SmartDashboard.putString('DB/String 5',"Wrist_motor_pos {:4.3f}".format(self.wrist_encoder.getPosition()))




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

