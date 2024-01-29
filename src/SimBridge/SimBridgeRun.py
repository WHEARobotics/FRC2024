import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
import ntcore
from networktables import NetworkTables
import pygame


class SimBridge(QWidget):
    def __init__(self, game_loop_target_ms=20):
        super().__init__()
        self.initUI()
        self.init_game_loop(game_loop_target_ms)
        pygame.init()

    def initUI(self):
        self.resize(800, 600)
        self.setWindowTitle('SimBridge')

        # Top-level layout is a vertical box
        layout = QVBoxLayout()
        self.setLayout(layout)

        banner = self.initBanner()
        banner.setStyleSheet("background-color: #00fff0; ")
        layout.addWidget(banner)
        # Push content to the top
        layout.addStretch()

        # Create a form
        form = self.initForm()
        form.setStyleSheet("background-color: #fff0f0; ")
        layout.addWidget(form)
        layout.addStretch()


        self.show()

    def init_game_loop(self, target_ms):
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.game_loop)
        self.game_timer.start(target_ms)

        self.game_loop_subscribers = []

    def subscribe_to_game_loop(self, subscriber):
        self.game_loop_subscribers.append(subscriber)

    def unsubscribe_from_game_loop(self, subscriber):
        self.game_loop_subscribers.remove(subscriber)

    def initBanner(self):
        banner = QLabel("Press 'Esc' key to quit")
        banner.setAlignment(Qt.AlignCenter)  # Center horizontally
        banner.setStyleSheet("font-size: 24pt; font-weight: bold;")  # H1 style
        return banner

    def initForm(self):
        form = QWidget()
        layout = QVBoxLayout()
        form.setLayout(layout)

        # Add a label
        self.quick_label = QLabel("This is a form")
        self.quick_label.setStyleSheet("font-size: 16pt;")
        layout.addWidget(self.quick_label)
        layout.addStretch()

        return form

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def set_quick_label(self, text):
        self.quick_label.setText(text)

    def game_loop(self):
        pygame.event.pump()
        for subscribers in self.game_loop_subscribers:
            subscribers.on_game_loop()


class MyXboxController:
    JOYSTICK_DEADBAND = 0.1 # Might want to change this? Especially for the triggers
    def __init__(self, status_callback, mock_limelight):
        # Thumbsticks are said to be one joystick with 4 axes, which is a curious decision
        assert pygame.joystick.get_count() ==1
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        axes_count = self.joystick.get_numaxes()
        assert axes_count == 6

        self.limelight = mock_limelight

        self.status_callback = status_callback
        status_callback("Gamepad connected")

    def on_joystick_moved(self, event):
        # Triggers are axis 5 & 6, but that should route to on_trigger_moved
        assert event.axis < 4
        # Apply deadband
        if abs(event.value) > self.JOYSTICK_DEADBAND:
            axis_names = ["LX", "LY", "RX", "RY"]
            axis_name = axis_names[event.axis]
            self.status_callback(f"Gamepad {axis_name} moved to {event.value}")
        else:
            # Take no action
            pass

    # Triggers are read by pygame as axis 4 and 5
    # Their value is -1 to 1, with resting position being -1 (!)
    def on_trigger_moved(self, event):
        assert event.axis >= 4

        trigger_name = ['_','_','_','_','LT','RT']
        axis_name = trigger_name[event.axis]
        self.status_callback(f"Gamepad {trigger_name} moved to {event.value}")

    def on_game_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                # The triggers are axis 4 and 5, and they are -1 to 1
                if event.axis == 4 or event.axis == 5:
                    self.on_trigger_moved(event)
                else:
                    self.on_joystick_moved(event)
            elif event.type == pygame.JOYBUTTONDOWN:
                self.status_callback(f"Gamepad button {event.button} pressed")
            elif event.type == pygame.JOYBUTTONUP:
                self.status_callback(f"Gamepad button {event.button} released")
            elif event.type == pygame.JOYHATMOTION:
                self.status_callback(f"Gamepad hat {event.hat} value {event.value}")
                self.limelight.set_robot_position(1, 2, 3, 4)
            elif event.type == pygame.JOYBALLMOTION:
                self.status_callback("Gamepad ball {event.ball} value {event.rel}")
            else:
                self.status_callback(f"Gamepad event {event.type}")

class MockLimelight:
    def __init__(self, status_callback):
        # The NT server is the `robotpy sim` process, which should be running prior to running this program
        NetworkTables.initialize(server='localhost')
        self.limelight_table = NetworkTables.getTable("limelight")

    def set_robot_position(self, x, y, z, rotation):
        self.limelight_table.putNumberArray("robot_position_initial", [x, y, z, rotation])
        

def main():
    app = QApplication(sys.argv)


    # The main window is just a big rectangle
    window = SimBridge()
    mock_limelight = MockLimelight(window.set_quick_label)
    controller = MyXboxController(window.set_quick_label, mock_limelight)
    window.subscribe_to_game_loop(controller)
    window.set_quick_label("Gamepad connected")

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()