from robotstate import RobotState


class RobotStateTeleop(RobotState):
    def __init__(self, robot):
        self.robot = robot

        robot.halfSpeed = True

        robot.intake.wrist_motor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        robot.swerve.front_left.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        robot.swerve.front_right.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        robot.swerve.back_left.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)
        robot.swerve.back_right.driveMotor.setIdleMode(rev._rev.CANSparkMax.IdleMode.kBrake)

        robot.intake_action = 1  # this action speeds up the intake motors to intake
        robot.outtake_action = 2  # this action speeds up the intake motors to outtake
        robot.wrist_intake_action = 2  # this action raises the wrist up
        robot.wrist_in_action = 1  # this action puts the wrist down
        robot.wrist_mid_action = 3  # action to move the intake to a position not in the way with the shooter and note

        robot.shooter_pivot_start = 1  # this pivots the shooter into a 0 degree angle
        robot.shooter_pivot_max = 2  # this pivots the shooter into a 90 degree angle
        robot.shooter_pivot_amp = 3  # this pivots the shooter into a 180 degree angle
        robot.shooter_pivot_sub = 4  # subwoofer angle to move the shooter to the sub angle
        robot.shooter_pivot_manual_up = 5  # this manually pivots the shooter up
        robot.shooter_pivot_manual_down = 6  # this manually pivots the shooter down

        robot.shooter_action_intake = 1  # this action moves the shooter motors to intake
        robot.shooter_action_shot = 2  # this action moves the shooter motors to outtake

        robot.kicker_intake = 1  # this action moves the kicker motors and feed the note into the shooter
        robot.kicker_amp_shot = 2  # this utilizes the kicker to shoot into the amp.
        robot.kicker_shooter = 3  # this speeds up the kicker to be able to shoot with it at high speeds into the flywheels

        robot.intake_idle = 0
        robot.shooter_pivot_idle = 0
        robot.shooter_flywheel_idle = 0
        robot.wrist_idle = 0
        robot.kicker_idle = 0

        robot.wiggleTimer.reset()

        robot.percent_output = 0.1

        robot.kicker_state = 0

        # is used to go to else, stopping the motor

    def periodic(self):

        self.driveWithJoystick()

        self.Abutton = self.xbox_operator.getAButton()
        self.Bbutton = self.xbox_operator.getBButton()
        self.Xbutton = self.xbox_operator.getXButton()
        self.Ybutton = self.xbox_operator.getYButton()
        self.RightBumper = self.xbox_operator.getRightBumper()
        self.LeftBumper = self.xbox_operator.getLeftBumper()
        self.leftStickButton = self.xbox_operator.getLeftStickButton()
        self.rightStickButton = self.xbox_operator.getRightStickButton()
        self.leftTrigger = self.xbox_operator.getLeftTriggerAxis()
        self.rightTrigger = self.xbox_operator.getRightTriggerAxis()
        self.startButton = self.xbox_operator.getStartButton()

        self.readAbsoluteEncodersAndOutputToSmartDashboard()

        self.botpose = self.vision.checkBotpose()

        # we commented out this for now because we dont want any position control for our first robot tests
        if self.leftStickButton:
            self.shooter_pivot_control = self.shooter_pivot_manual_up
        elif self.rightStickButton:
            self.shooter_pivot_control = self.shooter_pivot_manual_down
        else:
            self.shooter_pivot_control = 0

        if self.Abutton:
            self.wrist_position = WristAngleCommands.wrist_intake_action
            self.intake_control = IntakeCommands.intake_action
        elif self.Bbutton:
            self.wrist_position = WristAngleCommands.wrist_stow_action
            self.intake_control = IntakeCommands.outtake_action
            self.kicker_action = ShooterKickerCommands.kicker_intake
            self.shooter_pivot_control = 2
        # this is the button to transfer the note from the intake into the shooter kicker
        elif self.Xbutton:
            self.kicker_action = ShooterKickerCommands.kicker_amp_shot  # amp shot to shoot into the amp
        elif self.rightTrigger:
            self.kicker_action = ShooterKickerCommands.kicker_shooter
        # this is used after holding y(the flywheel speeds) to allow the kicker move the note into the flywheels to shoot
        else:
            self.intake_control = IntakeCommands.idle
            self.wrist_position = WristAngleCommands.wrist_stow_action
            self.kicker_action = ShooterKickerCommands.kicker_idle
            # this stops the motor from moving

        if self.Ybutton:
            self.shooter_control = self.shooter_action_shot
        else:
            self.shooter_control = self.shooter_flywheel_idle
        # this button speeds up the shooter flywheels before shooting the note

        # if self.LeftBumper:
        #     self.intake_control = IntakeCommands.intake_action
        # elif self.RightBumper:
        #     self.intake_control = IntakeCommands.outtake_action
        # # else:
        #     self.intake_control = IntakeCommands.idle

        # we could use manual intake to do without changing the wrist to move the note farther in. i could be wrong and we might just want
        # to hold intake longer to push the note farther.

        if self.startButton:
            self.shooter_pivot_control = self.shooter_pivot_amp
        elif self.leftTrigger:
            self.shooter_pivot_control = self.shooter_pivot_sub
            self.wrist_position = WristAngleCommands.wrist_mid_action
        # changes the shooter pitch angle to pitch into the amp or subwoofer speaker angle

        # this state machine is used to check if we have the note in our kicker and we have let go of the intake to the kicker button
        # once we let go we want the state machine to set the state to 3 to kick it back for a bit away from the flywheels so they
        # could speed up

        # the goal of this state machine is when the state has memory of intaking with the wrist and then after when the kicker intakes to
        # the shooter we check to see if the state has memory of both happening and we let go of the kicker intake button, the state completes
        # and the kicker adjusts the note back away from the flywheels.

        if self.kicker_state == 0:
            # we start by checking if we intook with the wristy
            if self.intake_control == IntakeCommands.intake_action:
                self.kicker_state = 1
        elif self.kicker_state == 1:
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
        self.intake.periodic(self.wrist_position, self.intake_control)

        if self.is_botpose_valid(self.botpose):
            speaker_distance_m = self.distance_to_speaker(self.botpose[0], self.botpose[1], self.speaker_x,
                                                          self.speaker_y)
        else:
            # No botpose!
            speaker_distance_m = 0
        self.shooter.periodic(speaker_distance_m, self.shooter_pivot_control, self.shooter_control, self.kicker_action)

        # self.botpose = self.vision.checkBotpose()

        # self.current_yaw = self.botpose[5]#getting the yaw from the self.botpose table
        # self.desired_yaw = 0 #where we want our yaw to go

        self.Abutton = self.xbox.getAButton()
        self.Bbutton = self.xbox.getBButton()

        if self.xbox.getRightBumper() and self.xbox.getLeftBumper():
            self.swerve.gyro.set_yaw(0)

        # wpilib.SmartDashboard.putString('DB/String 1',f"Desired angle: {self.desired_angle:.1f}")
        # wpilib.SmartDashboard.putString('DB/String 2', f"Current angle: {self.current_angle:.1f}")
        # wpilib.SmartDashboard.putString('DB/String 3', f"Desired Turn Count: {self.desired_turn_count:.1f}")

        # wpilib.SmartDashboard.putString('DB/String 4', f"abs_encoder_pos {self.correctedEncoderPosition():.3f}")

        if self.is_botpose_valid(self.botpose):
            x = self.botpose[0]
            y = self.botpose[1]
            wpilib.SmartDashboard.putString("DB/String 0", str(x))
            wpilib.SmartDashboard.putString("DB/String 1", str(y))

            current_yaw = self.botpose[5]  # getting the yaw from the self.botpose table
            desired_yaw = 0  # where we want our yaw to go

            speaker_x = 6.5273  # the x coordinate of the speaker marked in the field drawings in m.
            speaker_y = 1.98  # height of the speaker in meters.

            bot_x = self.botpose[0]  # the x coordinate from the botpose table
            bot_y = self.botpose[1]  # the y pos from the botpose table

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
            # wpilib.SmartDashboard.putString("DB/String 0", "No botpose")
            pass
        return self

    def finalize(self):
        pass
