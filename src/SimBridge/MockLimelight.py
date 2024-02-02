from typing import Callable

from _pynetworktables import NetworkTables


class MockLimelight:
    ###
    This class is a mock of the Limelight device. Instead of the physical device using a camera to recognize AprilTags,
    this class simply writes the robot's position and rotation to NetworkTables. The robot's position and rotation are
    taken from the files written by xRCSim.
    ###

    def __init__(self, status_callback: Callable[[str], None]) -> None:
        ###
        Initializes this class by creating a NetworkTables client and setting up the table that will hold the robot's
        position and rotation.
        ###

        # The NT server is the `robotpy sim` process, which should be running prior to running this program
        NetworkTables.initialize(server='localhost')
        self.limelight_table = NetworkTables.getTable("limelight")
        self.botpose = [0, 0, 0, 0, 0, 0]

    # Position variables are in Field Space (origin @ field center, meters) and rotation is in degrees clockwise from the positive x-axis
    def set_robot_position(self, x : float, y : float, z : float, roll : float, yaw : float, pitch : float) -> [float]:
        self.botpose = [x, y, z, roll, yaw, pitch]
        self.limelight_table.putNumberArray("botpose", self.botpose)
        return self.botpose

    def get_botpose(self):
        return self.botpose
