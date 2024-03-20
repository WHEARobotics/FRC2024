import logging

from rev import CANSparkLowLevel
from wpimath.units import degrees

from controllers import DriveSpeeds
from shooter import ShooterKickerCommands
from intake import IntakeCommands, WristAngleCommands

class RobotCommand:
    pass


class SwerveDriveSpeedCommand(RobotCommand):
    def __init__(self, speeds: DriveSpeeds):
        self.speeds = speeds

    def execute(self, robot):
        robot.swerve.drive(self.speeds.x_speed, self.speeds.y_speed, self.speeds.rot, fieldRelative=True)

class SwerveDriveStopCommand(RobotCommand):
    def __init__(self):
        pass

    def execute(self, robot):
        # ? Something else. Like set brakes?
        robot.swerve.drive(0, 0, 0, fieldRelative=True)


class PivotControlCommand(RobotCommand):
    def __init__(self, shooter_pivot_control):
        self.shooter_pivot_control = shooter_pivot_control

    def execute(self, robot):
        # TODO Do something with shooter_pivot_control
        pass


class IntakeCommand(RobotCommand):
    def __init__(self, intake_control, wrist_position):
        self.intake_control = intake_control
        self.wrist_position = wrist_position

    def execute(self, robot):
        # ? robot.intake.periodic(self.wrist_position, self.intake_control)
        raise NotImplementedError()


class OuttakeCommand(RobotCommand):
    def __init__(self, wrist_position, intake_control, kicker_action, shooter_pivot_control):
        self.wrist_position = wrist_position
        self.intake_control = intake_control
        self.kicker_action = kicker_action
        self.shooter_pivot_control = shooter_pivot_control

    def execute(self, robot):
        raise NotImplementedError()


class KickerAmpShotCommand(RobotCommand):
    def __init__(self):
        self.kicker_action = ShooterKickerCommands.kicker_amp_shot  # amp shot to shoot into the amp

    def execute(self, robot):
        raise NotImplementedError()


class KickerShooterCommand(RobotCommand):
    def __init__(self):
        self.kicker_action = ShooterKickerCommands.kicker_shooter  # shooter shot to shoot into the flywheels

    def execute(self, robot):
        raise NotImplementedError()


class KickerIdleCommand(RobotCommand):
    def __init__(self):
        self.kicker_action = ShooterKickerCommands.kicker_idle

    def execute(self, robot):
        raise NotImplementedError()


class IntakeIdleCommand(RobotCommand):
    def __init__(self):
        self.intake_control = IntakeCommands.idle

    def execute(self, robot):
        raise NotImplementedError()


class WristStowCommand(RobotCommand):
    def __init__(self):
        self.wrist_position = WristAngleCommands.wrist_stow_action

    def execute(self, robot):
        raise NotImplementedError()


class ShooterActionShotCommand(RobotCommand):
    def __init__(self):
        pass

    def execute(self, robot):
        raise NotImplementedError()


class ShooterFlywheelIdleCommand(RobotCommand):
    def __init__(self):
        pass

    def execute(self, robot):
        raise NotImplementedError()


class ShooterFlywheelSpinCommand(RobotCommand):
    def __init__(self):
        pass

    def execute(self, robot):
        raise NotImplementedError()

class ShooterPitchCommand(RobotCommand):
    def __init__(self, desired_pitch : degrees):
        self.desired_pitch = desired_pitch

    def execute(self, robot):
        desired_turn_count = robot.shooter.DegToTurnCount(self.desired_angle)
        robot.shooter.PIDController.setReference(desired_turn_count, CANSparkLowLevel.ControlType.kPosition)

        shooter_state = robot.shooter.get_state()
        if abs(shooter_state.pitch_encoder_pos - self.desired_pitch) < 0.1:
            logging.debug("ShooterPitchCommand: desired pitch reached")
            robot.shooter.set_pitch_motor(0.0)
        if shooter_state.pitch_encoder_pos < self.desired_pitch:
            logging.debug("ShooterPitchCommand: pitch too low")
            robot.shooter.set_pitch_motor(0.3)
        elif shooter_state.pitch_encoder_pos > self.desired_pitch:
            logging.debug("ShooterPitchCommand: pitch too high")
            robot.shooter.set_pitch_motor(-0.3)
        else:
            logging.debug("ShooterPitchCommand: pitch is just right")
            robot.shooter.set_pitch_motor(0.0)

class ShooterPitchStopCommand(RobotCommand):
    def __init__(self):
        pass

    def execute(self, robot):
        #? Something more? Set brake?
        robot.shooter.set_pitch_motor(0.0)

class ShooterPivotAmpCommand(RobotCommand):
    def __init__(self):
        pass

    def execute(self, robot):
        raise NotImplementedError()


class ShooterPivotSubCommand(RobotCommand):
    def __init__(self):
        pass

    def execute(self, robot):
        raise NotImplementedError()

class ShooterWheelSetSpeedCommand(RobotCommand):
    def __init__(self, speed):
        self.speed = speed

    def execute(self, robot):
        robot.shooter.PIDController_flywheel.setReference(self.speed, CANSparkLowLevel.ControlType.kVelocity)


class KickerSetSpeedCommand(RobotCommand):
    def __init__(self, speed):
        self.speed = speed

    def execute(self, robot):
        robot.shooter.kicker.set(self.speed)

class WristAngleMidCommand(RobotCommand):
    def __init__(self):
        pass

    def execute(self, robot):
        raise NotImplementedError()


class GyroSetYawCommand(RobotCommand):
    def __init__(self, yaw):
        self.desired_yaw = yaw

    def execute(self, robot):
        raise NotImplementedError()
