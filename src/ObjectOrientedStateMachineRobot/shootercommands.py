import logging

from rev import CANSparkLowLevel
from wpimath.units import degrees

from ObjectOrientedStateMachineRobot.robot import ObjectOrientedRobot
from ObjectOrientedStateMachineRobot.robotcommand import RobotCommand
from shooter import ShooterKickerCommands


class KickerAmpShotCommand(RobotCommand):
    def __init__(self):
        super().__init__()
        self.kicker_action = ShooterKickerCommands.kicker_amp_shot  # amp shot to shoot into the amp

    def execute(self, robot: ObjectOrientedRobot) -> None:
        raise NotImplementedError()


class KickerShooterCommand(RobotCommand):
    def __init__(self):
        super().__init__()

    def execute(self, robot: ObjectOrientedRobot) -> None:
        raise NotImplementedError()


class KickerIdleCommand(RobotCommand):
    def __init__(self):
        super().__init__()
        self.kicker_action = ShooterKickerCommands.kicker_idle

    def execute(self, robot: ObjectOrientedRobot) -> None:
        raise NotImplementedError()

class KickerIntakeCommand(RobotCommand):
    def __init__(self):
        super().__init__()
        self.kicker_action = ShooterKickerCommands.kicker_intake

    def execute(self, robot: ObjectOrientedRobot) -> None:
        raise NotImplementedError()

class ShooterActionShotCommand(RobotCommand):
    def __init__(self):
        super().__init__()
        pass

    def execute(self, robot: ObjectOrientedRobot) :
        raise NotImplementedError()


class ShooterFlywheelIdleCommand(RobotCommand):
    def __init__(self):
        super().__init__()
        pass

    def execute(self, robot: ObjectOrientedRobot) -> None:
        raise NotImplementedError()


class ShooterFlywheelSpinCommand(RobotCommand):
    def __init__(self):
        super().__init__()
        pass

    def execute(self, robot: ObjectOrientedRobot) -> None:
        raise NotImplementedError()


class ShooterPitchCommand(RobotCommand):
    def __init__(self, desired_pitch: degrees):
        super().__init__()
        self.desired_pitch = desired_pitch

    def execute(self, robot: ObjectOrientedRobot) -> None:
        desired_turn_count = robot.shooter.deg_to_turn_count(self.desired_pitch)
        robot.shooter.PIDController.setReference(desired_turn_count, CANSparkLowLevel.ControlType.kPosition)

        shooter_state = robot.shooter.get_state()
        if abs(shooter_state.pitch_encoder_pos - self.desired_pitch) < 0.1:
            logging.debug("ShooterPitchCommand: desired pitch reached")
            robot.shooter.set_pitch_motor_pct(0.0)
        if shooter_state.pitch_encoder_pos < self.desired_pitch:
            logging.debug("ShooterPitchCommand: pitch too low")
            robot.shooter.set_pitch_motor_pct(0.3)
        elif shooter_state.pitch_encoder_pos > self.desired_pitch:
            logging.debug("ShooterPitchCommand: pitch too high")
            robot.shooter.set_pitch_motor_pct(-0.3)
        else:
            logging.debug("ShooterPitchCommand: pitch is just right")
            robot.shooter.set_pitch_motor_pct(0.0)


class ShooterPitchStopCommand(RobotCommand):
    def __init__(self):
        super().__init__()
    
    def execute(self, robot: ObjectOrientedRobot) -> None:
        # ? Something more? Set brake?
        robot.shooter.set_pitch_motor_pct(0.0)


class ShooterPivotAmpCommand(RobotCommand):
    def __init__(self):
        super.__init__()

    def execute(self, robot: ObjectOrientedRobot) -> None:
        raise NotImplementedError()


class ShooterPivotSubCommand(RobotCommand):
    def __init__(self):
        super().__init__()

    def execute(self, robot: ObjectOrientedRobot) -> None:
        raise NotImplementedError()


class ShooterWheelSetSpeedCommand(RobotCommand):
    def __init__(self, speed):
        super().__init__()
        self.speed = speed

    def execute(self, robot: ObjectOrientedRobot) -> None:
        robot.shooter.PIDController_flywheel.setReference(self.speed, CANSparkLowLevel.ControlType.kVelocity)


class KickerSetSpeedCommand(RobotCommand):
    def __init__(self, speed):
        super().__init__()
        self.speed = speed

    def execute(self, robot):
        robot.shooter.kicker.set(self.speed)

