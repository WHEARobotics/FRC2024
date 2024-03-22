import rev
from rev import CANSparkLowLevel
import wpilib
import time
from wpilib import DutyCycleEncoder
from shooterdropcompensation import compensation, compensation_table
import dataclasses
from dataclasses import dataclass

@dataclass(frozen=True)
class ShooterPivotCommands:
    shooter_pivot_in_action = 1
    shooter_pivot_feeder_action = 2
    shooter_pivot_amp_action = 3
    shooter_pivot_sub_action = 4

    shooter_pivot_manual_up = 5
    shooter_pivot_manual_down = 6
    shooter_pivot_idle = 0

@dataclass(frozen=True)
class ShooterKickerCommands:
    kicker_intake = 1
    kicker_amp_shot = 2
    kicker_shot = 3
    kicker_adjustment = 4
    kicker_idle = 0

@dataclass(frozen=True)
class ShooterControlCommands:
    shooter_wheel_idle = 1
    shooter_wheel_intake = 2
    shooter_wheel_outtake = 3


class Shooter:
    def __init__(self) -> None:
        
        SHOOTER_AMP_ANGLE = 114
        SHOOTER_START_ANGLE = 0
        SHOOTER_FEEDING_ANGLE = -60

        SHOOTER_SUB_ANGLE = -63 #orginally -60


        self.SHOOTER_PIVOT_GEAR_RATIO = 100

        ABSOLUTE_ENCODER_OFFSET = 0.080


        kP = 0.11
        kP_2 = 0.005
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
        # these are the different shooter angles 

        self.automatic = True
        # automatic is a mode set to switch between set reference and manual control to not interfere with eachother
        self.set_speed = 0
        self.desired_angle = self.shooter_feeder
        # we might want to change this ti the sub angle to make sure its ready to shoot in autonomous

        self.optical_sensor = wpilib.DigitalInput(0)
        




    def periodic(self, distance_to_speaker_m, shooter_pivot_pos, shooter_control, kicker_action):

        self.absolute_encoder_pos = self.absolute_encoder.getAbsolutePosition()

        self.optical_sensor_is_detected = self.optical_sensor.get()

        # drop_compensation_degrees = compensation(compensation_table, distance_to_speaker_m)

        self.corrected_encoder_pos = self.correctedEncoderPosition()

        self.shooter_pivot_encoder.setPosition(self.corrected_encoder_pos * self.SHOOTER_PIVOT_GEAR_RATIO)

    # setting the desired angles the shooter pivot needs to go to to reach different positions
        if self.automatic:
            if shooter_pivot_pos == ShooterPivotCommands.shooter_pivot_in_action: # 1
                self.desired_angle = self.shooter_in
            elif shooter_pivot_pos == ShooterPivotCommands.shooter_pivot_feeder_action: # 2
                self.desired_angle = self.shooter_feeder
            elif shooter_pivot_pos == ShooterPivotCommands.shooter_pivot_amp_action: # 3
                self.desired_angle = self.shooter_amp
            elif shooter_pivot_pos == ShooterPivotCommands.shooter_pivot_sub_action: # 4
                self.desired_angle = self.shooter_sub
            


            # sets the shooter pivot to move to the desired angle using different control types like position or smart motion control 
            desired_turn_count = self.DegToTurnCount(self.desired_angle)
            self.PIDController.setReference(desired_turn_count, CANSparkLowLevel.ControlType.kPosition)

            # this checks if we are using the manual states in the code to switch from automatic to manual control
            if shooter_pivot_pos == ShooterPivotCommands.shooter_pivot_manual_up or shooter_pivot_pos == ShooterPivotCommands.shooter_pivot_manual_down:
                self.automatic = False
                
            # setting the speeds of the pivot motors to use a manual control for things like adjustment and climbing
        else:
            if shooter_pivot_pos == ShooterPivotCommands.shooter_pivot_manual_up: # 5
                self.shooter_pivot.set(0.3)
            elif shooter_pivot_pos == ShooterPivotCommands.shooter_pivot_manual_down: # 6
                self.shooter_pivot.set(-0.3)
            else:
                self.shooter_pivot.set(0.0)
            
            # what this does is it checks if we have not set a command to go to automatic and checks if we are not using any of the 2 manual up or
            # down and if it is not zero either to use zero as the else to not have the pivot move when we let go of the button
            if shooter_pivot_pos != ShooterPivotCommands.shooter_pivot_manual_up and shooter_pivot_pos != ShooterPivotCommands.shooter_pivot_manual_down and shooter_pivot_pos != ShooterPivotCommands.shooter_pivot_idle:   
                self.automatic = True
           
            
           

        # TODO: Add drop compensation to desired_angle!

        # the if statement that checks to see if the shooter pivot action is greater than 3. if it is less we use the set reference and if it is
        # greater than 3 we use the set speed command but the set speed will fight with set refernce and the first if statement will stop that.

        # simple state machine for all the shooter pivot motors actions. 4 and 5 will be to manually move for the chain climb
            
        # wpilib.SmartDashboard.putString('DB/String 6',"") #spe position {:4.3f}".format(self.shooter_pivot_encoder.getPosition()))
        wpilib.SmartDashboard.putString('DB/String 8',"cor abs enc pos {:4.3f}".format(self.corrected_encoder_pos))
        # wpilib.SmartDashboard.putString('DB/String 7', "") #f"drop compensation {drop_compensation_degrees:4.1f}")
        wpilib.SmartDashboard.putString('DB/String 1', f"internal enc {self.shooter_pivot_encoder.getPosition():4.4f}")
        # wpilib.SmartDashboard.putString('DB/String 2', "")#f"X {self.shooter_pivot_encoder.getPosition():4.4f}")
            

            
        if shooter_control == ShooterControlCommands.shooter_wheel_idle: #0
            self.set_speed = 0.0
        elif shooter_control == ShooterControlCommands.shooter_wheel_intake: #1
                self.set_speed = 0.5 # intake for shooter speed
        elif shooter_control == ShooterControlCommands.shooter_wheel_outtake: #2
            self.set_speed = -1.0 # maximum rpm for the neo motor
            # self.PIDController_flywheel.setReference(self.set_speed, CANSparkLowLevel.ControlType.kVelocity)
        else:
            self.set_speed = 0.0
        self.shooter_wheel.set(self.set_speed)
        

        # intake with kicker wheels when handoff
        if kicker_action == ShooterKickerCommands.kicker_intake: # 1
            if self.optical_sensor_is_detected == 0:
                self.kicker.set(-0.4)
            else:
                self.wiggleTimer.reset()
                self.wiggleTimer.start()
                self.kicker.set(0.4)
                if self.wiggleTimer.advanceIfElapsed(0.5):
                    self.kicker.set(0.0)
                

        # the amp scoring
        elif kicker_action == ShooterKickerCommands.kicker_amp_shot: # 2:
            self.kicker.set(0.2)
        # kicker shoot 
        elif kicker_action == ShooterKickerCommands.kicker_shot: # 3
            self.kicker.set(-0.9)
        # the 4th state for the kicker is to push the note back and adjust it so it is not hitting the fly wheels too early
        elif kicker_action == ShooterKickerCommands.kicker_adjustment: # 4
            self.kicker.set(0.4)
        else:
            self.kicker.set(0.0)

        # kicker state machine
        
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