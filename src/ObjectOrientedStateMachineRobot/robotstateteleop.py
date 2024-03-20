import wpilib

from intake import WristAngleCommands, IntakeCommands
from shooter import ShooterKickerCommands
from controllers import ControllersState, DriveSpeeds
from robotstate import RobotState
import rev

class KickerState:
    def __init__(self):
        pass

    def periodic(self):
        pass

    def finalize(self):
        pass

class KickerInitialState(KickerState):
    def __init__(self):
        pass

    def periodic(self, controller_state: ControllersState) -> tuple(KickerState, RobotCommand):
        # we start by checking if we intook with the wristy

        if self.intake_control == IntakeCommands.intake_action:
            self.kicker_state = 1
        return self, None

    def finalize(self):
        pass


class RobotStateTeleop(RobotState):
    def __init__(self, robot):
        self.robot = robot
        for component in [robot.swerve, robot.intake, robot.shooter]:
            component.set_idle_mode(rev.CANSparkMax.IdleMode.kBrake)

        self.kicker_state = KickerInitialState()

    def periodic(self):
        current_actions = []

        # Debugging
        self.robot.read_absolute_encoders_and_output_to_smart_dashboard()

        controller_state = self.robot.controllers.get_state()

        drive_command = self.drive_with_joystick_periodic()
        current_actions.append(drive_command)

        pivot_command = self.pivot_control_periodic(controller_state)
        current_actions.append(pivot_command)

        if controller_state.a_button:
            intake_command = self.do_intake()
            current_actions.append(intake_command)
        elif controller_state.b_button:
            outtake_command = self.do_outtake()
            current_actions.append(outtake_command)
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
            #shooter_pivot_control = self.shooter_pivot_amp
            current_actions.append(ShooterPivotAmpCommand())
        elif controller_state.left_trigger > 0.5:
            shooter_pivot_control = self.shooter_pivot_sub
            current_actions.append(ShooterPivotSubCommand())
            current_actions.append(WristAngleMidCommand())
        # changes the shooter pitch angle to pitch into the amp or subwoofer speaker angle

        # this state machine is used to check if we have the note in our kicker and we have let go of the intake to the kicker button
        # once we let go we want the state machine to set the state to 3 to kick it back for a bit away from the flywheels so they
        # could speed up

        # the goal of this state machine is when the state has memory of intaking with the wrist and then after when the kicker intakes to
        # the shooter we check to see if the state has memory of both happening and we let go of the kicker intake button, the state completes
        # and the kicker adjusts the note back away from the flywheels.

        self.kicker_state, self.kicker_command = self.kicker_state.periodic()
        current_actions.append(self.kicker_command)

        if self.kicker_state == 1:
            # we check to see if we have the wrist tucked back
            if self.intake.motor_pos_degrees < 5:
                self.kicker_state = 2
        elif self.kicker_state == 2:
            # we check to see if we started doing the kicker intake action
            if self.kicker_action == ShooterKickerCommands.kicker_intake:
                self.kicker_state = 3
            elif self.intake_control == IntakeCommands.intake_action:
                self.kicker_state = 0
        elif self.kicker_state == 3:
            # check to see if we finished intaking with the kicker and stopped
            if self.kicker_action != ShooterKickerCommands.kicker_intake:
                self.wiggleTimer.reset()
                self.wiggleTimer.start()
                self.kicker_state = 4
        elif self.kicker_state == 4:
            # adjusts the kicker to move the note back until the timer passes the 0.3 seconds
            if self.wiggleTimer.advanceIfElapsed(0.3):  # 0.3 seconds are change-able
                self.kicker_action = ShooterKickerCommands.kicker_idle
                self.kicker_state = 0
            else:
                self.kicker_action = ShooterKickerCommands.kicker_adjustment  # 4

        # wrist positions for intake to move towards the requested location remove magic numbers!
        # Not sure about robot.wrist_position here. It needs to be a WristAngleCommands enum value.
        self.intake.get_periodic_commands(self.wrist_position, self.intake_control)

        botpose = self.robot.vision.checkBotpose()
        if self.is_botpose_valid(botpose):
            speaker_distance_m = self.distance_to_speaker(self.botpose[0], self.botpose[1], self.speaker_x,
                                                          self.speaker_y)
            x = botpose[0]
            y = botpose[1]
            wpilib.SmartDashboard.putString("DB/String 0", str(x))
            wpilib.SmartDashboard.putString("DB/String 1", str(y))

            current_yaw = botpose[5]  # getting the yaw from the self.botpose table
            desired_yaw = 0  # where we want our yaw to go

            speaker_x = 6.5273  # the x coordinate of the speaker marked in the field drawings in m.
            speaker_y = 1.98  # height of the speaker in meters.

            bot_x = botpose[0]  # the x coordinate from the botpose table
            bot_y = botpose[1]  # the y pos from the botpose table

            self.speaker_distance = self.distance_to_speaker(bot_x, bot_y, speaker_x, speaker_y)
            # fills the distance to speaker function with its required values for the calculate pitch function

            self.calculate_pitch = self.calculate_desired_pitch(self.speaker_distance, speaker_y)
            # fills the calculate pitch function with necessary values to be properly called
            pitch_in_degrees = self.radians_to_degrees(self.calculate_pitch)
            # converts the pitch shooter angle to degrees from radians

            wpilib.SmartDashboard.putString("DB/String 4", str(pitch_in_degrees))

            desired_direction = self.calculate_desired_direction(desired_yaw, current_yaw)
            wpilib.SmartDashboard.putString("DB/String 2", f"{desired_direction:3.1f}")
            if abs(desired_direction) < 1.0:
                wpilib.SmartDashboard.putString("DB/String 3", "Shoot, you fools!")
            else:
                wpilib.SmartDashboard.putString("DB/String 3", "Hold!")
        else:
            # No botpose!
            speaker_distance_m = 0
        self.shooter.get_periodic_commands(speaker_distance_m, shooter_pivot_control, shooter_control, kicker_action)

        if controller_state.right_bumper and controller_state.left_bumper:
            current_actions.append(GyroSetYawCommand(0))

        for action in current_actions:
            action.execute(self.robot)
        return self

    def idle_actions(self):
        self.intake_control = IntakeCommands.idle
        self.wrist_position = WristAngleCommands.wrist_stow_action
        self.kicker_action = ShooterKickerCommands.kicker_idle
        return [IntakeIdleCommand(), WristStowCommand(), KickerIdleCommand()]

    def do_outtake(self):
        self.wrist_position = WristAngleCommands.wrist_stow_action
        self.intake_control = IntakeCommands.outtake_action
        self.kicker_action = ShooterKickerCommands.kicker_intake
        self.shooter_pivot_control = 2
        return OuttakeCommand(self.wrist_position, self.intake_control, self.kicker_action, self.shooter_pivot_control)

    def do_intake(self) -> RobotCommand:
        self.wrist_position = WristAngleCommands.wrist_intake_action
        self.intake_control = IntakeCommands.intake_action
        return IntakeCommand(self.intake_control, self.wrist_position)

    def finalize(self):
        pass


    def drive_with_joystick_periodic(self) -> SwerveDriveSpeedCommand:
        joystick_x, joystick_y, joystick_rot = self.robot.controller.getJoystickDriveValues()
        drive_speeds = self.robot.controller.speeds_for_joystick_values(joystick_x, joystick_y, joystick_rot)
        return SwerveDriveSpeedCommand(drive_speeds)
        '''
        this uses our joystick inputs and accesses a swerve drivetrain function to use field relative and the swerve module to drive the robot.
        '''

    def pivot_control_periodic(self, controller_state : ControllersState):
        # we commented out this for now because we dont want any position control for our first robot tests
        if controller_state.left_stick_button:
            self.shooter_pivot_control = self.shooter_pivot_manual_up
        elif controller_state.right_stick_button:
            self.shooter_pivot_control = self.shooter_pivot_manual_down
        else:
            self.shooter_pivot_control = 0
        # TODO Do something with shooter_pivot_control
        return PivotControlCommand(self.shooter_pivot_control)