from typing import Callable

from _pynetworktables import NetworkTables


class MockLimelight:
    def __init__(self, status_callback: Callable[[str], None]) -> None:
        # The NT server is the `robotpy sim` process, which should be running prior to running this program
        NetworkTables.initialize(server='localhost')
        self.limelight_table = NetworkTables.getTable("limelight")

    # Position variables are in Field Space (origin @ field center, meters) and rotation is in degrees clockwise from the positive x-axis
    def set_robot_position(self, x : float, y : float, z : float, roll : float, yaw : float, pitch : float) -> [float]:
        botpose = [x, y, z, roll, yaw, pitch]
        self.limelight_table.putNumberArray("botpose", botpose)
        return botpose
