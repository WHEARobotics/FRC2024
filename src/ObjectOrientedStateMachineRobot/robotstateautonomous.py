import wpilib

from controllers import DriveSpeeds
from shootercommands import SwerveDriveSpeedCommand, SwerveDriveStopCommand, \
    ShooterPitchCommand, ShooterPitchStopCommand, KickerShooterCommand
from robotstate import RobotState
import logging


class AutonomousState(RobotState):

    def __init__(self):
        super().__init__()

    def periodic(self, robot):
        raise NotImplementedError()


class AutonomousStateAiming(AutonomousState):
    def __init__(self, robot):
        super().__init__()
        self.AIMING_DEADZONE = 2.0

        logging.debug("AutonomousStateAiming.__init__")
        self.robot = robot

    def periodic(self, robot) -> AutonomousState:
        logging.debug("AutonomousStateAiming.periodic")
        commands = []
        if robot.is_botpose_valid(robot.botpose):
            rot, direction_to_travel = (
                robot.vision.get_rotation_autonomous_periodic_for_speaker_shot(robot.botpose, robot.botpose[5]))

            if abs(rot) < self.AIMING_DEADZONE:
                logging.debug("Bot is pivoted correctly")
                stop = SwerveDriveStopCommand()
                commands.append(stop)
            else:
                # This seems wrong to me, as I don't know if rot is absolute or relative
                logging.debug(f"AutonomousStateAiming.periodic: rot={rot}, direction_to_travel={direction_to_travel}")
                command = SwerveDriveSpeedCommand(DriveSpeeds(0, 0, rot))
                commands.append(command)

            if robot.shooter.is_pitched_correctly(robot.botpose):
                logging.debug("AutonomousStateAiming.periodic: shooter is pitched correctly")
                stop = ShooterPitchStopCommand()
                commands.append(stop)
            else:
                logging.debug("AutonomousStateAiming.periodic: shooter is not pitched correctly")
                commands.append(ShooterPitchCommand(self.robot.shooter.SHOOTER_SUB_ANGLE))

            # Good to fire?
            if robot.shooter.flywheel_is_ready(robot.botpose) \
                    and robot.shooter.is_pitched_correctly(robot.botpose) \
                    and abs(rot) < self.AIMING_DEADZONE:
                logging.debug("AutonomousStateAiming.periodic: ready to fire")
                next_state = AutonomousStateShooting(robot)
            else:
                next_state = self

        for command in commands:
            command.execute(robot)
        return next_state


class AutonomousStateShooting(AutonomousState):
    def __init__(self, robot):
        super().__init__()
        logging.debug("AutonomousStateShooting.__init__")
        self.robot = robot
        self.post_shot_timer = wpilib.Timer()
        self.post_shot_timer.start()

    def periodic(self, robot) -> AutonomousState:
        logging.debug("AutonomousStateShooting.periodic")
        commands = []

        # Just for debugging
        if robot.is_botpose_valid(robot.botpose):
            rot, direction_to_travel = robot.vision.get_rotation_autonomous_periodic_for_speaker_shot(robot.botpose,
                                                                                                      robot.botpose[5])
            logging.debug(f"AutonomousStateShooting -- should be lined up: rot={rot}, direction_to_travel={direction_to_travel}")
        commands.append(KickerShooterCommand())
        for command in commands:
            command.execute(robot)

        if self.post_shot_timer.hasPeriodPassed(1.0):
            next_state = AutonomousStateIdle(robot)
        else:
            next_state = self
        return next_state



class AutonomousStateIdle(AutonomousState):
    def __init__(self, robot):
        logging.debug("AutonomousStateIdle.__init__")
        self.robot = robot

    def periodic(self, robot) -> AutonomousState:
        logging.debug("AutonomousStateIdle.periodic")
        return self


class RobotStateAutonomous(RobotState):
    def __init__(self, robot):
        self.robot = robot
        self.substate = AutonomousStateAiming(robot)

    def periodic(self, robot) -> RobotState:
        self.substate = self.substate.periodic(robot)
        return self

    def is_botpose_valid(self, botpose):
        if botpose == None:
            return False
        if len(botpose) < 1:
            return False
        if botpose[0] == -1:
            return False
        if botpose[0] == 0 and botpose[1] == 0 and botpose[1] == 0:
            return False
        return True

