from wpimath.units import degrees

class AutonomousAimingState:
    """
    Abstract base class for autonomous aiming states. Controls yaw and pitch based on vision.
    """
    def __init__(self, robot, vision):
        self.robot = robot
        self.vision = vision

    def periodic(self):
        """
        Perform the state's action.
        """
        raise NotImplementedError("Implement in concrete subclass")

    def get_name(self):
        """
        Get the name of the state.
        """
        raise NotImplementedError("Implement in concrete subclass")


class Idle(AutonomousAimingState):
    """
    State that does nothing.
    """
    def __init__(self, robot, vision):
        super().__init__(robot, vision)

    def periodic(self):
        return self

    def get_name(self):
        return "Idle"


class Starting(AutonomousAimingState):
    """
    State that starts the robot's vision tracking.
    """
    def __init__(self, robot, vision):
        super().__init__(robot, vision)

    def startup_complete(self):
        return True

    def periodic(self):
        if self.startup_complete():
            return Aligning(self.robot, self.vision)
        else:
            return self

    def get_name(self):
        return "Starting"


class Aligning(AutonomousAimingState):
    """
    State that aligns the robot to the target.
    """
    def __init__(self, robot, vision):
        super().__init__(robot, vision)
        self.rotation_deadband = 2

    def is_aligned(self, botpose):
        yaw_is_aligned = self.is_yaw_aligned(botpose)
        pitch_is_aligned = self.is_pitch_aligned(botpose)
        return yaw_is_aligned and pitch_is_aligned

    def is_yaw_aligned(self, botpose):
        x = botpose[0]
        y = botpose[1]
        current_yaw = botpose[5]
        speaker_y = 1.44  #
        distance_to_wall = (self.vision.speaker_x - x)  # Ajd
        distance_to_speaker_y = (speaker_y - y)  # Opp
        desired_bot_angle = self.vision.calculate_desired_angle(distance_to_speaker_y, distance_to_wall)
        if abs(current_yaw - desired_bot_angle) < self.rotation_deadband:
            return True
        else:
            return False

    def is_pitch_aligned(self, botpose):
        speaker_y = 1.44
        speaker_distance = self.vision.distance_to_speaker(botpose[0], botpose[1], self.vision.speaker_x, speaker_y)
        pitch = self.vision.calculate_desired_pitch(speaker_distance, speaker_y)
        if abs(self.robot.get_pitch() - pitch) < self.rotation_deadband:
            return True
        else:
            return False

    def get_rotation(self, botpose) -> degrees:
        current_yaw = botpose[5]
        rotation = self.vision.get_rotation_autonomous_periodic_for_speaker_shot(botpose, current_yaw)
        return degrees(-rotation)

    def get_pitch(self, botpose) -> degrees:
        speaker_y = 1.44
        speaker_distance = self.vision.distance_to_speaker(botpose[0], botpose[1], self.vision.speaker_x, speaker_y)
        pitch = self.vision.calculate_desired_pitch(speaker_distance, speaker_y) #TODO: Move calc_desired_pitch into Vision
        return degrees(pitch)

    def periodic_not_aligned(self, botpose):
        rotation = self.get_rotation(botpose)
        pitch = self.get_pitch(botpose)
        self.robot.add_rotation_level(rotation)
        self.robot.set_pitch(pitch)

    def botpose_is_valid(self, botpose):
        if len(botpose) > 0 and abs(botpose[0]) > 0 and abs(botpose[1]) > 0:
            return True
        else:
            return False

    def periodic(self):
        botpose = self.vision.checkBotpose()
        if self.botpose_is_valid(botpose):
            if self.is_aligned(botpose):
                return Aligned(self.robot, self.vision)
            else:
                self.periodic_not_aligned(botpose)
                return self
        else:
            # Invalid botpose, just cycle (?) or return new LostVisionState?
            return self

    def get_name(self):
        return "Aligning"


class Aligned(AutonomousAimingState):
    """
    State that is aligned to the target.
    """
    def __init__(self, robot, vision):
        super().__init__(robot, vision)

    def periodic(self):
        return self

    def get_name(self):
        return "Aligned"

