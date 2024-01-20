import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QPainter, QColor, QPen

class RobotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.screen_width = 100
        self.screen_height = 100
        self.screen_pos = (10, 10)
        self.screen_angle = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black,  5, Qt.SolidLine))
        painter.setBrush(QColor(255, 0, 0, 127))
        painter.drawRect(self.screen_pos[0], self.screen_pos[1], self.screen_width, self.screen_height)

    def update_position(self, field_x, field_y):

        # TODO: Field X should be in "Field Space" (0,0) is the center of the field. Conversion to screen pos is display specific.
        screen_x = field_x - self.screen_width / 2
        screen_y = field_y - self.screen_height / 2

        self.screen_pos = (screen_x, screen_y)
        self.update()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Rectangle widget
        self.robot = RobotWidget()
        layout.addWidget(self.robot)

        # Background SVG
        self.svg_widget = QSvgWidget('path_to_your_svg.svg', self.robot)
        self.svg_widget.resize(300, 300)

        # Sliders
        self.field_x_slider = QSlider(Qt.Horizontal)
        self.field_x_slider.setMinimum(10)
        self.field_x_slider.setMaximum(300)
        self.field_x_slider.valueChanged.connect(self.update_robot_pos)
        layout.addWidget(self.field_x_slider)

        self.field_y_slider = QSlider(Qt.Horizontal)
        self.field_y_slider.setMinimum(10)
        self.field_y_slider.setMaximum(300)
        self.field_y_slider.valueChanged.connect(self.update_robot_pos)
        layout.addWidget(self.field_y_slider)

    def update_robot_pos(self):
        field_x = self.field_x_slider.value()
        field_y = self.field_y_slider.value()
        self.robot.update_position(field_x, field_y)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
