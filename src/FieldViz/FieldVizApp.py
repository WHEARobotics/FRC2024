import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QWidget, QVBoxLayout, QRadioButton, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtSvg import QSvgWidget
from networktables import NetworkTables
import math

from RobotWidget import RobotWidget


class MainWindow(QMainWindow):
    def __init__(self, nt_server_ip : str = 'localhost'):
        super().__init__()

        # Set up the main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.control_panel = self._build_control_panel()
        layout.addWidget(self.control_panel)
        self.field, self.robot = self._build_field()
        layout.addWidget(self.field)

        # Set window size to 1024x768
        self.resize(1024, 800)

        # Attach to NetworkTables
        # The NT server is the `robotpy sim` process, which should be running prior to running this program
        NetworkTables.initialize(server= nt_server_ip)
        self.limelight_table = NetworkTables.getTable("limelight")
        # Read it every 30ms
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.get_robot_position_from_limelight_network_tables)
        self.timer.start(30)

        self.subscribers = []
        self.subscribe(self.robot)

    def _build_control_panel(self):
        # Create a panel for other controls
        control_panel = QWidget()
        control_panel_layout = QVBoxLayout(control_panel)

        # Display-only fields
        self.rpm_flywheel_label = QLabel("Flywheel RPM: 0")
        control_panel_layout.addWidget(self.rpm_flywheel_label)
        self.rpm_kicker_label = QLabel("Kicker Wheel RPM: 0")
        control_panel_layout.addWidget(self.rpm_kicker_label)
        self.distance_speaker_label = QLabel("Distance to Speaker: 0")
        self.distance_speaker_label.setStyleSheet("font-size: 20px; color: red;")
        control_panel_layout.addWidget(self.distance_speaker_label)
        self.angle_degrees_label = QLabel("Angle to Speaker: 0")
        control_panel_layout.addWidget(self.angle_degrees_label)

        return control_panel

    @staticmethod
    def _build_field():
        # Background SVG
        svg_widget = QSvgWidget('./field_whole.svg')
        widget_width = 800  # pixels
        field_size_x = 18  # meters
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
        # Calculate the distance to the speaker
        speaker_x = 7
        speaker_y = 2

        robot_x = self.robot.field_pos[0]
        robot_y = self.robot.field_pos[1]
        robot_rotation = self.robot.field_rotation

        distance_to_speaker = ((speaker_x - robot_x) ** 2 + (speaker_y - robot_y) ** 2) ** 0.5
        self.distance_speaker_label.setText(f"Distance to speaker: {distance_to_speaker:.1f}m")
        if distance_to_speaker < 2:
            self.distance_speaker_label.setStyleSheet("font-size: 20px; color: black; background-color: green;")
        elif distance_to_speaker < 4:
            self.distance_speaker_label.setStyleSheet("font-size: 20px; color: black; background-color: yellow;")
        else:
            self.distance_speaker_label.setStyleSheet("font-size: 20px; color: red;")

        # Calculate the angle to the speaker
        # Calculate the differences in coordinates
        delta_x = speaker_x - robot_x
        delta_y = speaker_y - robot_y

        # Calculate the angle in radians
        angle_radians = math.atan2(delta_y, delta_x)

        # Convert the angle to degrees
        angle_degrees = math.degrees(angle_radians)

        # Subtract the robot's rotation from the angle to the speaker
        angle_degrees -= robot_rotation

        # Normalize the angle to the range -180 to 180
        angle_degrees = (angle_degrees + 180) % 360 - 180

        self.angle_degrees_label.setText(f"Angle to speaker: {angle_degrees:.1f}°")
        if abs(angle_degrees) < 10:
            self.angle_degrees_label.setStyleSheet("font-size: 20px; color: black; background-color: green;")
        elif abs(angle_degrees) < 20:
            self.angle_degrees_label.setStyleSheet("font-size: 20px; color: black; background-color: yellow;")
        else:
            self.angle_degrees_label.setStyleSheet("font-size: 20px; color: red;")

    def get_robot_position_from_limelight_network_tables(self):
        botpose = self.limelight_table.getNumberArray("botpose", [0, 0, 0, 0, 0, 0])
        x, y, z, roll, pitch, yaw = botpose
        self.robot.update_position(x, y, pitch)
        self.update_robot_pos()

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        self.subscribers.remove(subscriber)

    def update(self):
        for subscriber in self.subscribers:
            subscriber.update(self)


app = QApplication(sys.argv)
window = MainWindow(nt_server_ip='localhost')
window.show()
sys.exit(app.exec_())
