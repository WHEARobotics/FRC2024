import wpilib

from robotcommand import RobotCommand
from shootercommands import KickerAmpShotCommand, KickerShooterCommand, ShooterActionShotCommand, \
    ShooterFlywheelIdleCommand, ShooterPitchAmplifierCommand, ShooterPitchSubwooferCommand, KickerIdleCommand, \
    ShooterPitchCommand, VisionPitchCommand, VisionYawCommand
from drivecommands import SwerveDriveSpeedCommand, GyroSetYawCommand, \
    PivotControlCommand
from intakecommands import IntakeCommand, IntakeToShooterHandoff, IntakeIdleCommand, \
    WristStowCommand, WristAngleMidCommand
from intake import WristAngleCommandEnum, IntakeCommandEnum
from shooterenums import ShooterKickerCommandEnum
from controllers import ControllersState
from robotstate import RobotState
import rev


class RobotStateTeleop(RobotState):
    def __init__(self, robot):
        super().__init__(robot)
        self.robot = robot
        self.shooter_pivot_manual_up = 1
        self.shooter_pivot_manual_down = -1

        for component in [robot.swerve, robot.intake, robot.shooter]:
            component.set_idle_mode(rev.CANSparkMax.IdleMode.kBrake)

    def periodic(self, robot):
        current_actions = []
        controller_state = self.robot.controllers.get_state()
        current_actions += self.commands_based_on_controller_input(controller_state)

        # End commands based on controller input
        # wrist positions for intake to move towards the requested location remove magic numbers!
        # Not sure about robot.wrist_position here. It needs to be a WristAngleCommands enum value.
        current_actions += self.robot.intake.get_teleop_periodic_commands()
        current_actions += self.robot.shooter.get_teleop_periodic_commands()
        current_actions += self.robot.vision.get_teleop_periodic_commands()
        
        # If there is a ShooterPitchCommand in commands, remove any VisionPitchCommand
        # because the ShooterPitchCommand comes from controller override
        if any(isinstance(command, ShooterPitchCommand) for command in current_actions):
            current_actions = [command for command in current_actions if not isinstance(command, VisionPitchCommand)]
            
        # If there is a SwerveDriveSpeedCommand in commands, remove any VisionYawCommand
        # because the SwerveDriveSpeedCommand comes from controller override
        if any(isinstance(command, SwerveDriveSpeedCommand) for command in current_actions):
            current_actions = [command for command in current_actions if not isinstance(command, VisionYawCommand)]

        for action in current_actions:
            action.execute(self.robot)
        return self

    @staticmethod
    def idle_actions():
        return [IntakeIdleCommand(), WristStowCommand(), KickerIdleCommand()]

    def do_handoff_intake_to_shooter(self):
        return IntakeToShooterHandoff(self.wrist_position, self.intake_control, self.kicker_action, self.shooter_pivot_control)

    def do_intake(self) -> RobotCommand:
        self.wrist_position = WristAngleCommandEnum.wrist_intake_action
        self.intake_control = IntakeCommandEnum.intake_action
        return IntakeCommand(self.intake_control, self.wrist_position)



    def pivot_control_periodic(self, controller_state : ControllersState):
        if controller_state.left_stick_button:
            pivot_delta = self.shooter_pivot_manual_up
        elif controller_state.right_stick_button:
            pivot_delta = self.shooter_pivot_manual_down
        else:
            pivot_delta = 0
        pivot_current = self.robot.shooter.get_state().shooter_pivot_encoder_pos
        return ShooterPitchCommand(pivot_current + pivot_delta)

    def commands_based_on_controller_input(self, controller_state):
        current_actions = []
        drive_speeds = self.speeds_for_joystick_values(controller_state.joystick_x,
                                                       controller_state.joystick_y,
                                                       controller_state.joystick_rot)
        swerve_drive_speed_command = SwerveDriveSpeedCommand(drive_speeds)
        current_actions.append(swerve_drive_speed_command)

        pivot_command = self.pivot_control_periodic(controller_state)
        current_actions.append(pivot_command)

        if controller_state.a_button:
            intake_command = self.do_intake()
            current_actions.append(intake_command)
        elif controller_state.b_button:
            handoff_command = self.do_handoff_intake_to_shooter()
            current_actions.append(handoff_command)
        # this is the button to transfer the note from the intake into the shooter kicker
        elif controller_state.x_button:
            current_actions.append(KickerAmpShotCommand())

        elif controller_state.y_button:
            current_actions.append(KickerShooterCommand())
            #kicker_action = ShooterKickerCommands.kicker_shooter
        # this is used after holding y(the flywheel speeds) to allow the kicker move the note into the flywheels to shoot
        else:
            idle_commands = self.idle_actions()
            current_actions += idle_commands
            # this stops the motor from moving

        if controller_state.y_button:
            current_actions.append(ShooterActionShotCommand())
        else:
            current_actions.append(ShooterFlywheelIdleCommand())
        # this button speeds up the shooter flywheels before shooting the note

        # we could use manual intake to do without changing the wrist to move the note farther in. i could be wrong and we might just want
        # to hold intake longer to push the note farther.

        if controller_state.start_button:
            current_actions.append(ShooterPitchAmplifierCommand())
        elif controller_state.left_trigger > 0.5:
            current_actions.append(ShooterPitchSubwooferCommand())
            current_actions.append(WristAngleMidCommand())
        # changes the shooter pitch angle to pitch into the amp or subwoofer speaker angle

        if controller_state.right_bumper and controller_state.left_bumper:
            current_actions.append(GyroSetYawCommand(0))

        return current_actions