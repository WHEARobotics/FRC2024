import rev
from rev import CANSparkLowLevel
import wpilib
import time
from wpilib import DutyCycleEncoder
from shooterdropcompensation import compensation, compensation_table



class Shooter:
    def __init__(self) -> None:
        
        SHOOTER_AMP_ANGLE = 120
        SHOOTER_START_ANGLE = 0
        SHOOTER_FEEDING_ANGLE = -18

        SHOOTER_SUB_ANGLE = -60


        self.SHOOTER_PIVOT_GEAR_RATIO = 100

        ABSOLUTE_ENCODER_OFFSET = 0.0


        kP = 0.125
        kP_2 = 0.01
        kI = 0.0
        kD = 0.005
        kIz = 0.0
        kFF = 0.0
        kMaxOutput = 1.0
        kMinOutput = -1.0
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
   
        self.absolute_encoder = wpilib.DutyCycleEncoder(3)
        self.absolute_encoder_pos = self.absolute_encoder.getAbsolutePosition()
        self.abs_enc_offset = ABSOLUTE_ENCODER_OFFSET
        self.shooter_wheel_encoder = self.shooter_wheel.getEncoder()

        self.shooter_wheel_2.follow(self.shooter_wheel, True)
        self.shooter_pivot_2.follow(self.shooter_pivot, True)

        self.shooter_pivot.setInverted(False)  
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

        # self.corrected_encoder_pos_1 = self.correctedEncoderPosition()
        # wpilib.SmartDashboard.putString("DB/String 5", f"init enc pos1 {self.corrected_encoder_pos_1:.3f}")


        self.wiggleTimer = wpilib.Timer()
        self.wiggleTimer.start()
        time.sleep(1.5)
        self.corrected_encoder_pos = self.correctedEncoderPosition()
        wpilib.SmartDashboard.putString("DB/String 0", f"init cep {self.corrected_encoder_pos:.3f}")
        self.shooter_pivot_encoder.setPosition(self.corrected_encoder_pos * self.SHOOTER_PIVOT_GEAR_RATIO)
        wpilib.SmartDashboard.putString("DB/String 3", f"init spe pos {self.corrected_encoder_pos * self.SHOOTER_PIVOT_GEAR_RATIO:.3f}")
        



        self.shooter_in = SHOOTER_START_ANGLE
        self.shooter_feeder = SHOOTER_FEEDING_ANGLE
        self.shooter_amp = SHOOTER_AMP_ANGLE
        self.shooter_sub = SHOOTER_SUB_ANGLE

        self.automatic = True
        self.set_speed = 0
        self.desired_angle = self.shooter_feeder

        self.kicker_state = 0



    def periodic(self, distance_to_speaker_m, shooter_pivot_pos, shooter_control, kicker_action):

        self.absolute_encoder_pos = self.absolute_encoder.getAbsolutePosition()

        # drop_compensation_degrees = compensation(compensation_table, distance_to_speaker_m)

        self.corrected_encoder_pos = self.correctedEncoderPosition()
        
        if shooter_pivot_pos > 4:
            self.automatic = False
            if shooter_pivot_pos == 5:
                self.shooter_pivot.set(0.3)
            elif shooter_pivot_pos == 6:
                self.shooter_pivot.set(-0.3)
            else:
                self.shooter_pivot.set(0.0)
        else:
            if shooter_pivot_pos == 1:
                self.automatic = True
                self.desired_angle = self.shooter_in
            elif shooter_pivot_pos == 2:
                self.desired_angle = self.shooter_feeder
            elif shooter_pivot_pos == 3:
                self.desired_angle = self.shooter_amp
            elif shooter_pivot_pos == 4:
                self.desired_angle = self.shooter_sub

        # TODO: Add drop compensation to desired_angle!

        if self.automatic == True:
            desired_turn_count = self.DegToTurnCount(self.desired_angle)
            self.PIDController.setReference(desired_turn_count, CANSparkLowLevel.ControlType.kPosition)
        # the if statement that checks to see if the shooter pivot action is greater than 3. if it is less we use the set reference and if it is
        # greater than 3 we use the set speed command but the set speed will fight with set refernce and the first if statement will stop that.

        # simple state machine for all the shooter pivot motors actions. 4 and 5 will be to manually move for the chain climb
            
        # wpilib.SmartDashboard.putString('DB/String 6',"") #spe position {:4.3f}".format(self.shooter_pivot_encoder.getPosition()))
        # wpilib.SmartDashboard.putString('DB/String 8',"cor abs enc pos {:4.3f}".format(self.corrected_encoder_pos))
        # wpilib.SmartDashboard.putString('DB/String 7', "") #f"drop compensation {drop_compensation_degrees:4.1f}")
        # wpilib.SmartDashboard.putString('DB/String 1', f"internal enc {self.shooter_pivot_encoder.getPosition():4.4f}")
        # wpilib.SmartDashboard.putString('DB/String 2', "")#f"X {self.shooter_pivot_encoder.getPosition():4.4f}")
            
        # this state machine is used to check if we have the note in our kicker and we have let go of the intake to the kicker button
        # once we let go we want the state machine to set the state to 3 to kick it back for a bit away from the flywheels so they 
        # could speed up
            
        if self.kicker_state == 0:
            if  kicker_action ==  1:
                self.kicker_state = 1
            elif kicker_action == 4:
                self.kicker_state = 3

        elif self.kicker_state == 1:
            if self.kicker_state != 1:
                self.kicker_state = 2
                self.wiggleTimer.reset()
                self.wiggleTimer.start()

        elif self.kicker_state == 2:
            if self.wiggleTimer.advanceIfElapsed(0.3):
                self.kicker_state = 0

        elif self.kicker_state == 3:
            if kicker_action != 4:
                self.kicker_state = 0
        else:
            kicker_action = 0

            
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
            # the amp scoring
            self.kicker.set(0.5)
        elif kicker_action == 3:
            self.kicker.set(0.3)
        elif kicker_action == 4:
            self.kicker.set(-0.9)
        elif kicker_action == 0:
            self.kicker.set(0.0)
        else:
            self.kicker.set(0.0)
        
        wpilib.SmartDashboard.putString('DB/String 6',f"{kicker_action}")

        


    

    def DegToTurnCount(self, deg):

        return deg * (1.0/360.0) * self.SHOOTER_PIVOT_GEAR_RATIO #150/7 : 1
    #deg to count 

    def TurnCountToDeg(self, count):
        return count * 360.0 / self.SHOOTER_PIVOT_GEAR_RATIO
    #count to deg

    def correctedEncoderPosition(self):
        AbsEncValue =  self.absolute_encoder.getAbsolutePosition() - self.abs_enc_offset
        if AbsEncValue < -0.5:
            AbsEncValue += 1.0 # we add 1.0 to the encoder value if it returns negative to be able to keep it on the 0-1 range.
        elif AbsEncValue > 0.5:
            AbsEncValue -= 1
        return AbsEncValue