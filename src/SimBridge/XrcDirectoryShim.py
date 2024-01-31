import json
import os

from PyQt5.QtCore import QTimer

from GameControllerState import GameControllerState
from MockLimelight import MockLimelight
from MyXboxController import MyXboxController


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

        controller.add_subscriber(self)


    def read_game_state(self) -> None:
        load_worked = False
        f = open(self.myrobot_hidden_state_fname, "r")
        try:
            raw = f.read()
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

            # I _think_ this is the correct ordering
            y, z, x = position_data
            pitch, yaw, roll = rotation_data

            yaw += 90
            self.limelight.set_robot_position(x, y, z, roll, yaw, pitch)

    def write_control_state(self) -> None:
        swerve_control_state = self.current_control_state.swerve_controls_to_tank_controls(self.limelight.get_botpose()[4])
        control_string = swerve_control_state.to_xrc_control_strings()
        try:
            f = open(self.myrobot_control_file_fname, "w")
            f.write(control_string)
        finally:
            f.close()

    def check_for_file_changes(self) -> None:
        self.read_game_state()
        self.write_control_state()

    def update(self, controller_state : GameControllerState) -> None:
        self.current_control_state = controller_state
