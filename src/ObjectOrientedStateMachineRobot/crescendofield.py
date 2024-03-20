import logging

from wpilib import DriverStation

from fieldpositions import FieldPositions


class CrescendoField:
    def __init__(self, ally: DriverStation.Alliance):
        if ally is not None:
            if ally == DriverStation.Alliance.kRed:
                self.speaker_x = FieldPositions.speaker_x_red
                self.desired_x_for_autonomous_driving = FieldPositions.desired_x_for_autonomous_driving_red
            elif ally == DriverStation.Alliance.kBlue:
                self.speaker_x = FieldPositions.speaker_x_blue
                self.desired_x_for_autonomous_driving = FieldPositions.desired_x_for_autonomous_driving_blue
        else:
            logging.warning("No alliance found, defaulting to red")
            self.speaker_x = FieldPositions.speaker_x_red
            self.desired_x_for_autonomous_driving = FieldPositions.desired_x_for_autonomous_driving_red
