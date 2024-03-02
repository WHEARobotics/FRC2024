import rev
from rev import CANSparkLowLevel
import wpilib
from wpilib import DutyCycleEncoder
from shooterdropcompensation import compensation, compensation_table



class Shooter:
    def __init__(self) -> None:
        
        SHOOTER_SUB_ANGLE = 180
        SHOOTER_START_ANGLE = 0
        SHOOTER_MAX_ANGLE = 90
        self.WRIST_GEAR_RATIO = 1

        ABSOLUTE_ENCODER_OFFSET = 0

        kP = 0.1
        kP_2 = 0.01
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
   
        self.absolute_encoder = wpilib.DutyCycleEncoder(1)
        self.absolute_encoder_pos = self.absolute_encoder.getAbsolutePosition()
        self.abs_enc_offset = ABSOLUTE_ENCODER_OFFSET

        self.shooter_wheel_2.follow(self.shooter_wheel, True)
        self.shooter_pivot_2.follow(self.shooter_pivot, True)

        self.shooter_pivot.setInverted(True)  
        #self.motor2.setInverted(True)
        self.shooter_wheel.setInverted(True)
        self.shooter_wheel_2.setInverted(False)
        self.kicker.setInverted(False)

        self.shooter_pivot.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus3, 500)
        self.shooter_pivot.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus4, 500)
        self.shooter_pivot.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus5, 500)
        self.shooter_pivot.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus6, 500)

        self.shooter_pivot_2.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus0, 100)        
        self.shooter_pivot_2.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus1, 500)
        self.shooter_pivot_2.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus2, 500)
        self.shooter_pivot_2.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus3, 500)
        self.shooter_pivot_2.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus4, 500)
        self.shooter_pivot_2.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus5, 500)
        self.shooter_pivot_2.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus6, 500)

        self.shooter_wheel.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus3, 500)
        self.shooter_wheel.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus4, 500)
        self.shooter_wheel.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus5, 500)
        self.shooter_wheel.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus6, 500)
        
        
        self.shooter_wheel_2.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus0, 100)
        self.shooter_wheel_2.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus1, 500)
        self.shooter_wheel_2.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus2, 500)
        self.shooter_wheel_2.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus3, 500)
        self.shooter_wheel_2.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus4, 500)
        self.shooter_wheel_2.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus5, 500)
        self.shooter_wheel_2.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus6, 500)

        self.kicker.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus1, 500)
        self.kicker.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus2, 500)
        self.kicker.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus3, 500)
        self.kicker.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus4, 500)
        self.kicker.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus5, 500)
        self.kicker.setPeriodicFramePeriod(CANSparkLowLevel.PeriodicFrame.kStatus6, 500)
        #the status code here give the difrent packed from the encoders serten speed to not overload the CANBuss. defult speed is 20ms.
       
        self.shooter_pivot.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.shooter_pivot_2.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        self.shooter_wheel.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)
        self.shooter_wheel_2.setIdleMode(rev._rev.CANSparkMax.IdleMode.kCoast)
        self.kicker.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)


        self.shooter_pivot_encoder = self.shooter_pivot.getEncoder()
        self.shooter_pivot_encoder.setPosition(0.0)

        self.PIDController_flywheel = self.shooter_wheel.getPIDController()
        self.PIDController_flywheel.setP(kP_2)
        self.PIDController_flywheel.setI(kI)
        self.PIDController_flywheel.setD(kD)
        self.PIDController_flywheel.setIZone(kIz)
        self.PIDController_flywheel.setFF(kFF)
        self.PIDController_flywheel.setOutputRange(kMinOutput,kMaxOutput)

        self.PIDController_flywheel.setOutputRange(-1, 1)
        #sets the maximum output power that could be used for the voltage control

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

        self.shooter_pivot_encoder.setPosition(self.correctedEncoderPosition() * self.WRIST_GEAR_RATIO)   



        self.shooter_in = SHOOTER_START_ANGLE
        self.shooter_out = SHOOTER_MAX_ANGLE
        self.shooter_sub = SHOOTER_SUB_ANGLE

        self.automatic = True
        self.set_speed = 0

    def periodic(self, shooter_pivot_pos, shooter_control, kicker_action):
            
      

        desired_angle = self.shooter_in

        if shooter_pivot_pos > 3:
            self.automatic = False
            if shooter_pivot_pos == 4:
                self.shooter_pivot.set(0.3)
            elif shooter_pivot_pos == 5:
                self.shooter_pivot.set(-0.3)
            else:
                self.shooter_pivot.set(0.0)
        else:
            if shooter_pivot_pos == 1:
                self.automatic = True
                desired_angle = self.shooter_in
            elif shooter_pivot_pos == 2:
                desired_angle = self.shooter_out
            elif shooter_pivot_pos == 3:
                desired_angle = self.shooter_sub
            else:
                self.shooter_pivot.set(0.0)

        if self.automatic == True:
            desired_turn_count = self.DegToTurnCount(desired_angle)
            self.PIDController.setReference(desired_turn_count, CANSparkLowLevel.ControlType.kPosition)
        # the if statement that checks to see if the shooter pivot action is greater than 3. if it is less we use the set reference and if it is
        # greater than 3 we use the set speed command but the set speed will fight with set refernce and the first if statement will stop that.

        # simple state machine for all the shooter pivot motors actions. 4 and 5 will be to manually move for the chain climb
            
        wpilib.SmartDashboard.putString('DB/String 6',"desired angle {:4.3f}".format(self.shooter_pivot_encoder.getPosition()))
            
        
        
        if shooter_control > 0:
            shooter_automatic = True
            if shooter_control == 1:
                self.set_speed = 2500 # intake for shooter speed
            elif shooter_control == 2:
                self.set_speed = -5700 # maximum rpm for the neo motor
            self.PIDController_flywheel.setReference(self.set_speed, CANSparkLowLevel.ControlType.kVelocity)
        else:
                self.shooter_wheel.set(0.0)
                self.kicker.set(0.0)

        if kicker_action == 1:
            self.kicker.set(-0.3)
        elif kicker_action == 2:
            self.kicker.set(0.5)
        else:
            self.kicker.set(0.0) 

    

    def DegToTurnCount(self, deg):

        return deg * (1.0/360.0) * self.WRIST_GEAR_RATIO #150/7 : 1
    #deg to count 

    def TurnCountToDeg(self, count):
        return count * 360.0 / self.WRIST_GEAR_RATIO
    #count to deg

    def correctedEncoderPosition(self):
        AbsEncValue =  self.absolute_encoder_pos - self.abs_enc_offset
        if AbsEncValue < 0.0:
            AbsEncValue += 1.0 # we add 1.0 to the encoder value if it returns negative to be able to keep it on the 0-1 range.
        return AbsEncValue
    