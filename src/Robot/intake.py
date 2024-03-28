import rev
import wpilib
from rev import CANSparkMax, CANSparkLowLevel
from dataclasses import dataclass

@dataclass(frozen=True)
class WristAngleCommands:
    wrist_stow_action = 1
    wrist_intake_action = 2
    wrist_mid_action = 3
    wrist_amp_angle = 4

@dataclass(frozen=True)
class IntakeCommands:
    idle = 0
    intake_action = 1
    outtake_action = 2
    outtake_shot_action = 3

class Intake:

    def __init__(self) -> None:

        self.WRIST_STOWED_ANGLE = 0   # Starting position inside the robot.
        self.INTAKE_WRIST_ANGLE = 158 # Intake deployed to grab a note.
        self.WRIST_MID_ANGLE = 60     # Out of the way so shooter can take a subwoofer shot.
        self.WRIST_AMP = 46
        self.WRIST_GEAR_RATIO = 80

        kP = 0.075
        kP_2 = 0.01
        kI = 0
        kD = 0.0
        kIz = 0.0
        kFF = 0.0
        kMaxOutput = 0.6
        kMinOutput = -0.6
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
        self.wrist_motor.setInverted(False) 

        # This function slows down CAN state frames to not overload the CANbus by slowing down the amount of things are needed to be checked
        # in a certain amount of time and we slowed down the amount of time needed for less important things on the canbus
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

        # this sets up the the pid control for the intake and sets things up for pid and smart motion control  
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

        
        self.set_speed = 0.0

        self.intake_move_on_init = True


        self.desired_angle = self.WRIST_STOWED_ANGLE

        self.wrist_limit_switch = self.wrist_motor.getReverseLimitSwitch(rev.SparkMaxLimitSwitch.Type.kNormallyOpen)
      
        self.wrist_encoder = self.wrist_motor.getEncoder()

    def periodic(self, wrist_pos, intake_control):
        wpilib.SmartDashboard.putString("DB/String 1", f'wrist pos {wrist_pos}')


        if self.wrist_limit_switch.get() == True:
            self.wrist_encoder.setPosition(0.0)
            self.desired_angle = self.WRIST_STOWED_ANGLE
            self.intake_move_on_init = False
            # print("TRUE")


        if self.intake_move_on_init == True:
            self.wrist_motor.set(-0.2)
        else:
            if wrist_pos == WristAngleCommands.wrist_stow_action:
                self.desired_angle = self.WRIST_STOWED_ANGLE
            elif wrist_pos == WristAngleCommands.wrist_intake_action:
                self.desired_angle = self.INTAKE_WRIST_ANGLE
            elif wrist_pos == WristAngleCommands.wrist_mid_action:
                self.desired_angle = self.WRIST_MID_ANGLE
            elif wrist_pos == WristAngleCommands.wrist_amp_angle:
                self.desired_angle = self.WRIST_AMP
            else:
                self.desired_angle = self.WRIST_STOWED_ANGLE
            
            desired_turn_count = self.DegToTurnCount(self.desired_angle)
            self.PIDController.setReference(desired_turn_count, CANSparkLowLevel.ControlType.kPosition)
            
            wpilib.SmartDashboard.putString('DB/String 2',f"wrist_go_pos{desired_turn_count - self.wrist_encoder.getPosition():1.3f}")

            self.motor_pos_degrees = self.TurnCountToDeg(self.wrist_encoder.getPosition())

            self.motor_pos_to_degrees = self.DegToTurnCount(self.wrist_encoder.getPosition())


        if intake_control == IntakeCommands.intake_action:
            self.set_speed =  -0.5
            self.intake_state = 1
        elif intake_control == IntakeCommands.outtake_action:
            self.set_speed = 0.3
                #intake action
        elif intake_control == IntakeCommands.outtake_shot_action:
            self.set_speed = 0.7
        else:
            self.set_speed = 0.0

        self.intake_motor.set(self.set_speed)


    def DegToTurnCount(self, deg):
        '''Convert intake "wrist" angle in degrees to turns (rotations) of motor shaft.'''
        return deg * (1.0/360.0) * self.WRIST_GEAR_RATIO

    def TurnCountToDeg(self, count):
        '''Convert turns (rotations) of motor shaft to angle in degrees of intake "wrist".'''
        return count * 360.0 / self.WRIST_GEAR_RATIO

