import wpilib

from shootercommands import ShooterFlywheelSpinCommand, SwerveDriveSpeedCommand, SwerveDriveStopCommand, \
    ShooterPitchCommand, ShooterPitchStopCommand, KickerShooterCommand
from robotstate import RobotState
from intake import WristAngleCommands
import logging

class AutonomousState:
    def periodic(self, robot):
        raise NotImplementedError()

class AutonomousStateAiming(AutonomousState):
    def __init__(self, robot):
        self.AIMING_DEADZONE = 2.0

        logging.debug("AutonomousStateAiming.__init__")
        self.robot = robot

    def periodic(self, robot) -> AutonomousState:
        logging.debug("AutonomousStateAiming.periodic")
        commands = []
        if robot.is_botpose_valid(robot.botpose):
            rot, direction_to_travel = robot.vision.get_rotation_autonomous_periodic_for_speaker_shot(robot.botpose,
                                                                                                             robot.botpose[5])

            if abs(rot) < self.AIMING_DEADZONE:
                logging.debug("Bot is pivoted correctly")
                stop = SwerveDriveStopCommand()
                commands.append(stop)
            else:
                # This seems wrong to me, as I don't know if rot is absolute or relative
                logging.debug(f"AutonomousStateAiming.periodic: rot={rot}, direction_to_travel={direction_to_travel}")
                command = SwerveDriveSpeedCommand(0, 0, rot)
                commands.append(command)
                next_state = self

            if robot.shooter.is_pitched_correctly(robot.botpose):
                logging.debug("AutonomousStateAiming.periodic: shooter is pitched correctly")
                stop = ShooterPitchStopCommand()
                commands.append(stop)
            else:
                logging.debug("AutonomousStateAiming.periodic: shooter is not pitched correctly")
                command.append(ShooterPitchCommand(self.robot.shooter.SHOOTER_SUB_ANGLE))

            # Good to fire?
            if robot.shooter.flywheel_is_ready(robot.botpose) \
                    and robot.shooter.is_pitched_correctly(robot.botpose) \
                    and abs(rot) < self.AIMING_DEADZONE:
                logging.debug("AutonomousStateAiming.periodic: ready to fire")
                next_state = AutonomousStateShooting(robot)

        for command in commands:
            command.execute(robot)
        return next_state



class AutonomousStateShooting(AutonomousState):
    def __init__(self, robot):
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
        self.substate.periodic(robot)

        # robot.swerve.drive(robot.x_speed, robot.y_speed, robot.rot, True)
        # # wrist positions for intake to move towards the requested location remove magic numbers!
        # # Not sure about robot.wrist_position here. It needs to be a WristAngleCommands enum value.
        # commands = robot.intake.get_periodic_commands(robot.wrist_position, robot.intake_control)
        # if robot.is_botpose_valid(robot.botpose):
        #     speaker_distance_m = robot.distance_to_speaker(robot.botpose[0], robot.botpose[1], robot.speaker_x,
        #                                                    FieldPositions.speaker_y)
        # else:
        #     # No botpose!
        #     speaker_distance_m = 0
        # robot.shooter.get_periodic_commands(speaker_distance_m, robot.shooter_pivot_control, robot.shooter_control, robot.kicker_action)
        # for command in commands:
        #     command.execute(robot)


    # def autonomous_periodic_aiming(self, botpose):
    #
    #     x = botpose[0]
    #     y = botpose[1]
    #     current_yaw = botpose[5]  # getting the yaw from the self.botpose table
    #     desired_yaw = 0  # where we want our yaw to go
    #
    #     desired_direction = self.calculate_desired_direction(desired_yaw, current_yaw)
    #     wpilib.SmartDashboard.putString("DB/String 0", str(x))
    #     wpilib.SmartDashboard.putString("DB/String 1", str(y))
    #     wpilib.SmartDashboard.putString("DB/String 2", f"{desired_direction:3.1f}")
    #
    #     current_yaw = botpose[5]  # getting the yaw from the self.botpose table
    #     desired_yaw = 0  # where we want our yaw to go
    #
    #     direction_to_travel = self.calculate_desired_direction(desired_yaw, current_yaw)
    #     self.vision.get_rotation_autonomous_periodic_for_speaker_shot(self.botpose, current_yaw)
    #
    #     if direction_to_travel < -1:
    #         self.intake.get_periodic_commands(WristAngleCommands.wrist_stow_action_action, 1)
    #     elif direction_to_travel > 2:
    #         self.intake.get_periodic_commands(WristAngleCommands.wrist_mid_action, 2)
    #     else:
    #         self.rot = 0.0
    #     # How can we tell that we have completed turning? When we do that
    #     # self.automous_state = self.AUTONOMOUS_STATE_SPEAKER_SHOOTING
    #
    # def autonomous_periodic_shooting(self, botpose):
    #     """
    #     this will get the angle needed for the shooter to be able to shoot from different positions by calculating through trig
    #     """
    #     print("NOT IMPLEMENTED")
    #     pass

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

