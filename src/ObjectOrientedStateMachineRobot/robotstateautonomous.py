from robotstate import RobotState


class RobotStateAutonomous(RobotState):
    def __init__(self, robot):
        self.robot = robot

    def periodic(self, robot) -> RobotState:
        robot.botpose = robot.vision.checkBotpose()
        robot.shooter_control = 2  # this sets the shooter to always spin at shooting speed
        # during the whole autonomous gamemode.

        if robot.is_botpose_valid(robot.botpose):
            if robot.autonomous_state == robot.AUTONOMOUS_STATE_AIMING:
                robot.autonomous_periodic_aiming(robot.botpose)
            elif robot.autonomous_state == robot.AUTONOMOUS_STATE_SPEAKER_SHOOTING:
                robot.autonomous_periodic_shooting(robot.botpose)
        else:
            wpilib.SmartDashboard.putString("DB/String 0", str("noBotpose"))

        robot.swerve.drive(robot.x_speed, robot.y_speed, robot.rot, True)
        # wrist positions for intake to move towards the requested location remove magic numbers!
        robot.intake.periodic(robot.wrist_position, robot.intake_control)
        if robot.is_botpose_valid(robot.botpose):
            speaker_distance_m = robot.distance_to_speaker(robot.botpose[0], robot.botpose[1], robot.speaker_x,
                                                           FieldPositions.speaker_y)
        else:
            # No botpose!
            speaker_distance_m = 0
        robot.shooter.periodic(speaker_distance_m, robot.shooter_pivot_control, robot.shooter_control, robot.kicker_action)

    def autonomous_periodic_aiming(self, botpose):

        x = botpose[0]
        y = botpose[1]
        current_yaw = botpose[5]  # getting the yaw from the self.botpose table
        desired_yaw = 0  # where we want our yaw to go

        desired_direction = self.calculate_desired_direction(desired_yaw, current_yaw)
        wpilib.SmartDashboard.putString("DB/String 0", str(x))
        wpilib.SmartDashboard.putString("DB/String 1", str(y))
        wpilib.SmartDashboard.putString("DB/String 2", f"{desired_direction:3.1f}")

        current_yaw = botpose[5]  # getting the yaw from the self.botpose table
        desired_yaw = 0  # where we want our yaw to go

        direction_to_travel = self.calculate_desired_direction(desired_yaw, current_yaw)
        self.vision.get_rotation_autonomous_periodic_for_speaker_shot(self.botpose, current_yaw)

        if direction_to_travel < -1:
            self.intake.periodic(1, 1)
        elif direction_to_travel > 2:
            self.intake.periodic(3, 2)
        else:
            self.rot = 0.0
        # How can we tell that we have completed turning? When we do that
        # self.automous_state = self.AUTONOMOUS_STATE_SPEAKER_SHOOTING

    def autonomous_periodic_shooting(self, botpose):
        """
        this will get the angle needed for the shooter to be able to shoot from different positions by calculating through trig
        """
        print("NOT IMPLEMENTED")
        pass

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

