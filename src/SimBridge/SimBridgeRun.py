import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from networktables import NetworkTables
import pygame
import json
from typing import Callable
from dataclasses import dataclass
import os
from pathlib import Path
import msvcrt

@dataclass
class GameControllerState:
    a: bool
    b: bool
    x: bool
    y: bool
    dpad_down: bool
    dpad_up: bool
    dpad_left: bool
    dpad_right: bool
    bumper_l: bool
    bumper_r: bool
    stop: bool
    restart: bool
    right_y: float
    right_x: float
    left_y: float
    left_x: float
    trigger_l: float
    trigger_r: float



class SimBridge(QWidget):
    def __init__(self, game_loop_target_ms : int =20):
        super().__init__()
        self.init_ui()
        self.init_game_loop(game_loop_target_ms)
        pygame.init()

    def init_ui(self):
        self.resize(800, 600)
        self.setWindowTitle('SimBridge')

        # Top-level layout is a vertical box
        layout = QVBoxLayout()
        self.setLayout(layout)

        banner = self.init_banner()
        banner.setStyleSheet("background-color: #00fff0; ")
        layout.addWidget(banner)
        # Push content to the top
        layout.addStretch()

        # Create a form
        form = self.init_form()
        form.setStyleSheet("background-color: #fff0f0; ")
        layout.addWidget(form)
        layout.addStretch()


        self.show()

    def init_game_loop(self, target_ms : int = 20):
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.game_loop)
        self.game_timer.start(target_ms)

        self.game_loop_subscribers = []

    # Subscriber must implement on_game_loop
    def subscribe_to_game_loop(self, subscriber : object) -> None:
        self.game_loop_subscribers.append(subscriber)

    def unsubscribe_from_game_loop(self, subscriber : object) -> None:
        self.game_loop_subscribers.remove(subscriber)

    @staticmethod
    def init_banner():
        banner = QLabel("Press 'Esc' key to quit")
        banner.setAlignment(Qt.AlignCenter)  # Center horizontally
        banner.setStyleSheet("font-size: 24pt; font-weight: bold;")  # H1 style
        return banner

    def init_form(self):
        form = QWidget()
        layout = QVBoxLayout()
        form.setLayout(layout)

        # Add a label
        self.quick_label = QLabel("This is a form")
        self.quick_label.setStyleSheet("font-size: 16pt;")
        layout.addWidget(self.quick_label)
        layout.addStretch()

        return form

    def keyPressEvent(self, event : pygame.event.Event) -> None:
        if event.key() == Qt.Key_Escape:
            # Quit the application
            self.close()

    def set_quick_label(self, text : str) -> None:
        self.quick_label.setText(text)

    def game_loop(self):
        pygame.event.pump()
        for subscribers in self.game_loop_subscribers:
            subscribers.on_game_loop()


class MockLimelight:
    def __init__(self, status_callback: Callable[[str], None]) -> None:
        # The NT server is the `robotpy sim` process, which should be running prior to running this program
        NetworkTables.initialize(server='localhost')
        self.limelight_table = NetworkTables.getTable("limelight")

    # Position variables are in Field Space (origin @ field center, meters) and rotation is in degrees clockwise from the positive x-axis
    def set_robot_position(self, x : float, y : float, z : float, yaw : float, pitch : float, roll : float) -> [float]:
        botpose = [x, y, z, yaw, pitch, roll]
        self.limelight_table.putNumberArray("botpose", botpose)
        return botpose


