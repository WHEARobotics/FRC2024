import PyQt5
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QLineF, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QWidget

class ShooterWidget(QWidget):

    def __init__(self):

        super().__init__()

        self.setFixedSize(200,200)
        self.setStyleSheet("background-color: blue;")
        self.shooter_angle = 0

    def set_shooter_angle(self, angle):
        self.shooter_angle = angle
        self.update()

    def paintEvent(self, event):
        q = QPainter(self)
        q.setPen(QPen(Qt.black, 5, Qt.SolidLine))
        q.setBrush(QColor(255, 0, 0, 127))

        angleLine = QLineF()
        angleLine.setP1(QPoint(100, 100));

        angleLine.setAngle(self.shooter_angle);
        angleLine.setLength(300);
        q.drawLine(angleLine);

        # q.drawLine(0, 0, 100, 100)
        # q.drawLine(100, 100, 200, 0)
        # q.drawLine(100, 100, 100, 200)


        q.end()