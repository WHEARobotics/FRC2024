import json
import os

from PyQt5.QtCore import QTimer

from GameControllerState import GameControllerState
from MockLimelight import MockLimelight
from MyXboxController import MyXboxController


class XrcDirectoryShim:
    """
    This class reads and writes files to simulate the robot. It's deeply tied to the xRCsim application.
    """

    def __init__(self, directory: str, limelight : MockLimelight, gameloop_target_ms : int = 20) -> None:
        """
        Initializes the class with a directory to read and write files to, and a MockLimelight object
        """

        self.directory = directory
        self.limelight = limelight

        # Set up file watching
        self.myrobot_hidden_state_fname = os.path.join(self.directory, "myRobot.txt")
        self.myrobot_control_file_fname = os.path.join(self.directory, "Controls.txt")

        # Default controller state
        self.current_control_state = GameControllerState(a=False, b=False, x=False, y=False,
                                                         dpad_down=False, dpad_up=False, dpad_left=False, dpad_right=False,
                                                         bumper_l=False, bumper_r=False, stop=False, restart=False,
                                                         right_y=0.0, right_x=0.0, left_y=0.0, left_x=0.0,
                                                         trigger_l=-1.0, trigger_r=-1.0)


    def read_game_state(self) -> None:
        """
        Reads the xRC-written game-state file (or files, if you wanted to extend this).
        Extracts the robot position and rotation (or more data, if you wanted to extend...)
        Tells the `MockLimelight` object about the robot position and rotation ("as if" it were recognizing AprilTags)
        """

        # Because the sim might be writing the file simulatneously, we have to be careful about claiming
        # that we've successfully read the data. So, first, we'll set a flag to False and only if we
        # successfully read the file contents will we set it to True.
        load_worked = False
        f = open(self.myrobot_hidden_state_fname, "r")
        try:
            raw = f.read()
            # We only want to say we loaded the data if there's, y'know, data to load
            if len(raw) > 0:
                # There's data, so try to parse it from JSON. If there's a problem (for instance,
                # if the file is being written to at the same time), this `loads` will crash and throw
                # to the `finally` block (or an `except` block if we wanted to respond to the error).
                json_data = json.loads(raw)
                # OK, so we got the file, read it, and successfully parsed it. Set the flag to True.
                load_worked = True
            else:
                # Empty file (leave the flag False)
                pass
        finally:
            # No matter what, close the file
            f.close()

        # Check the flag
        if load_worked:
            # This is from the data format written by xRCsim (see "myRobot.txt" in simulation directory)
            robot = json_data["myrobot"]
            position_data = robot[1]["global pos"]
            rotation_data = robot[1]["global rot"]

            # I _think_ this is the correct ordering
            # TODO: Triple-check this is consistent across this, MockLimelight, and FieldVizApp
            y, z, x = position_data
            pitch, yaw, roll = rotation_data

            # Set the robot position in the limelight (as if it were recognizing AprilTags)
            self.limelight.set_robot_position(x, y, z, roll, yaw, pitch)

    def write_control_state(self) -> None:
        """ Writes the game-controller state to a file, to simulate the robot's controls """

        # Convert the gamepad controls (as our swerve-drive pilot uses the controller) to the equivalent (or as close as
        # possible) tank-drive controls that are expected by xRC
        #swerve_control_state = self.current_control_state.swerve_controls_to_tank_controls(self.limelight.get_botpose()[4])
        swerve_control_state = self.current_control_state

        # Convert the controller game state into the format expected by xRCsim
        control_string = swerve_control_state.to_xrc_control_strings()

        # Write the control string to the file
        try:
            f = open(self.myrobot_control_file_fname, "w")
            f.write(control_string)
        finally:
            f.close()

    def update(self, controller_state : GameControllerState) -> None:
        """ Assigns the current game-controller state """
        self.current_control_state = controller_state

    def on_game_loop(self) -> None:
        """
        Because this class is a subscriber to the game loop, this method is called every game loop iteration.
        It reads the game state and writes the control state.
        """

        self.read_game_state()
        self.write_control_state()
