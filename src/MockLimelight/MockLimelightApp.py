import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QWidget, QVBoxLayout, QRadioButton, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QPainter, QColor, QPen


class RobotWidget(QWidget):
    def __init__(self, pixels_per_meter):
        super().__init__()
        # Update with real frame+bumper size
        self.robot_edge_px = int(76 / 100 * pixels_per_meter)  # 76cm
        self.field_pos = (0, 0)
        self.origin_offset_x = 0
        # Running on a widget that's 8m tall, with origin halfway down
        # It's not negative because widget coordinates are in "typewriter" space (0,0) is top left, down is +y
        self.origin_offset_y = 4 * pixels_per_meter
        self.pixels_per_meter = pixels_per_meter
        self.field_rotation = 0

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
        q.drawRect(int(-self.robot_edge_px/2),
                   int(-self.robot_edge_px/2),
                   int(self.robot_edge_px),
                   int(self.robot_edge_px))
        # Draw directional arrow
        q.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        arrow_start = (0, 0)
        arrow_end = (self.robot_edge_px + 5, 0)
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        self.field, self.robot = self._build_field()
        layout.addWidget(self.field)
        self.control_panel = self._build_control_panel()
        layout.addWidget(self.control_panel)

        # Set window size to 1024x768
        self.resize(1024, 800)

    def _build_control_panel(self):
        # Create a panel on the right-hand side
        control_panel = QWidget()
        control_panel_layout = QVBoxLayout(control_panel)

        # Sliders
        self.field_x_slider = QSlider(Qt.Horizontal)
        self.field_x_slider.setMinimum(0)
        self.field_x_slider.setMaximum(800)
        self.field_x_slider.valueChanged.connect(self.update_robot_pos)
        control_panel_layout.addWidget(self.field_x_slider)
        self.field_y_slider = QSlider(Qt.Horizontal)
        self.field_y_slider.setMinimum(-400)
        self.field_y_slider.setMaximum(400)
        self.field_y_slider.setValue(0)
        self.field_y_slider.valueChanged.connect(self.update_robot_pos)
        control_panel_layout.addWidget(self.field_y_slider)

        self.field_rotation_slider = QSlider(Qt.Horizontal)
        self.field_rotation_slider.setMaximum(-180)
        self.field_rotation_slider.setMaximum(180)
        self.field_rotation_slider.setValue(0)
        self.field_rotation_slider.valueChanged.connect(self.update_robot_pos)
        control_panel_layout.addWidget(self.field_rotation_slider)

        # Mock Limelight Radio Button
        self.mock_limelight = QRadioButton("Mock Limelight")
        self.mock_limelight.setChecked(False)  # Default to False
        control_panel_layout.addWidget(self.mock_limelight)
        # Display-only fields
        self.rpm_flywheel_label = QLabel("Flywheel RPM: 0")
        control_panel_layout.addWidget(self.rpm_flywheel_label)
        self.rpm_kicker_label = QLabel("Kicker Wheel RPM: 0")
        control_panel_layout.addWidget(self.rpm_kicker_label)
        self.distance_speaker_label = QLabel("Distance to Speaker: 0")
        control_panel_layout.addWidget(self.distance_speaker_label)
        self.angle_degrees_label = QLabel("Angle in Degrees: 0")
        control_panel_layout.addWidget(self.angle_degrees_label)

        return control_panel

    @staticmethod
    def _build_field():
        # Background SVG
        svg_widget = QSvgWidget('./field_right.svg')
        widget_width = 800  # pixels
        field_size_x = 9  # meters
        field_size_y = 8
        pixels_per_meter = int(widget_width / field_size_x)  # 1px == 1cm
        svg_widget.setFixedSize(field_size_x * pixels_per_meter, field_size_y * pixels_per_meter)
        # Place it at 0,0
        svg_widget.move(0, 0)

        # Robot Widget
        # Place it inside the svg_widget
        # Rectangle widget
        robot = RobotWidget(pixels_per_meter)
        robot.setParent(svg_widget)

        return svg_widget, robot

    def update_robot_pos(self):
        field_x = self.field_x_slider.value() / 100
        field_y = self.field_y_slider.value() / 100
        field_rotation = self.field_rotation_slider.value()
        self.robot.update_position(field_x, field_y, field_rotation)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