class MyXboxController:
    JOYSTICK_DEADBAND = 0.1 # Might want to change this? Especially for the triggers
    def __init__(self, status_callback : Callable[[str], None], mock_limelight : MockLimelight) -> None:
        # Thumbsticks are said to be one joystick with 4 axes, which is a curious decision
        assert pygame.joystick.get_count() ==1
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        axes_count = self.joystick.get_numaxes()
        assert axes_count == 6

        self.limelight = mock_limelight
        self.controller_state = GameControllerState(a=False, b=False, x=False, y=False,
                                                 dpad_down=False, dpad_up=False, dpad_left=False, dpad_right=False,
                                                 bumper_l=False, bumper_r=False, stop=False, restart=False,
                                                 right_y=0.0, right_x=0.0, left_y=0.0, left_x=0.0,
                                                 trigger_l=-1.0, trigger_r=-1.0)

        self.subscribers = []

        self.status_callback = status_callback
        status_callback("Gamepad connected")

    def on_joystick_moved(self, event : pygame.event.Event) -> None:
        # Triggers are axis 5 & 6, but that should route to on_trigger_moved
        assert event.axis < 4
        # Apply deadband
        if abs(event.value) > self.JOYSTICK_DEADBAND:
            axis_names = ["LX", "LY", "RX", "RY"]
            axis_name = axis_names[event.axis]
            self.status_callback(f"Gamepad {axis_name} moved to {event.value}")
            state_for_axis = {
                "LX": self.controller_state.left_x,
                "LY": self.controller_state.left_y,
                "RX": self.controller_state.right_x,
                "RY": self.controller_state.right_y
            }
            state_for_axis[axis_name] = event.value
        else:
            # Take no action
            pass

    # Triggers are read by pygame as axis 4 and 5
    # Their value is -1 to 1, with resting position being -1 (!)
    def on_trigger_moved(self, event: pygame.event.Event) -> None:
        assert event.axis >= 4

        trigger_name = ['_','_','_','_','LT','RT']
        axis_name = trigger_name[event.axis]
        self.status_callback(f"Gamepad {trigger_name} moved to {event.value}")
        if axis_name == "LT":
            self.controller_state.trigger_l = event.value
        else:
            assert axis_name == "RT"
            self.controller_state.trigger_r = event.value


    def on_game_loop(self) -> None:
        # Handle the events (set the state)
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

        # Transmit the state to subscribers
        for subscribers in self.subscribers:
            subscribers.update(self.game_controller_state)


    def add_subscriber(self, subscriber : object) -> None:
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber : object) -> None:
        self.subscribers.remove(subscriber)

class XrcDirectoryShim:
    def __init__(self, directory: str, controller: MyXboxController, limelight : MockLimelight, gameloop_target_ms : int = 20) -> None:
        self.directory = directory
        self.controller = controller
        self.limelight = limelight

        # Set up file watching
        self.myrobot_hidden_state_fname = os.path.join(self.directory, "myRobot.txt")
        self.myrobot_control_file_fname = os.path.join(self.directory, "Controls.txt")

        # Create a QTimer to check for file changes
        self.file_check_timer = QTimer()
        self.file_check_timer.timeout.connect(self.check_for_file_changes)
        self.file_check_timer.start(gameloop_target_ms)

        self.current_control_state = GameControllerState(a=False, b=False, x=False, y=False,
                                                    dpad_down=False, dpad_up=False, dpad_left=False, dpad_right=False,
                                                    bumper_l=False, bumper_r=False, stop=False, restart=False,
                                                    right_y=0.0, right_x=0.0, left_y=0.0, left_x=0.0,
                                                    trigger_l=-1.0, trigger_r=-1.0)


    def read_game_state(self) -> None:
        load_worked = False
        try:
            f = open(self.myrobot_hidden_state_fname, "r")
            raw = f.read()
            print(f"Read {len(raw)} bytes from {self.myrobot_hidden_state_fname}")
            if len(raw) > 0:
                json_data = json.loads(raw)
                load_worked = True
            else:
                pass
        finally:
            f.close()

        if load_worked:
            robot = json_data["myrobot"]
            position_data = robot[1]["global pos"]
            rotation_data = robot[1]["global rot"]
            # TODO: I know this is almost certainly wrong in terms of ordering.
            self.limelight.set_robot_position(position_data[0], position_data[1], position_data[2], rotation_data[0], rotation_data[1], rotation_data[2])

    def write_control_state(self) -> None:
        pass

    def check_for_file_changes(self) -> None:
        self.read_game_state()
        self.write_control_state()

    def update(self, controller_state : GameControllerState) -> None:
        self.current_control_state = controller_state

def main():
    app = QApplication(sys.argv)

    # The main window is just a big rectangle
    window = SimBridge()
    mock_limelight = MockLimelight(window.set_quick_label)
    controller = MyXboxController(window.set_quick_label, mock_limelight)
    window.subscribe_to_game_loop(controller)
    window.set_quick_label("Gamepad connected")

    xrc_sim = XrcDirectoryShim("c:\\tmp\\xRCsim", controller, mock_limelight, 20)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()