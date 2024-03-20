import rev
from rev import CANSparkLowLevel
import wpilib
import time


from shootercommands import ShooterPitchCommand, ShooterWheelSetSpeedCommand

from ObjectOrientedStateMachineRobot.shootercommands import KickerSetSpeedCommand
from dataclasses import dataclass


@dataclass(frozen=True)
class ShooterPivotCommands:
    shooter_pivot_in_action = 1
    shooter_pivot_feeder_action = 2
    shooter_pivot_amp_action = 3
    shooter_pivot_sub_action = 4

    shooter_pivot_manual_up = 5
    shooter_pivot_manual_down = 6


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


@dataclass(frozen=True)
class ShooterState:
    absolute_encoder_pos: float
    shooter_pivot_encoder_pos: float
    shooter_wheel_encoder_pos: float


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
        # maxRPM = 5700

        maxVel = 10
        minVel = 0
        maxAcc = 5

        allowedErr = 0

        self.shooter_pivot = rev.CANSparkMax(15, rev.CANSparkLowLevel.MotorType.kBrushless)
        self.shooter_pivot_2 = rev.CANSparkMax(13, rev.CANSparkLowLevel.MotorType.kBrushless)
        self.shooter_wheel = rev.CANSparkMax(12, rev.CANSparkLowLevel.MotorType.kBrushless)
        self.shooter_wheel_2 = rev.CANSparkMax(14, rev.CANSparkLowLevel.MotorType.kBrushless)
        self.kicker = rev.CANSparkMax(16, rev.CANSparkLowLevel.MotorType.kBrushless)

        self.absolute_encoder = wpilib.DutyCycleEncoder(3)
        self.absolute_encoder_pos = self.absolute_encoder.getAbsolutePosition()
        self.abs_enc_offset = ABSOLUTE_ENCODER_OFFSET
        self.shooter_wheel_encoder = self.shooter_wheel.getEncoder()

        self.shooter_wheel_2.follow(self.shooter_wheel, True)
        self.shooter_pivot_2.follow(self.shooter_pivot, True)

        self.shooter_pivot.setInverted(False)
        # self.motor2.setInverted(True)
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
        # the status code here give the different packed from the encoders certain speed to not overload the CANBuss.
        # default speed is 20ms.

        self.shooter_pivot.setIdleMode(rev.CANSparkMax.IdleMode.kBrake)
        self.shooter_pivot_2.setIdleMode(rev.CANSparkMax.IdleMode.kBrake)
        self.shooter_wheel.setIdleMode(rev.CANSparkMax.IdleMode.kCoast)
        self.shooter_wheel_2.setIdleMode(rev.CANSparkMax.IdleMode.kCoast)
        self.kicker.setIdleMode(rev.CANSparkMax.IdleMode.kBrake)

        self.shooter_pivot_encoder = self.shooter_pivot.getEncoder()

        self.PIDController_flywheel = self.shooter_wheel.getPIDController()
        self.PIDController_flywheel.setP(kP_2)
        self.PIDController_flywheel.setI(kI)
        self.PIDController_flywheel.setD(kD)
        self.PIDController_flywheel.setIZone(kIz)
        self.PIDController_flywheel.setFF(kFF)
        self.PIDController_flywheel.setOutputRange(kMinOutput, kMaxOutput)

        self.PIDController_flywheel.setOutputRange(-1, 1)
        # sets the maximum output power that could be used for the voltage control

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
        self.corrected_encoder_pos = self.corrected_encoder_position()
        wpilib.SmartDashboard.putString("DB/String 0", f"init cep {self.corrected_encoder_pos:.3f}")
        self.shooter_pivot_encoder.setPosition(self.corrected_encoder_pos * self.SHOOTER_PIVOT_GEAR_RATIO)
        wpilib.SmartDashboard.putString("DB/String 3",
                                        f"init spe pos {self.corrected_encoder_pos * self.SHOOTER_PIVOT_GEAR_RATIO:.3f}")

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

    def flywheel_is_ready(self):
        # TODO: This should return false if the flywheel is not spinning at desired rate
        return True

    def get_state(self):
        absolute_encoder_pos = self.absolute_encoder.getAbsolutePosition()
        shooter_pivot_encoder_pos = self.shooter_pivot_encoder.getPosition()
        shooter_wheel_encoder_pos = self.shooter_wheel_encoder.getPosition()
        return ShooterState(absolute_encoder_pos, shooter_pivot_encoder_pos, shooter_wheel_encoder_pos)

    def get_teleop_periodic_commands(self, shooter_pivot_command, shooter_control, kicker_action):
        commands = []
        # setting the desired angles the shooter pivot needs to go to to reach different positions
        commands += self.pivot_commands(shooter_pivot_command)

        commands += self.shooter_commands(shooter_control)
        self.shooter_commands(shooter_control)

        commands += self.kicker_commands(kicker_action)

        return commands

    @staticmethod
    def shooter_commands(shooter_control):
        commands = []
        if shooter_control != ShooterControlCommands.shooter_wheel_idle:  # 0
            if shooter_control == ShooterControlCommands.shooter_wheel_intake:  # 1
                commands.append(ShooterWheelSetSpeedCommand(2500))  # intake for shooter speed
            elif shooter_control == ShooterControlCommands.shooter_wheel_outtake:  # 2
                commands.append(ShooterWheelSetSpeedCommand(-5700))  # Maximum RPM for the neo motor

        else:
            commands.append(ShooterWheelSetSpeedCommand(0.0))
            commands.append(KickerSetSpeedCommand(0.0))
        return commands

    def pivot_commands(self, shooter_pivot_command):
        commands = []
        if self.automatic:
            if shooter_pivot_command == ShooterPivotCommands.shooter_pivot_in_action:  # 1
                commands.append(ShooterPitchCommand(self.shooter_in))
            elif shooter_pivot_command == ShooterPivotCommands.shooter_pivot_feeder_action:  # 2
                commands.append(ShooterPitchCommand(self.shooter_feeder))
            elif shooter_pivot_command == ShooterPivotCommands.shooter_pivot_amp_action:  # 3
                commands.append(ShooterPitchCommand(self.shooter_amp))
            elif shooter_pivot_command == ShooterPivotCommands.shooter_pivot_sub_action:  # 4
                # TODO: Add drop compensation to desired_angle!
                drop_compensation_degrees = 0  # drop_compensation_degrees

                commands.append(ShooterPitchCommand(self.shooter_sub + drop_compensation_degrees))

            # this checks if we are using the manual states in the code to switch from automatic to manual control
            if (shooter_pivot_command == ShooterPivotCommands.shooter_pivot_manual_up
                    or shooter_pivot_command == ShooterPivotCommands.shooter_pivot_manual_down):
                self.automatic = False

            # setting the speeds of the pivot motors to use a manual control for things like adjustment and climbing
        else:
            if shooter_pivot_command == ShooterPivotCommands.shooter_pivot_manual_up:  # 5
                commands.append(ShooterPitchCommand(self.shooter_pivot_encoder.getPosition() + 0.3))
            elif shooter_pivot_command == ShooterPivotCommands.shooter_pivot_manual_down:  # 6
                commands.append(ShooterPitchCommand(self.shooter_pivot_encoder.getPosition() - 0.3))
            else:
                commands.append(ShooterPitchCommand(self.shooter_pivot_encoder.getPosition()))

            # what this does is it checks if we have not set a command to go to automatic and checks if we are not
            # using any of the 2 manual up orndown and if it is not zero either to use zero as the else to not have
            # the pivot move when we let go of the button
            if (shooter_pivot_command != ShooterPivotCommands.shooter_pivot_manual_up
                    and shooter_pivot_command != ShooterPivotCommands.shooter_pivot_manual_down
                    and shooter_pivot_command != self.shooter_pivot_idle):
                self.automatic = True
        return commands

    @staticmethod
    def kicker_commands(kicker_action):
        commands = []
        # intake with kicker wheels when handoff
        if kicker_action == ShooterKickerCommands.kicker_intake:  # 1
            commands.append(KickerSetSpeedCommand(0.3))
            # self.kicker.set(-0.3)
        # the amp scoring
        elif kicker_action == ShooterKickerCommands.kicker_amp_shot:  # 2:
            # self.kicker.set(0.5)
            commands.append(KickerSetSpeedCommand(0.5))
        # kicker shoot
        elif kicker_action == ShooterKickerCommands.kicker_shot:  # 3
            # self.kicker.set(-0.9)
            commands.append(KickerSetSpeedCommand(-0.9))
        # the 4th state for the kicker is to push the note back and adjust it so it is not hitting
        # the fly wheels too early
        elif kicker_action == ShooterKickerCommands.kicker_adjustment:  # 4
            # self.kicker.set(0.3)
            commands.append(KickerSetSpeedCommand(0.3))
        else:
            commands.append(KickerSetSpeedCommand(0.0))

        # kicker state machine

        wpilib.SmartDashboard.putString('DB/String 6', f"{kicker_action}")
        return commands

    def deg_to_turn_count(self, deg):

        return deg * (1.0 / 360.0) * self.SHOOTER_PIVOT_GEAR_RATIO  # 150/7 : 1

    # deg to count

    def turn_count_to_deg(self, count):
        return count * 360.0 / self.SHOOTER_PIVOT_GEAR_RATIO

    # count to deg

    def corrected_encoder_position(self):
        AbsEncValue = self.absolute_encoder.getAbsolutePosition() - self.abs_enc_offset
        if AbsEncValue < -0.5:
            AbsEncValue += 1.0  # we add 1.0 to the encoder value if it returns negative to be able to
            # keep it on the 0-1 range.
        elif AbsEncValue > 0.5:
            AbsEncValue -= 1
        return AbsEncValue
