from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QWidget


class RobotWidget(QWidget):
    """
    A widget that displays a robot at a given position and rotation. It is a rectangle with an arrow.
    """

    def __init__(self, pixels_per_meter):
        """
        Initializes the robot widget to be properly sized given `pixels_per_meter`
        """

        super().__init__()

        # TODO: Update with real frame+bumper size
        self.robot_edge_pixels = int(76 / 100 * pixels_per_meter)  # 76cm
        self.field_pos = (0, 0)
        self.origin_offset_x = 9 * pixels_per_meter
        # Running on a widget that's 8m tall, with origin halfway down
        # It's not negative because widget coordinates are in "typewriter" space (0,0) is top left, down is +y
        self.origin_offset_y = 4 * pixels_per_meter
        self.pixels_per_meter = pixels_per_meter
        self.field_rotation = 0
        # The robot is drawn as a smallish square, but the widget size defines "where on the screen" it's allowed to
        # paint. So make the widget big enough to contain the robot no matter where it's positioned
        self.setFixedSize(1600,1600)

    # Called by Qt when the widget needs to be redrawn (e.g. when it's first shown, or when update() is called)
    def paintEvent(self, event):
        q = QPainter(self)
        q.setPen(QPen(Qt.black, 5, Qt.SolidLine))
        q.setBrush(QColor(255, 0, 0, 127))

        # Transform to center of robot
        transform = q.transform()
        # Set origin to the center of the robot
        transform.translate(self.field_pos[0] * self.pixels_per_meter + self.origin_offset_x,
                            self.field_pos[1] * self.pixels_per_meter + self.origin_offset_y)
        # Rotate around center of robot
        transform.rotate(self.field_rotation)
        # Use this new translated and rotated transform for drawing
        q.setTransform(transform)
        # Note that at this point, the origin is at the center of the robot and the robot is rotated
        # So we can draw the robot as if it's at (0,0) and it will appear on the screen properly located and rotated
        q.drawRect(int(-self.robot_edge_pixels / 2),
                   int(-self.robot_edge_pixels / 2),
                   int(self.robot_edge_pixels),
                   int(self.robot_edge_pixels))
        # Draw directional arrow
        q.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        arrow_start = (0, 0)
        arrow_end = (self.robot_edge_pixels + 5, 0)
        q.drawLine(int(arrow_start[0]), int(arrow_start[1]), int(arrow_end[0]), int(arrow_end[1]))
        q.drawLine(int(arrow_end[0]), int(arrow_end[1]), int(arrow_end[0] - 10), int(arrow_end[1] - 10))
        q.drawLine(int(arrow_end[0]), int(arrow_end[1]), int(arrow_end[0] - 10), int(arrow_end[1] + 10))

        # Anything drawn after this call to `end` will be in the original coordinate system
        q.end()

    def update_position(self, field_x, field_y, field_rotation):
        # "Field Space" (0,0) is the center of the field in meters.
        self.field_pos = (field_x, field_y)
        self.field_rotation = field_rotation
        self.update()
