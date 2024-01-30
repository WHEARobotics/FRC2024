import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QWidget, QVBoxLayout, QRadioButton, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtSvg import QSvgWidget
from networktables import NetworkTables

from RobotWidget import RobotWidget


class MainWindow(QMainWindow):
    def __init__(self, nt_server_ip : str = 'localhost'):
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
        pass
        # field_x = self.field_x_slider.value() / 100
        # field_y = self.field_y_slider.value() / 100
        # field_rotation = self.field_rotation_slider.value()
        # self.robot.update_position(field_x, field_y, field_rotation)

    def get_robot_position_from_limelight_network_tables(self):
        botpose = self.limelight_table.getNumberArray("botpose", [0, 0, 0, 0, 0, 0])
        x, y, z, roll, pitch, yaw = botpose
        self.robot.update_position(x, y, pitch)

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
